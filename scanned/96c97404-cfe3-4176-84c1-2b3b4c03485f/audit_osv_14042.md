# [M] CVE-2018-6542

## Summary
Severity: Medium
Advisory: CVE-2018-6542
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-02
Source: https://osv.dev/vulnerability/CVE-2018-6542
Type: osv

## Details
In ZZIPlib 0.13.67, there is a bus error (when handling a disk64_trailer seek value) caused by loading of a misaligned address in the zzip_disk_findfirst function of zzip/mmapped.c.

## References
- https://github.com/gdraheim/zziplib/issues/17
