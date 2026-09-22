# [M] CVE-2018-14016

## Summary
Severity: Medium
Advisory: CVE-2018-14016
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-12
Source: https://osv.dev/vulnerability/CVE-2018-14016
Type: osv

## Details
The r_bin_mdmp_init_directory_entry function in mdmp.c in radare2 2.7.0 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted Mini Crash Dump file.

## References
- https://github.com/radareorg/radare2/commit/eb7deb281df54771fb8ecf5890dc325a7d22d3e2
- https://github.com/radare/radare2/issues/10464
