#!/usr/bin/env python

import logging
import os
import sys

from pyhanko.pdf_utils.crypt import SecurityHandlerVersion
from pyhanko.pdf_utils.reader import PdfFileReader

logger = logging.getLogger(__name__)


class Encryption:
    def __init__(self, pdf: PdfFileReader):
        keys = ("/O", "/U", "/OE", "/UE")
        encryption_dict = pdf._get_encryption_params()

        self.entries = {
            key: value for key in keys if (value := encryption_dict.get(key))
        }
        self.algorithm = encryption_dict.get("/V", 0)
        self.key_length = encryption_dict.get("/Length")
        self.permissions = encryption_dict["/P"]


class PdfHashExtractor:
    def __init__(self, file_name):
        self.file_name = file_name

        with open(file_name, "rb") as doc:
            pdf = PdfFileReader(doc, strict=False)
            self.permanent_document_id = pdf.document_id[0]
            self.encryption = Encryption(pdf)
            self.security_handler = pdf.security_handler
            self.encrypt_metadata = pdf.security_handler.encrypt_metadata

    def parse(self):
        passwords = self.get_passwords()

        output = (
            "$pdf$"
            + str(self.encryption.algorithm)
            + "*"
            + str(self.security_handler.version.value)
            + "*"
            + str(self.encryption.key_length)
            + "*"
        )

        output += (
            str(self.encryption.permissions)
            + "*"
            + str(int(self.encrypt_metadata))
            + "*"
        )
        output += (
            str(int(len(self.permanent_document_id) / 2))
            + "*"
            + self.permanent_document_id.hex()
            + "*"
            + passwords
        )
        logger.info("Hash: %s", output)

        return output[:-1]

    def get_passwords(self):
        output = ""
        entries = self.encryption.entries

        for key, data in entries.items():
            if key in ("/O", "/U"):
                if self.security_handler.version == SecurityHandlerVersion.AES256:
                    data = data[:40]

                # Legacy support for older PDF specifications
                if (
                    self.security_handler.version
                    <= SecurityHandlerVersion.RC4_OR_AES128
                ):
                    data = data[:32]

            output += str(int(len(data))) + "*" + data.hex() + "*"

        return output


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
