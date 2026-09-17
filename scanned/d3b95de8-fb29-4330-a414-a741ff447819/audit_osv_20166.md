# [M] CVE-2021-3181

## Summary
Severity: Medium
Advisory: CVE-2021-3181
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-01-19
Source: https://osv.dev/vulnerability/CVE-2021-3181
Type: osv

## Details
rfc822.c in Mutt through 2.0.4 allows remote attackers to cause a denial of service (mailbox unavailability) by sending email messages with sequences of semicolon characters in RFC822 address fields (aka terminators of empty groups). A small email message from the attacker can cause large memory consumption, and the victim may then be unable to see email messages from other persons.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DXGWXFO77HBCD3VYEIYHHYU33LYWWWNQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P2OMLQKAOHPYQA4GI7ZUO6UKCPUHLYO7/
- http://www.openwall.com/lists/oss-security/2021/01/19/10
- http://www.openwall.com/lists/oss-security/2021/01/27/3
- https://gitlab.com/muttmua/mutt/-/issues/323
- https://lists.debian.org/debian-lts-announce/2021/01/msg00017.html
- https://security.gentoo.org/glsa/202101-25
- https://www.debian.org/security/2021/dsa-4838
- https://gitlab.com/muttmua/mutt/-/commit/4a2becbdb4422aaffe3ce314991b9d670b7adf17
- https://gitlab.com/muttmua/mutt/-/commit/939b02b33ae29bc0d642570c1dcfd4b339037d19
- https://gitlab.com/muttmua/mutt/-/commit/d4305208955c5cdd9fe96dfa61e7c1e14e176a14
