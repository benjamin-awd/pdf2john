from conftest import unlock_pdf
from pytest import raises, mark


def test_wrong_password():
    """Sanity check to confirm that John will fail if a bad password is given"""
    with raises(ValueError):
        unlock_pdf("tests/pdf/r6-test-bad-password.pdf", "asdf")


@mark.parametrize(
    ("pdf_name"),
    [
        # PDFs borrowed from https://github.com/py-pdf/pypdf/tree/8a4adac/resources/encryption
        ("r2-user-password.pdf"),
        ("r3-user-password.pdf"),
        ("r4-user-password.pdf"),
        ("r4-aes-user-password.pdf"),
        ("r5-user-password.pdf"),
        ("r6-user-password.pdf"),
    ],
)
def test_encryption(pdf_name):
    password = unlock_pdf(f"tests/pdf/{pdf_name}", "asdfzxcv")
    assert password == "asdfzxcv"
