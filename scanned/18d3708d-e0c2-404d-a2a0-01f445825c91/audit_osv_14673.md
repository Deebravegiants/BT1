# [H] CVE-2019-10691

## Summary
Severity: High
Advisory: CVE-2019-10691
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-24
Source: https://osv.dev/vulnerability/CVE-2019-10691
Type: osv

## Details
The JSON encoder in Dovecot before 2.3.5.2 allows attackers to repeatedly crash the authentication service by attempting to authenticate with an invalid UTF-8 sequence as the username.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QHFZ5OWRIZGIWZJ5PTNVWWZNLLNH4XYS/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00000.html
- http://www.openwall.com/lists/oss-security/2019/04/18/3
- https://dovecot.org/list/dovecot-news/2019-April/000406.html
- https://security.gentoo.org/glsa/201908-29
