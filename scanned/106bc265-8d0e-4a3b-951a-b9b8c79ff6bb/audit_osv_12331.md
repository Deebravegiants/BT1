# [M] CVE-2018-11376

## Summary
Severity: Medium
Advisory: CVE-2018-11376
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11376
Type: osv

## Details
The r_read_le32() function in radare2 2.5.0 allows remote attackers to cause a denial of service (heap-based out-of-bounds read and application crash) via a crafted ELF file.

## References
- https://github.com/radare/radare2/issues/9904
- https://github.com/radare/radare2/commit/1f37c04f2a762500222dda2459e6a04646feeedf
