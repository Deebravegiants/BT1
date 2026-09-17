# [M] CVE-2019-19783

## Summary
Severity: Medium
Advisory: CVE-2019-19783
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-12-16
Source: https://osv.dev/vulnerability/CVE-2019-19783
Type: osv

## Details
An issue was discovered in Cyrus IMAP before 2.5.15, 3.0.x before 3.0.13, and 3.1.x through 3.1.8. If sieve script uploading is allowed (3.x) or certain non-default sieve options are enabled (2.x), a user with a mail account on the service can use a sieve script containing a fileinto directive to create any mailbox with administrator privileges, because of folder mishandling in autosieve_createfolder() in imap/lmtp_sieve.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2DIV4HQ6LG5GPRO4B5Z2NHCZUPBUVVVF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6IGOO5UGEBBDPN7B2YXLK7I7L3Y35EBA/
- https://seclists.org/bugtraq/2019/Dec/38
- https://security.gentoo.org/glsa/202006-23
- https://usn.ubuntu.com/4566-1/
- https://www.debian.org/security/2019/dsa-4590
- https://www.cyrusimap.org/imap/download/release-notes/2.5/x/2.5.15.html
- https://www.cyrusimap.org/imap/download/release-notes/3.0/x/3.0.13.html
