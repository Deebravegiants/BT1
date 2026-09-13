# [H] CVE-2020-25275

## Summary
Severity: High
Advisory: CVE-2020-25275
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-04
Source: https://osv.dev/vulnerability/CVE-2020-25275
Type: osv

## Details
Dovecot before 2.3.13 has Improper Input Validation in lda, lmtp, and imap, leading to an application crash via a crafted email message with certain choices for ten thousand MIME parts.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GXDKFLOCUP7I4ELGQ2F4P5TGC6NXMYV7/
- http://packetstormsecurity.com/files/160841/Dovecot-2.3.11.3-Denial-Of-Service.html
- http://seclists.org/fulldisclosure/2021/Jan/18
- http://www.openwall.com/lists/oss-security/2021/01/04/3
- https://dovecot.org/pipermail/dovecot-news/2021-January/000451.html
- https://dovecot.org/security
- https://security.gentoo.org/glsa/202101-01
- https://www.debian.org/security/2021/dsa-4825
