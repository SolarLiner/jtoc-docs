import os
from shutil import which
from pathlib import Path
import shlex
from typing import Callable


def exec(command: str, *args: str, check=True, shell=True) -> int:
    import subprocess

    cmd_str = shlex.join([command, *args])
    print(cmd_str)
    child_process = subprocess.Popen(cmd_str, shell=shell, encoding="utf-8")
    retcode = child_process.wait()
    if check:
        assert retcode == 0, "Child process did not exit successfully: " + cmd_str
    return retcode


def compile(input: Path, format="pdf", typst: str | None = None) -> None:
    if not typst:
        typst = which("typst")
    assert typst is not None, f"typst required to generate {format} files"

    src_dir = Path("src").absolute()
    main_file = src_dir / "main.typ"
    output = Path("out") / str(input.relative_to(src_dir)).replace(os.path.sep, " ")
    output = output.with_suffix(f".{format}")
    input = input.relative_to(src_dir)
    print("Compiling", str(input), "->", str(output))
    output.parent.mkdir(parents=True, exist_ok=True)
    _ = exec("typst", "compile",
             "--root", ".",
             "--font-path", "assets/fonts",
             "-f", format,
             "--input", f"file={input}",
             str(main_file),
             str(output))


if __name__ == "__main__":
    from functools import partial, wraps
    from multiprocessing import cpu_count
    from threading import Semaphore, Thread

    sem = Semaphore(cpu_count())
    def sync(f: Callable[[], None]):
        @wraps(f)
        def wrapper():
            with sem:
                f()
        return wrapper

    def mkthread(f: Callable[[], None]):
        t = Thread(target=f)
        t.start()
        return t

    threads = [mkthread(sync(partial(compile, input))) for input in Path.cwd().joinpath("src").glob("**/*.md")]
    for t in threads:
        t.join()
