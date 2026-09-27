# [H] CVE-2017-7225

## Summary
Severity: High
Advisory: CVE-2017-7225
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-22
Source: https://osv.dev/vulnerability/CVE-2017-7225
Type: osv

## Details
The find_nearest_line function in addr2line in GNU Binutils 2.28 does not handle the case where the main file name and the directory name are both empty, triggering a NULL pointer dereference and an invalid write, and leading to a program crash.

## References
- http://www.securityfocus.com/bid/97275
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=20891
