import subprocess

from pytest import mark


def run_cli(args: list, cmd: str = "pdf2john", input_text=None):
    process = subprocess.Popen(
        [cmd] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate(input_text)
    return process, stdout, stderr


@mark.parametrize("cmd", ["pdf2john", "./src/pdf2john/pdf2john.py"])
def test_cli_extraction(cmd):
    pdf_file = "tests/pdf/r6-test-bad-password.pdf"
    process, stdout, _ = run_cli(cmd=cmd, args=[pdf_file])

    expected = "$pdf$5*6*256*-4*1*16*fce2fe96b7e142b4a0576f61e2e9c441*48*aef6c4bf5e8a0f3bb1adef2b8ac2367d1ce95ecc1ddc3243ce49786086a023aa310aa9f7d1d103f837e4d4f738ac913d*48*eabf37f3f1f1b208f7c8ddfad3b817c689889ecbadd30f4581382cfbf79806304fb438e9ca227a023138a38eadcf82f3*32*37afcbfcbb32d4e1bca1eb10165693a1633ebb742c00045177a284ba22196937*32*3459a644d5f4c4f7cee562b754b30df48d598e1911ea513ef29bb3928593caf3"
    assert process.returncode == 0
    assert stdout == expected + "\n"


def test_handle_multiple_files():
    pdf_files = [
        "tests/pdf/r6-test-bad-password.pdf",
        "tests/pdf/pypdf/r6-user-password.pdf",
    ]
    process, stdout, _ = run_cli(pdf_files)

    expected = [
        "$pdf$5*6*256*-4*1*16*fce2fe96b7e142b4a0576f61e2e9c441*48*aef6c4bf5e8a0f3bb1adef2b8ac2367d1ce95ecc1ddc3243ce49786086a023aa310aa9f7d1d103f837e4d4f738ac913d*48*eabf37f3f1f1b208f7c8ddfad3b817c689889ecbadd30f4581382cfbf79806304fb438e9ca227a023138a38eadcf82f3*32*37afcbfcbb32d4e1bca1eb10165693a1633ebb742c00045177a284ba22196937*32*3459a644d5f4c4f7cee562b754b30df48d598e1911ea513ef29bb3928593caf3",
        "$pdf$5*6*256*-4*1*16*fce2fe96b7e142b4a0576f61e2e9c441*48*ae700c793d687882958ce411fed797a6364e182dc4cb8c3819d347b9d577c3526d9fd5c2b9fe54cfed6539accc53ac28*48*57c08f4d2b7e02a2eb6deabf903267643bd971f5201ed5e1865311001c05d012e7a9dea18e3de1aa35675d0069944da1*32*ec81dd84bd5492acdcd5f82cd3093427d2db0eace3789f0f39c65ebea10253dd*32*557c4e6be3cc2bd0166a1b1ab3b0e09d6f0e3f5d17d305925c7055116ac14c6c",
    ]
    assert process.returncode == 0
    assert stdout.split("\n")[:2] == expected


def test_cli_debug():
    pdf_file = "tests/pdf/r6-test-bad-password.pdf"
    process, stdout, _ = run_cli([pdf_file, "--debug"])
    assert process.returncode == 0

    with open("tests/debug_output.txt", "r") as file:
        lines = file.readlines()
        assert stdout == "".join(lines)
