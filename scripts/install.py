#!/usr/bin/env python3
import os
import subprocess
from pathlib import PosixPath


def main():
    release_version = "3.7.3"

    package_path = PosixPath("/workspace/monitoring_prometheus")
    package_path.mkdir()
    (package_path / "__init__.py").open("w").close()

    bin_path = PosixPath("/workspace/bin")
    bin_path.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "curl",
            "--silent",
            "--show-error",
            "--fail",
            "-L",
            "-o",
            f"/tmp/prometheus-{release_version}.linux-amd64.tar.gz",
            f"https://github.com/prometheus/prometheus/releases/download/v{release_version}/"
            f"prometheus-{release_version}.linux-amd64.tar.gz",
        ],
        check=True,
    )
    subprocess.run(
        [
            "tar",
            "-C",
            bin_path.as_posix(),
            "-xf",
            f"/tmp/prometheus-{release_version}.linux-amd64.tar.gz",
            "--strip-components=1",
            f"prometheus-{release_version}.linux-amd64/prometheus",
            f"prometheus-{release_version}.linux-amd64/promtool",
        ],
        check=True,
    )
    os.remove(f"/tmp/prometheus-{release_version}.linux-amd64.tar.gz")


if __name__ == "__main__":
    main()
