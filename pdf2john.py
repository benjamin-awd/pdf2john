#!/usr/bin/env python

import logging
import os
import sys

from pyhanko.pdf_utils.crypt import StandardSecuritySettingsRevision
from pyhanko.pdf_utils.reader import PdfFileReader

logger = logging.getLogger(__name__)


class Encryption:
    def __init__(self, pdf: PdfFileReader):
        keys = ("/U", "/O", "/UE", "/OE")
        encryption_dict = pdf._get_encryption_params()

        self.entries: dict = {
            key: value for key in keys if (value := encryption_dict.get(key))
        }
        self._algorithm: int = encryption_dict.get("/V", 0)
        self._key_length: int = encryption_dict.get("/Length")
        self._permissions: int = encryption_dict["/P"]
        self._security_handler_revision: int = encryption_dict["/R"]

    @property
    def algorithm(self) -> str:
        return str(self._algorithm)

    @property
    def key_length(self) -> str:
        return str(self._key_length)

    @property
    def permissions(self) -> str:
        return str(self._permissions)

    @property
    def security_handler_revision(self) -> str:
        return str(self._security_handler_revision)


class PdfHashExtractor:
    def __init__(self, file_name):
        self.file_name = file_name

        with open(file_name, "rb") as doc:
            self.pdf = PdfFileReader(doc, strict=False)
            self.encryption = Encryption(self.pdf)
            self.security_handler = self.pdf.security_handler

    @property
    def document_id(self):
        return self.pdf.document_id[0]

    @property
    def encrypt_metadata(self):
        return str(int(self.security_handler.encrypt_metadata))

    def parse(self):
        passwords = self.get_passwords()

        encryption_info = (
            "$pdf$"
            + self.encryption.algorithm
            + "*"
            + self.encryption.security_handler_revision
            + "*"
            + self.encryption.key_length
        )

        permissions_info = self.encryption.permissions + "*" + self.encrypt_metadata

        id_info = str(len(self.document_id)) + "*" + self.document_id.hex()

        output = (
            encryption_info + "*" + permissions_info + "*" + id_info + "*" + passwords
        )
        logger.info("Hash: %s", output)

        return output

    def get_passwords(self):
        passwords = []
        entries = self.encryption.entries

        for key, data in entries.items():
            if key in ("/O", "/U"):
                if int(revision) >= StandardSecuritySettingsRevision.AES256.value:
                    max_length = 40

                else:
                    max_length = 32
                data = data[:max_length]

            passwords.extend([str(len(data)), data.hex()])

        return "*".join(passwords)


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
