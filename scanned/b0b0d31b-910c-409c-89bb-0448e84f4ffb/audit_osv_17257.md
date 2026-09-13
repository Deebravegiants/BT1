# [H] CVE-2020-14149

## Summary
Severity: High
Advisory: CVE-2020-14149
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-15
Source: https://osv.dev/vulnerability/CVE-2020-14149
Type: osv

## Details
In uftpd before 2.12, handle_CWD in ftpcmd.c mishandled the path provided by the user, causing a NULL pointer dereference and denial of service, as demonstrated by a CWD /.. command.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00052.html
- https://github.com/troglobit/uftpd/releases/tag/v2.12
- https://bugs.gentoo.org/726308
- https://github.com/troglobit/uftpd/issues/30
