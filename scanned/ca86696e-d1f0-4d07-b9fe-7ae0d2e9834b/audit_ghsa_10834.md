# [H] pyLoad has an Arbitrary File Write via Path Traversal in edit_package()

## Summary
Severity: High
Advisory: GHSA-6px9-j4qr-xfjw
CVE: CVE-2026-29778
CWE: CWE-23
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-6px9-j4qr-xfjw
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0.5.0b3.dev13 <0.5.0b3.dev97

## Details
The edit_package() function implements insufficient sanitization for the pack_folder parameter. The current protection relies on a single-pass string replacement of "../", which can be bypassed using crafted recursive traversal sequences.

Exploitation

An authenticated user with MODIFY permission can bypass the sanitization by submitting a payload such as:
`pack_folder=..././..././..././tmp`

After the single-pass replacement, this becomes:
`../../../tmp`

Because the traversal sequences are not properly validated, the resulting normalized path escapes the intended storage directory and writes files to /tmp or other locations.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-6px9-j4qr-xfjw
- https://nvd.nist.gov/vuln/detail/CVE-2026-29778
- https://github.com/pyload/pyload
- https://github.com/pypa/advisory-database/tree/main/vulns/pyload-ng/PYSEC-2026-121.yaml
