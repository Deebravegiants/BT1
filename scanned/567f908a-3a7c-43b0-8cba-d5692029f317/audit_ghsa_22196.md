# [H] Mirumee Saleor CSRF Protection Disabled

## Summary
Severity: High
Advisory: GHSA-fgjh-x3f8-8gmh
CVE: CVE-2019-13594
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fgjh-x3f8-8gmh
Type: github-advisory

## Affected
- PyPI: `saleor` — affected >=2.7.0 <2.8.0

## Details
In Mirumee Saleor 2.7.0 (fixed in 2.8.0), CSRF protection middleware was accidentally disabled, which allowed attackers to send a POST request without a valid CSRF token and be accepted by the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13594
- https://github.com/mirumee/saleor/commit/94c07034ff1bfc209461e39ca1bb6228d8ca0e35
- http://web.archive.org/web/20190713094847/https://github.com/mirumee/saleor/releases/tag/2.8.0
