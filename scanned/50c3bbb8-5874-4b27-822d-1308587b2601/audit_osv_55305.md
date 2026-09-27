# [C] CVE-2025-27837

## Summary
Severity: Critical
Advisory: CVE-2025-27837
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-25
Source: https://osv.dev/vulnerability/CVE-2025-27837
Type: osv

## Details
An issue was discovered in Artifex Ghostscript before 10.05.0. Access to arbitrary files can occur through a truncated path with invalid UTF-8 characters, for base/gp_mswin.c and base/winrtsup.cpp.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=708238
