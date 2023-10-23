"""Tests to check that pdf2john.py produces valid hashes for John to use"""
from tempfile import NamedTemporaryFile

from conftest import unlock_pdf
from pyhanko.pdf_utils.misc import PdfReadError
from pytest import mark, raises

from pdf2john import PdfHashExtractor


def test_wrong_password():
    """Sanity check to confirm that John will fail if a bad password is given"""
    with raises(ValueError):
        unlock_pdf("tests/pdf/r6-test-bad-password.pdf", "asdf")


@mark.parametrize(
    ("pdf_name", "password"),
    [
        # PDFs borrowed from https://github.com/py-pdf/pypdf/tree/8a4adac/resources/encryption
        ("r2-empty-password.pdf", ""),
        ("r2-owner-password.pdf", ""),
        ("r2-user-password.pdf", "asdfzxcv"),
        ("r3-empty-password.pdf", ""),
        ("r3-user-password.pdf", "asdfzxcv"),
        ("r4-aes-user-password.pdf", "asdfzxcv"),
        ("r4-owner-password.pdf", ""),
        ("r4-user-password.pdf", "asdfzxcv"),
        ("r5-empty-password.pdf", ""),
        ("r5-user-password.pdf", "asdfzxcv"),
        ("r6-both-passwords.pdf", "foo"),
        ("r6-empty-password.pdf", ""),
        ("r6-owner-password.pdf", ""),
        ("r6-user-password.pdf", "asdfzxcv"),
    ],
)
def test_pypdf_encryption(pdf_name, password):
    result = unlock_pdf(f"tests/pdf/pypdf/{pdf_name}", password)
    if password:
        assert result == password


@mark.parametrize(
    ("pdf_name", "password"),
    [
        # PDFs borrowed from https://github.com/openwall/john-samples/tree/main/PDF
        ("r2-no-length.pdf", "hashcat"),
        ("r3-password-1.pdf", "July2099"),
        ("r3-password-2.pdf", "38r285a9"),
        ("r3-password-3.pdf", "WHATwhatWHERE?"),
        ("r3-password-4.pdf", "hashcat"),
    ],
)
def test_john_encryption(pdf_name, password):
    result = unlock_pdf(f"tests/pdf/john/{pdf_name}", password)
    if password:
        assert result == password


def test_parse_unencrypted_should_raise_error():
    with raises(RuntimeError):
        PdfHashExtractor("tests/pdf/pypdf/unencrypted.pdf")


def test_invalid_pdf():
    with NamedTemporaryFile(suffix="foo.pdf", delete=True) as temp_file:
        temp_file.write(b"This is an invalid PDF file")
        with raises(PdfReadError):
            PdfHashExtractor(temp_file.name)
