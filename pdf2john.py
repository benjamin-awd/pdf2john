#!/usr/bin/env python

import logging
import os
import sys
from dataclasses import dataclass

from pyhanko.pdf_utils.reader import PdfFileReader

logger = logging.getLogger(__name__)


class EncryptionDictionary:
    def __init__(self, pdf: PdfFileReader):
        keys = ("/U", "/O", "/UE", "/OE")
        encryption_dict = pdf._get_encryption_params()

        self.entries: dict = {
            key: value for key in keys if (value := encryption_dict.get(key))
        }
        self.algorithm: int = encryption_dict.get("/V", 0)
        self.key_length: int = encryption_dict.get("/Length")
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

    def parse(self) -> str:
        passwords = self.get_passwords(
            self.encryption.entries, self.encryption.revision
        )

        generator = HashGenerator(
            algorithm=self.encryption.algorithm,
            revision=self.encryption.revision,
            key_length=self.encryption.key_length,
            permissions=self.encryption.permissions,
            encrypt_metadata=self.encrypt_metadata,
            document_id_length=len(self.document_id),
            document_id=self.document_id.hex(),
            passwords=passwords,
        )

        return generator.hash

    @staticmethod
    def get_passwords(entries: dict, revision: int):
        passwords = []

        for key, data in entries.items():
            if key in ("/O", "/U"):
                if revision >= 5:
                    max_length = 48

                else:
                    max_length = 32
                data = data[:max_length]

            passwords.extend([str(len(data)), data.hex()])

        return passwords


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: %s <PDF file(s)>", {os.path.basename(sys.argv[0])})
        sys.exit(-1)

    for filename in sys.argv[1:]:
        extractor = PdfHashExtractor(filename)

        try:
            pdf_hash = extractor.parse()
            print(pdf_hash)
        except RuntimeError as error:
            logger.error("%s : %s", filename, error)
