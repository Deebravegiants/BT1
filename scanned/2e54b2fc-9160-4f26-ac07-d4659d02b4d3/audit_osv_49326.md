# [M] CVE-2019-1010302

## Summary
Severity: Medium
Advisory: CVE-2019-1010302
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-15
Source: https://osv.dev/vulnerability/CVE-2019-1010302
Type: osv

## Details
jhead 3.03 is affected by: Incorrect Access Control. The impact is: Denial of service. The component is: iptc.c Line 122 show_IPTC(). The attack vector is: the victim must open a specially crafted JPEG file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3WVQTORTGQE56XXC6OVHQCSCUGABRMQZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTGUHTJTQ6EKEPDXFSKZKVLUJC4UAPBQ/
- https://lists.debian.org/debian-lts-announce/2019/12/msg00037.html
- https://security.gentoo.org/glsa/202007-17
- https://bugzilla.redhat.com/show_bug.cgi?id=1679978
