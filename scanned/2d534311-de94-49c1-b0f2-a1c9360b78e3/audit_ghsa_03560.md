# [M] Regular Expression Denial of Service (ReDoS) in Pillow

## Summary
Severity: Medium
Advisory: GHSA-9hx2-hgq2-2g4f
CVE: CVE-2021-25292
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-9hx2-hgq2-2g4f
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=5.1.0 <8.1.1

## Details
An issue was discovered in Pillow before 8.1.1. The PDF parser allows a regular expression DoS (ReDoS) attack via a crafted PDF file because of a catastrophic backtracking regex.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25292
- https://github.com/python-pillow/Pillow/commit/3bce145966374dd39ce58a6fc0083f8d1890719c
- https://github.com/python-pillow/Pillow/commit/521dab94c7ab72b037bd9a83e9663401e0fd2cee
- https://github.com/python-pillow/Pillow/commit/6207b44ab1ff4a91d8ddc7579619876d0bb191a4
- https://github.com/advisories/GHSA-9hx2-hgq2-2g4f
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2021-38.yaml
- https://github.com/python-pillow/Pillow
- https://pillow.readthedocs.io/en/stable/releasenotes/8.1.1.html
- https://security.gentoo.org/glsa/202107-33
