# [M] CVE-2020-7957

## Summary
Severity: Medium
Advisory: CVE-2020-7957
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2020-7957
Type: osv

## Details
The IMAP and LMTP components in Dovecot 2.3.9 before 2.3.9.3 mishandle snippet generation when many characters must be read to compute the snippet and a trailing > character exists. This causes a denial of service in which the recipient cannot read all of their messages.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6XYT55WH372BJOXCJRKBDIFGBMPVOIDT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NJXHOUT3FH2DJNMACSX4GHPP4MUV4UKA/
- https://dovecot.org/security
- http://www.openwall.com/lists/oss-security/2020/02/12/2
- https://dovecot.org/pipermail/dovecot-news/2020-February/000430.html
