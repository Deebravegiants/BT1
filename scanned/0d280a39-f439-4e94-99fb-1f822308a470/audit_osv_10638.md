# [H] CVE-2017-17866

## Summary
Severity: High
Advisory: CVE-2017-17866
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17866
Type: osv

## Details
pdf/pdf-write.c in Artifex MuPDF before 1.12.0 mishandles certain length changes when a repair operation occurs during a clean operation, which allows remote attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a crafted PDF document.

## References
- https://www.debian.org/security/2018/dsa-4334
- https://bugs.ghostscript.com/show_bug.cgi?id=698699
- http://www.ghostscript.com/cgi-bin/findgit.cgi?520cc26d18c9ee245b56e9e91f9d4fcae02be5f0
