# [H] CVE-2021-3561

## Summary
Severity: High
Advisory: CVE-2021-3561
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2021-3561
Type: osv

## Details
An Out of Bounds flaw was found fig2dev version 3.2.8a. A flawed bounds check in read_objects() could allow an attacker to provide a crafted malicious input causing the application to either crash or in some cases cause memory corruption. The highest threat from this vulnerability is to integrity as well as system availability.

## References
- https://lists.debian.org/debian-lts-announce/2021/10/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/C44WSY5KAQXC3Y2NMSVXXZS3M5U5U2E6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JKMOIQX6GULVSYXLYW5JQY6KJNTWV3E4/
- https://sourceforge.net/p/mcj/fig2dev/ci/6827c09d2d6491cb2ae3ac7196439ff3aa791fd9/
- https://bugzilla.redhat.com/show_bug.cgi?id=1955675
- https://sourceforge.net/p/mcj/tickets/116/
