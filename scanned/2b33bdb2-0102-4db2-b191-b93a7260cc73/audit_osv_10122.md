# [H] CVE-2017-13748

## Summary
Severity: High
Advisory: CVE-2017-13748
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13748
Type: osv

## Details
There are lots of memory leaks in JasPer 2.0.12, triggered in the function jas_strdup() in base/jas_string.c, that will lead to a remote denial of service attack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N4ALB4SXHURLVWKAOKYRNJXPABW3M22M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UPOVZTSIQPW2H4AFLMI3LHJEZGBVEQET/
- http://www.securityfocus.com/bid/100514
- https://lists.debian.org/debian-lts-announce/2018/11/msg00023.html
- https://security.gentoo.org/glsa/201908-03
- https://bugzilla.redhat.com/show_bug.cgi?id=1485287
