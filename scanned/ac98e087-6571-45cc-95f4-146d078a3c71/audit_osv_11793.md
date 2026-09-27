# [M] CVE-2017-9761

## Summary
Severity: Medium
Advisory: CVE-2017-9761
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-9761
Type: osv

## Details
The find_eoq function in libr/core/cmd.c in radare2 1.5.0 allows remote attackers to cause a denial of service (heap-based out-of-bounds read and application crash) via a crafted binary file.

## References
- http://www.securityfocus.com/bid/99138
- https://github.com/radare/radare2/commit/00e8f205475332d7842d0f0d1481eeab4e83017c
- https://github.com/radare/radare2/issues/7727
