# [M] CVE-2017-13736

## Summary
Severity: Medium
Advisory: CVE-2017-13736
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13736
Type: osv

## Details
There are lots of memory leaks in the GMCommand function in magick/command.c in GraphicsMagick 1.3.26 that will lead to a remote denial of service attack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- http://www.securityfocus.com/bid/100513
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://bugzilla.redhat.com/show_bug.cgi?id=1484192
