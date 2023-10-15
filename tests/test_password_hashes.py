from conftest import unlock_pdf
from pytest import mark, raises


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
def test_encryption(pdf_name, password):
    unlock_pdf(f"tests/pdf/{pdf_name}", password)
