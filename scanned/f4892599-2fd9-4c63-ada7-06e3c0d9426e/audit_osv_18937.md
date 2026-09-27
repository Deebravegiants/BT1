# [H] CVE-2020-5221

## Summary
Severity: High
Advisory: CVE-2020-5221
Aliases: GHSA-wmx8-v7mx-6x9h
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2020-01-22
Source: https://osv.dev/vulnerability/CVE-2020-5221
Type: osv

## Details
In uftpd before 2.11, it is possible for an unauthenticated user to perform a directory traversal attack using multiple different FTP commands and read and write to arbitrary locations on the filesystem due to the lack of a well-written chroot jail in compose_abspath(). This has been fixed in version 2.11

## References
- https://github.com/troglobit/uftpd/commit/455b47d3756aed162d2d0ef7f40b549f3b5b30fe
- https://github.com/troglobit/uftpd/security/advisories/GHSA-wmx8-v7mx-6x9h
