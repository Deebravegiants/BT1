# [M] CVE-2019-1010301

## Summary
Severity: Medium
Advisory: CVE-2019-1010301
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-15
Source: https://osv.dev/vulnerability/CVE-2019-1010301
Type: osv

## Details
jhead 3.03 is affected by: Buffer Overflow. The impact is: Denial of service. The component is: gpsinfo.c Line 151 ProcessGpsInfo(). The attack vector is: Open a specially crafted JPEG file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3WVQTORTGQE56XXC6OVHQCSCUGABRMQZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTGUHTJTQ6EKEPDXFSKZKVLUJC4UAPBQ/
- https://security.gentoo.org/glsa/202007-17
- https://lists.debian.org/debian-lts-announce/2019/12/msg00037.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1679952
- https://launchpadlibrarian.net/435112680/32_crash_in_gpsinfo
- https://bugs.launchpad.net/ubuntu/+source/jhead/+bug/1838251
