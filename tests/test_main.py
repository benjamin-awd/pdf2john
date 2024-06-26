import argparse
from tempfile import NamedTemporaryFile
from unittest.mock import patch

from pyhanko.pdf_utils.misc import PdfReadError
from pytest import raises

from pdf2john import PdfHashExtractor, main


def test_main_unencrypted(unencrypted_pdf_path, caplog):
    with patch(
        "argparse.ArgumentParser.parse_args",
        return_value=argparse.Namespace(pdf_files=[unencrypted_pdf_path]),
    ) as _:
        with raises(SystemExit) as e:
            main()

        assert e.value.code == -1
        assert f"{unencrypted_pdf_path} is not encrypted" in caplog.text


def test_parse_unencrypted_should_not_return_encrypt_dict(unencrypted_pdf_path):
    pdf = PdfHashExtractor(unencrypted_pdf_path)
    assert not pdf.encrypt_dict


def test_can_read_from_byte_stream():
    with open("tests/pdf/pypdf/r6-owner-password.pdf", "rb") as file:
        file_bytes = file.read()
        pdf = PdfHashExtractor(file_bytes=file_bytes)
        assert pdf.algorithm == 5
        assert pdf.length == 256
        assert pdf.permissions == -4
        assert pdf.revision == 6


def test_invalid_pdf():
    with NamedTemporaryFile(suffix="foo.pdf", delete=True) as temp_file:
        temp_file.write(b"This is an invalid PDF file")
        with raises(PdfReadError):
            PdfHashExtractor(temp_file.name)
