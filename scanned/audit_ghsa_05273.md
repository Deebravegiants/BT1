# [H] Docling Core: Unsafe remote filename resolution

## Summary
Severity: High
Advisory: GHSA-jmmv-h3mp-59v8
CVE: CVE-2026-44023
CWE: CWE-22, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-jmmv-h3mp-59v8
Type: github-advisory

## Affected
- PyPI: `docling-core` — affected >=1.5.0 <2.74.1

## Details
### Impact
In versions `>= 1.5.0, < 2.74.1`, `docling-core` did not sufficiently restrict remote request destinations and could resolve a server-provided `Content-Disposition` to a local path in an unsafe manner.

In applications that accept untrusted URLs, this could allow SSRF attacks targeting local files outside the user-defined cache directory.

### Patches
Patched in `docling-core` `2.74.1`.
The fix adds stricter validation for remote destinations and normalizes server-provided filenames before use.

Users should upgrade to:
- `docling-core` `>= 2.74.1`

### Workarounds
If upgrading is not immediately possible, avoid passing untrusted URLs into remote fetch functionality.

### References
- Fix release: [`v2.74.1`](https://github.com/docling-project/docling-core/releases/tag/v2.74.1)

## References
- https://github.com/docling-project/docling-core/security/advisories/GHSA-jmmv-h3mp-59v8
- https://github.com/docling-project/docling-core
- https://github.com/docling-project/docling-core/releases/tag/v2.74.1
