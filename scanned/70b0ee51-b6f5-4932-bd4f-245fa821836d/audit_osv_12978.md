# [M] CVE-2018-16646

## Summary
Severity: Medium
Advisory: CVE-2018-16646
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-16646
Type: osv

## Details
In Poppler 0.68.0, the Parser::getObj() function in Parser.cc may cause infinite recursion via a crafted file. A remote attacker can leverage this for a DoS attack.

## References
- https://lists.debian.org/debian-lts-announce/2020/07/msg00018.html
- https://access.redhat.com/errata/RHSA-2019:2022
- https://lists.debian.org/debian-lts-announce/2018/10/msg00024.html
- https://lists.debian.org/debian-lts-announce/2018/11/msg00040.html
- https://lists.debian.org/debian-lts-announce/2018/12/msg00004.html
- https://usn.ubuntu.com/3837-1/
- https://usn.ubuntu.com/3837-2/
- https://bugzilla.redhat.com/show_bug.cgi?id=1622951
