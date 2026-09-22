# [H] BIT-pillow-2021-25291

## Summary
Severity: High
Advisory: BIT-pillow-2021-25291
Aliases: CVE-2021-25291, GHSA-mvg9-xffr-p774, PYSEC-2021-37
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-pillow-2021-25291
Type: osv

## Affected
- Bitnami: `pillow` — affected >=0 <8.1.1

## Details
An issue was discovered in Pillow before 8.1.1. In TiffDecode.c, there is an out-of-bounds read in TiffreadRGBATile via invalid tile boundaries.

## References
- https://pillow.readthedocs.io/en/stable/releasenotes/8.1.1.html
- https://security.gentoo.org/glsa/202107-33
- https://nvd.nist.gov/vuln/detail/CVE-2021-25291
