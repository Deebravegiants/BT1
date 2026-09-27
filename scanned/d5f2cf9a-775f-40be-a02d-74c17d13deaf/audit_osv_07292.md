# [C] BIT-pillow-2021-25289

## Summary
Severity: Critical
Advisory: BIT-pillow-2021-25289
Aliases: CVE-2021-25289, GHSA-57h3-9rgr-c24m, PYSEC-2021-35
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-pillow-2021-25289
Type: osv

## Affected
- Bitnami: `pillow` — affected >=0 <8.1.1

## Details
An issue was discovered in Pillow before 8.1.1. TiffDecode has a heap-based buffer overflow when decoding crafted YCbCr files because of certain interpretation conflicts with LibTIFF in RGBA mode. NOTE: this issue exists because of an incomplete fix for CVE-2020-35654.

## References
- https://pillow.readthedocs.io/en/stable/releasenotes/8.1.1.html
- https://security.gentoo.org/glsa/202107-33
- https://nvd.nist.gov/vuln/detail/CVE-2021-25289
