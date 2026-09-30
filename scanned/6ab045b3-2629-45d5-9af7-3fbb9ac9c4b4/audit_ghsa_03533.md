# [H] Out-of-bounds Write in Pillow

## Summary
Severity: High
Advisory: GHSA-8xjq-8fcg-g5hw
CVE: CVE-2021-25290
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-8xjq-8fcg-g5hw
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <8.1.1

## Details
An issue was discovered in Pillow before 8.1.1. In TiffDecode.c, there is a negative-offset memcpy with an invalid size.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25290
- https://github.com/python-pillow/Pillow/commit/86f02f7c70862a0954bfe8133736d352db978eaa
- https://github.com/python-pillow/Pillow/commit/e25be1e33dc526bfd1094bc778a54d8e29bf66c9
- https://github.com/advisories/GHSA-8xjq-8fcg-g5hw
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2021-36.yaml
- https://github.com/python-pillow/Pillow
- https://lists.debian.org/debian-lts-announce/2021/07/msg00018.html
- https://pillow.readthedocs.io/en/stable/releasenotes/8.1.1.html
- https://security.gentoo.org/glsa/202107-33
