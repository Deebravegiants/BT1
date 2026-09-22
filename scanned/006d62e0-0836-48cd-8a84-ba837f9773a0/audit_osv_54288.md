# [H] CVE-2023-46751

## Summary
Severity: High
Advisory: CVE-2023-46751
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-06
Source: https://osv.dev/vulnerability/CVE-2023-46751
Type: osv

## Details
An issue was discovered in the function gdev_prn_open_printer_seekable() in Artifex Ghostscript through 10.02.0 allows remote attackers to crash the application via a dangling pointer.

## References
- https://ghostscript.com/
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=dcdbc595c13c9d11d235702dff46bb74c80f7698
- https://www.debian.org/security/2023/dsa-5578
- https://bugs.ghostscript.com/show_bug.cgi?id=707264
