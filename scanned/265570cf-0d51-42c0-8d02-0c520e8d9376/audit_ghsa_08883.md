# [M] misp-modules has nsafe remote resource fetching in expansion

## Summary
Severity: Medium
Advisory: GHSA-fhq3-2gf3-8f3j
CVE: CVE-2026-44363
CWE: CWE-295, CWE-918
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-fhq3-2gf3-8f3j
Type: github-advisory

## Affected
- PyPI: `misp-modules` — affected >=0

## Details
An unsafe remote resource fetching vulnerability existed in MISP Modules expansion modules. The html_to_markdown module accepted arbitrary HTTP(S) URLs without sufficient validation, which could allow Server-Side Request Forgery against loopback, private, or link-local network resources. Additionally, the qrcode module disabled TLS certificate verification when retrieving remote images, exposing requests to potential man-in-the-middle interception or response tampering. The issue was fixed by validating URL schemes, blocking local and private address ranges, resolving hostnames before fetching, enforcing request timeouts, and re-enabling TLS certificate verification. As reported by Bilal Teke.

## References
- https://github.com/MISP/misp-modules/security/advisories/GHSA-fhq3-2gf3-8f3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-44363
- https://github.com/MISP/misp-modules/commit/01a522f2772fc31eeed379ccf23750c8a3d401db
- https://github.com/MISP/misp-modules
