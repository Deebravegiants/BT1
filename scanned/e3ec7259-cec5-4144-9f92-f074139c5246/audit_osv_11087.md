# [M] CVE-2017-5978

## Summary
Severity: Medium
Advisory: CVE-2017-5978
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-5978
Type: osv

## Details
The zzip_mem_entry_new function in memdisk.c in zziplib 0.13.62 allows remote attackers to cause a denial of service (out-of-bounds read and crash) via a crafted ZIP file.

## References
- http://www.securityfocus.com/bid/96268
- http://www.debian.org/security/2017/dsa-3878
- https://blogs.gentoo.org/ago/2017/02/09/zziplib-out-of-bounds-read-in-zzip_mem_entry_new-memdisk-c/
