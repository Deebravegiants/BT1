# [M] CVE-2019-19722

## Summary
Severity: Medium
Advisory: CVE-2019-19722
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2019-12-13
Source: https://osv.dev/vulnerability/CVE-2019-19722
Type: osv

## Details
In Dovecot before 2.3.9.2, an attacker can crash a push-notification driver with a crafted email when push notifications are used, because of a NULL Pointer Dereference. The email must use a group address as either the sender or the recipient.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4OZCJ3RBA4WIYGN7SOV4TW2AIHXPZATK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6PPB7PG5BM3MC5ZF2KHQ3UR7CZIO42BB/
- http://www.openwall.com/lists/oss-security/2019/12/13/3
- https://dovecot.org/list/dovecot-news/2019-December/000428.html
- https://dovecot.org/pipermail/dovecot-news/2019-December/000428.html
- https://dovecot.org/security.html
