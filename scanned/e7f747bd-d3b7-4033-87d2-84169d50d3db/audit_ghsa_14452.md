# [M] Saleor has Staff-Authenticated Error Message Information Disclosure Vulnerability via Python Exceptions

## Summary
Severity: Medium
Advisory: GHSA-r8qr-wwg3-2r85
CVE: CVE-2023-26051
CWE: CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-r8qr-wwg3-2r85
Type: github-advisory

## Affected
- PyPI: `Saleor` — affected >=2.0.0 <3.1.48
- PyPI: `Saleor` — affected >=3.11.0 <3.11.12
- PyPI: `Saleor` — affected >=3.10.0 <3.10.14
- PyPI: `Saleor` — affected >=3.9.0 <3.9.27
- PyPI: `Saleor` — affected >=3.8.0 <3.8.30
- PyPI: `Saleor` — affected >=3.7.0 <3.7.59
- PyPI: `saleor` — affected >=2.0.0 <3.1.48
- PyPI: `saleor` — affected >=3.7.0 <3.7.59
- PyPI: `saleor` — affected >=3.8.0 <3.8.30
- PyPI: `saleor` — affected >=3.9.0 <3.9.27
- PyPI: `saleor` — affected >=3.10.0 <3.10.14
- PyPI: `saleor` — affected >=3.11.0 <3.11.12

## Details
### Impact
Some internal Python exceptions are not handled properly and thus are returned in API as error messages. Some messages might contain sensitive information like user email address in staff-authenticated requests.

This issue has been patched in versions 3.1.48, 3.7.59, 3.8.30, 3.9.27, 3.10.14 and 3.11.12.

### Workarounds
None

### For more information
If you have any questions or comments about this advisory:
* Open a discussion at https://github.com/saleor/saleor/discussions
* Email us at [hello@saleor.io](mailto:hello@saleor.io)

## References
- https://github.com/saleor/saleor/security/advisories/GHSA-r8qr-wwg3-2r85
- https://nvd.nist.gov/vuln/detail/CVE-2023-26051
- https://github.com/saleor/saleor/commit/31bce881ccccf0d79a9b14ecb6ca3138d1edeec1
- https://github.com/pypa/advisory-database/tree/main/vulns/saleor/PYSEC-2026-917.yaml
- https://github.com/saleor/saleor
- https://github.com/saleor/saleor/releases/tag/3.1.48
- https://github.com/saleor/saleor/releases/tag/3.10.14
- https://github.com/saleor/saleor/releases/tag/3.11.12
- https://github.com/saleor/saleor/releases/tag/3.7.59
- https://github.com/saleor/saleor/releases/tag/3.8.30
- https://github.com/saleor/saleor/releases/tag/3.9.27
