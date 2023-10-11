#!/usr/bin/env python

import logging
import os
import sys

from pyhanko.pdf_utils.crypt import StandardSecuritySettingsRevision
from pyhanko.pdf_utils.reader import PdfFileReader
from dataclasses import dataclass

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
    def document_id(self):
        return self.pdf.document_id[0]

    @property
    def encrypt_metadata(self):
        return str(int(self.security_handler.encrypt_metadata))

    def parse(self):
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
    def get_passwords(entries, revision):
        passwords = []

        for key, data in entries.items():
            if key in ("/O", "/U"):
                if revision >= StandardSecuritySettingsRevision.AES256.value:
                    max_length = 40

                else:
                    max_length = 32
                data = data[:max_length]

            passwords.extend([str(len(data)), data.hex()])

        return passwords


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error(f"Usage: {os.path.basename(sys.argv[0])} <PDF file(s)>")
        sys.exit(-1)

    for j in range(1, len(sys.argv)):
        filename = sys.argv[j]
        logger.info(f"Analyzing {filename}")
        extractor = PdfHashExtractor(filename)

        try:
            hash = extractor.parse()
            print(hash)
        except RuntimeError as e:
            logger.error(f"{filename} : {str(e)}")
