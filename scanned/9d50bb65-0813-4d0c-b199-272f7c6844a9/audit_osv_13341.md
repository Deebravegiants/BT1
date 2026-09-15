# [H] CVE-2018-19416

## Summary
Severity: High
Advisory: CVE-2018-19416
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-11-21
Source: https://osv.dev/vulnerability/CVE-2018-19416
Type: osv

## Details
An issue was discovered in sysstat 12.1.1. The remap_struct function in sa_common.c has an out-of-bounds read during a memmove call, as demonstrated by sadf.

## References
- http://www.securityfocus.com/bid/106010
- https://github.com/sysstat/sysstat/issues/196
