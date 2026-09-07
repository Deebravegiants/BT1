# [H] Docling Core: Insufficient validation of image reference URIs

## Summary
Severity: High
Advisory: GHSA-j5xp-7m2f-49jv
CVE: CVE-2026-44019
CWE: CWE-400, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-j5xp-7m2f-49jv
Type: github-advisory

## Affected
- PyPI: `docling-core` — affected >=2.5.0 <2.74.1

## Details
### Impact
In versions `>= 2.5.0, < 2.74.1`, `docling-core`  could allow local `file://` image references and accepted inline `data:` content without a decoded-size limit.

In applications that accept untrusted image references, this may allow access to local files readable by the process or excessive memory use from large inline payloads.

### Patches
Patched in `docling-core` `2.74.1`.
The fix blocks local file URIs by default and adds a size limit for decoded inline image data.

Users should upgrade to:
- `docling-core` `>= 2.74.1`

### Workarounds
If upgrading is not immediately possible:
- reject `file:` and `data:` image references from untrusted input
- allow only approved local or remote image sources
- apply input size and memory limits to processing workers

### References
- Fix release: [`v2.74.1`](https://github.com/docling-project/docling-core/releases/tag/v2.74.1)

## References
- https://github.com/docling-project/docling-core/security/advisories/GHSA-j5xp-7m2f-49jv
- https://github.com/docling-project/docling-core
- https://github.com/docling-project/docling-core/releases/tag/v2.74.1
