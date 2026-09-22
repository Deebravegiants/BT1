# [M] CVE-2018-19517

## Summary
Severity: Medium
Advisory: CVE-2018-19517
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-24
Source: https://osv.dev/vulnerability/CVE-2018-19517
Type: osv

## Details
An issue was discovered in sysstat 12.1.1. The remap_struct function in sa_common.c has an out-of-bounds read during a memset call, as demonstrated by sadf.

## References
- https://github.com/sysstat/sysstat/issues/199
