# [M] CVE-2017-5977

## Summary
Severity: Medium
Advisory: CVE-2017-5977
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-5977
Type: osv

## Details
The zzip_mem_entry_extra_block function in memdisk.c in zziplib 0.13.62 allows remote attackers to cause a denial of service (invalid memory read and crash) via a crafted ZIP file.

## References
- http://www.securityfocus.com/bid/96268
- http://www.openwall.com/lists/oss-security/2017/02/14/3
- https://blogs.gentoo.org/ago/2017/02/09/zziplib-invalid-memory-read-in-zzip_mem_entry_extra_block-memdisk-c/
