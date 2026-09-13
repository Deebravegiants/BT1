# [H] CVE-2020-7046

## Summary
Severity: High
Advisory: CVE-2020-7046
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2020-7046
Type: osv

## Details
lib-smtp in submission-login and lmtp in Dovecot 2.3.9 before 2.3.9.3 mishandles truncated UTF-8 data in command parameters, as demonstrated by the unauthenticated triggering of a submission-login infinite loop.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6XYT55WH372BJOXCJRKBDIFGBMPVOIDT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NJXHOUT3FH2DJNMACSX4GHPP4MUV4UKA/
- http://www.openwall.com/lists/oss-security/2020/02/12/1
- https://dovecot.org/pipermail/dovecot-news/2020-February/000431.html
- https://dovecot.org/security
