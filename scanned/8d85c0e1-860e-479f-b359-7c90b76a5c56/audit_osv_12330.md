# [M] CVE-2018-11375

## Summary
Severity: Medium
Advisory: CVE-2018-11375
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11375
Type: osv

## Details
The _inst__lds() function in radare2 2.5.0 allows remote attackers to cause a denial of service (heap-based out-of-bounds read and application crash) via a crafted binary file.

## References
- https://github.com/radare/radare2/issues/9928
- https://github.com/radare/radare2/commit/041e53cab7ca33481ae45ecd65ad596976d78e68
