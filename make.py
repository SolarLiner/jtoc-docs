from collections.abc import Iterable
import os
from shutil import which
from pathlib import Path
import shlex
from typing import Callable


FILE = Path(__file__)
ROOT_DIR = FILE.parent
SRC_DIR = ROOT_DIR / "src"
OUT_DIR = ROOT_DIR / "out"


async def exec(command: str, *args: str, check=True, shell=True) -> int:
    from asyncio import subprocess

    cmd = shlex.join([command, *args])
    proc = await subprocess.create_subprocess_shell(cmd)
    retcode = await proc.wait()
    if check:
        assert retcode == 0, f"Process returned non-zero exit code: {cmd}"
    return retcode


async def compile(input: Path, format="pdf", typst: str | None = None, command="compile") -> None:
    if not typst:
        typst = which("typst")
    assert typst is not None, f"typst required to generate {format} files"

    def output_path(path: Path) -> Path:
        out = OUT_DIR / str(path).replace(os.path.sep, " ")
        return out.with_suffix(f".{format}")

    input = input.relative_to(SRC_DIR)
    output = output_path(input)
    print("Compiling", str(input), "->", str(output))
    output.parent.mkdir(parents=True, exist_ok=True)

    if format == "html":
        features_args = ["--features", "html"]
    else:
        features_args = []

    match input.suffix:
        case ".md":
            main_file = SRC_DIR / "main.typ"
            io_args = ["--input", f"file={input}", str(main_file), str(output)]
        case ".typ":
            io_args = [str(input), str(output_path(input))]
        case suffix:
            raise AssertionError(f"{suffix!r} input format not supported")

    _ = await exec("typst", command,
             *features_args,
             "--root", ".",
             "--font-path", "assets/fonts",
             "-f", format,
             *io_args)


def markdown_files() -> Iterable[Path]:
    return SRC_DIR.glob("**/*.md")


async def md2pdf(inputs: Iterable[Path], command = "compile"):
    import asyncio

    futures = [compile(input, format="pdf", command=command) for input in inputs]
    _ = await asyncio.gather(*futures)


if __name__ == "__main__":
    import asyncio
    from argparse import ArgumentParser
    import sys

    p = ArgumentParser()
    p.add_argument("-w", "--watch", action="store_true", default=False)

    args = p.parse_args()
    if args.watch:
        command = "watch"
    else:
        command = "compile"

    try:
        asyncio.run(md2pdf(markdown_files(), command=command))
    except Exception as ex:
        print(ex, file=sys.stderr)
