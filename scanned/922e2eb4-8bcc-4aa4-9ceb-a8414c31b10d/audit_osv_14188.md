# [M] CVE-2018-7727

## Summary
Severity: Medium
Advisory: CVE-2018-7727
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-06
Source: https://osv.dev/vulnerability/CVE-2018-7727
Type: osv

## Details
An issue was discovered in ZZIPlib 0.13.68. There is a memory leak triggered in the function zzip_mem_disk_new in memdisk.c, which will lead to a denial of service attack.

## References
- https://access.redhat.com/errata/RHSA-2018:3229
- https://github.com/gdraheim/zziplib/issues/40
