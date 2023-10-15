#!/usr/bin/env python

import logging
import os
import sys
from dataclasses import dataclass
from enum import Enum

from pyhanko.pdf_utils.crypt import SecurityHandlerVersion
from pyhanko.pdf_utils.reader import PdfFileReader

logger = logging.getLogger(__name__)


class SecurityRevision(Enum):
    RC4_BASIC = (2, 32)
    RC4_EXTENDED = (3, 32)
    RC4_OR_AES128 = (4, 32)
    AES_256_R5 = (5, 48)
    AES256 = (6, 48)

    @property
    def revision(self):
        return self.value[0]

    @property
    def key_length(self):
        return self.value[1]

    @classmethod
    def get_key_length(cls, revision):
        for item in cls:
            if item.revision == revision:
                return item.key_length
        logger.warning(
            "No explicit key length for revision %s, using default length of 48",
            revision,
        )
        return 48


class Entries(Enum):
    U = "udata"
    O = "odata"
    OE = "oeseed"
    UE = "ueseed"


class EncryptionDictionary:
    def __init__(self, pdf: PdfFileReader):
        encryption_dict = pdf._get_encryption_params()

        if not encryption_dict:
            raise RuntimeError("File not encrypted")

        self.algorithm: int = encryption_dict.get(
            "/V", SecurityHandlerVersion.RC4_40.value
        )
        self.key_length: int = encryption_dict.get("/Length", 40)
        self.permissions: int = encryption_dict["/P"]
        self.revision: int = encryption_dict["/R"]


@dataclass(kw_only=True)
class HashGenerator:
    algorithm: int
    revision: int
    key_length: int
    permissions: int
    encrypt_metadata: bool
    document_id_length: int
    document_id: str
    passwords: list

    def __post_init__(self):
        self.passwords = "*".join(self.passwords)
        self.hash = "$pdf$" + "*".join([str(value) for value in self.__dict__.values()])


class PdfHashExtractor:
    def __init__(self, file_name):
        self.file_name = file_name

        with open(file_name, "rb") as doc:
            self.pdf = PdfFileReader(doc, strict=False)
            self.encryption = EncryptionDictionary(self.pdf)
            self.security_handler = self.pdf.security_handler

    @property
    def document_id(self) -> bytes:
        return self.pdf.document_id[0]

    @property
    def encrypt_metadata(self) -> str:
        return str(int(self.security_handler.encrypt_metadata))

    @property
    def entries(self) -> dict:
        return {
            enum.name: getattr(self.security_handler, enum.value) for enum in Entries
        }

    def parse(self) -> str:
        passwords = self.get_passwords(self.entries, self.encryption.revision)

        generator = HashGenerator(
            **vars(self.encryption),
            encrypt_metadata=self.encrypt_metadata,
            document_id_length=len(self.document_id),
            document_id=self.document_id.hex(),
            passwords=passwords,
        )

        return generator.hash

    @staticmethod
    def get_passwords(entries: dict[str, bytes], revision: int):
        passwords = []

        for key, data in entries.items():
            if data and key in list(Entries.__members__):
                max_length = SecurityRevision.get_key_length(revision)
                data = data[:max_length]
                passwords.extend([str(len(data)), data.hex()])

        return passwords


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: %s <PDF file(s)>", os.path.basename(__file__))
        sys.exit(-1)

    for filename in sys.argv[1:]:
        extractor = PdfHashExtractor(filename)

        try:
            pdf_hash = extractor.parse()
            print(pdf_hash)
        except RuntimeError as error:
            logger.error("%s : %s", filename, error)
