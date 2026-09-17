# [H] Mako: Path traversal via double-slash URI prefix in TemplateLookup

## Summary
Severity: High
Advisory: GHSA-v92g-xgxw-vvmm
CVE: CVE-2026-41205
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-v92g-xgxw-vvmm
Type: github-advisory

## Affected
- PyPI: `Mako` — affected >=0 <1.3.11

## Details
### Summary

`TemplateLookup.get_template()` is vulnerable to path traversal when a URI starts with `//` (e.g., `//../../../secret.txt`). The root cause is an inconsistency between two slash-stripping implementations:

- `Template.__init__` strips **one** leading `/` using `if`/slice
- `TemplateLookup.get_template()` strips **all** leading `/` using `re.sub(r"^\/+", "")`

When a URI like `//../../../../etc/passwd` is passed:
1. `get_template()` strips all `/` → `../../../../etc/passwd` → file found via `posixpath.join(dir_, u)`
2. `Template.__init__` strips one `/` → `/../../../../etc/passwd` → `normpath` → `/etc/passwd`
3. `/etc/passwd`.startswith(`..`) → `False` → **check bypassed**

### Impact

Arbitrary file read: any file readable by the process can be returned as rendered template content when an application passes untrusted input directly to `TemplateLookup.get_template()`.

Note: this is exploitable at the library API level. HTTP-based exploitation is mitigated by Python's `BaseHTTPRequestHandler` which normalizes double-slash prefixes since CPython gh-87389. Applications using other HTTP servers that do not normalize paths may be affected.

### Fix

Changed `Template.__init__` to use `lstrip("/")` instead of stripping only a single leading slash, so both code paths handle leading slashes consistently.

## References
- https://github.com/sqlalchemy/mako/security/advisories/GHSA-v92g-xgxw-vvmm
- https://nvd.nist.gov/vuln/detail/CVE-2026-41205
- https://github.com/sqlalchemy/mako/commit/e05ac61989a7fb9dd7dcde6cfd72dc48328719a3
- https://github.com/pypa/advisory-database/tree/main/vulns/mako/PYSEC-2026-88.yaml
- https://github.com/sqlalchemy/mako
- https://github.com/sqlalchemy/mako/releases/tag/rel_1_3_11
