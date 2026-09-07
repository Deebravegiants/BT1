# [H] Pillow Buffer overflow in ImagingFliDecode

## Summary
Severity: High
Advisory: GHSA-8xjv-v9xq-m5h9
CVE: CVE-2016-0775
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-8xjv-v9xq-m5h9
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <3.1.1

## Details
Buffer overflow in the `ImagingFliDecode` function in `libImaging/FliDecode.c` in Pillow before 3.1.1 allows remote attackers to cause a denial of service (crash) via a crafted FLI file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0775
- https://github.com/python-pillow/Pillow/commit/893a40850c2d5da41537958e40569c029a6e127b
- https://github.com/advisories/GHSA-8xjv-v9xq-m5h9
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2016-6.yaml
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/blob/c3cb690fed5d4bf0c45576759de55d054916c165/CHANGES.rst
- https://security.gentoo.org/glsa/201612-52
- http://www.debian.org/security/2016/dsa-3499
