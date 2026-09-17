# [C] CVE-2020-20277

## Summary
Severity: Critical
Advisory: CVE-2020-20277
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-18
Source: https://osv.dev/vulnerability/CVE-2020-20277
Type: osv

## Details
There are multiple unauthenticated directory traversal vulnerabilities in different FTP commands in uftpd FTP server versions 2.7 to 2.10 due to improper implementation of a chroot jail in common.c's compose_abspath function that can be abused to read or write to arbitrary files on the filesystem, leak process memory, or potentially lead to remote code execution.

## References
- https://arinerron.com/blog/posts/6
- https://github.com/troglobit/uftpd/commit/455b47d3756aed162d2d0ef7f40b549f3b5b30fe
- http://packetstormsecurity.com/files/167908/uftpd-2.10-Directory-Traversal.html
