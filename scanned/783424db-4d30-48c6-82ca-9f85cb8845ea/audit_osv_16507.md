# [H] CVE-2019-7524

## Summary
Severity: High
Advisory: CVE-2019-7524
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-28
Source: https://osv.dev/vulnerability/CVE-2019-7524
Type: osv

## Details
In Dovecot before 2.2.36.3 and 2.3.x before 2.3.5.1, a local attacker can cause a buffer overflow in the indexer-worker process, which can be used to elevate to root. This occurs because of missing checks in the fts and pop3-uidl components.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4XLI55NGRDTGMVOPYFCPPFNPA5VKYSSY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QHFZ5OWRIZGIWZJ5PTNVWWZNLLNH4XYS/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00067.html
- http://www.openwall.com/lists/oss-security/2019/03/28/1
- http://www.securityfocus.com/bid/107672
- https://dovecot.org/list/dovecot-news/2019-March/000403.html
- https://dovecot.org/security.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00038.html
- https://security.gentoo.org/glsa/201904-19
- https://usn.ubuntu.com/3928-1/
- https://www.debian.org/security/2019/dsa-4418
- https://seclists.org/bugtraq/2019/Mar/59
