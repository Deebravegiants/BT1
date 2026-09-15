# [M] CVE-2017-5980

## Summary
Severity: Medium
Advisory: CVE-2017-5980
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-5980
Type: osv

## Details
The zzip_mem_entry_new function in memdisk.c in zziplib 0.13.62 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a crafted ZIP file.

## References
- http://www.securityfocus.com/bid/96268
- http://www.debian.org/security/2017/dsa-3878
- https://blogs.gentoo.org/ago/2017/02/09/zziplib-null-pointer-dereference-in-zzip_mem_entry_new-memdisk-c/
