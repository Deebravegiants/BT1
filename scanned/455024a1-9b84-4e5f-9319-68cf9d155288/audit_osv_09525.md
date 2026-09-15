# [H] CVE-2017-1000050

## Summary
Severity: High
Advisory: CVE-2017-1000050
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-1000050
Type: osv

## Details
JasPer 2.0.12 is vulnerable to a NULL pointer exception in the function jp2_encode which failed to check to see if the image contained at least one component resulting in a denial-of-service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N4ALB4SXHURLVWKAOKYRNJXPABW3M22M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UPOVZTSIQPW2H4AFLMI3LHJEZGBVEQET/
- http://www.openwall.com/lists/oss-security/2017/03/06/1
- http://www.securityfocus.com/bid/96595
- https://access.redhat.com/errata/RHSA-2018:3253
- https://access.redhat.com/errata/RHSA-2018:3505
- https://security.gentoo.org/glsa/201908-03
- https://usn.ubuntu.com/3693-1/
