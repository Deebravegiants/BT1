# [M] CVE-2017-7716

## Summary
Severity: Medium
Advisory: CVE-2017-7716
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2017-7716
Type: osv

## Details
The read_u32_leb128 function in libr/util/uleb128.c in radare2 1.3.0 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted Web Assembly file.

## References
- https://github.com/radare/radare2/issues/7260
