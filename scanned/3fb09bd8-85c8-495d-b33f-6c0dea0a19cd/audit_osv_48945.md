# [C] CVE-2018-18493

## Summary
Severity: Critical
Advisory: CVE-2018-18493
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-28
Source: https://osv.dev/vulnerability/CVE-2018-18493
Type: osv

## Details
A buffer overflow can occur in the Skia library during buffer offset calculations with hardware accelerated canvas 2D actions due to the use of 32-bit calculations instead of 64-bit. This results in a potentially exploitable crash. This vulnerability affects Thunderbird < 60.4, Firefox ESR < 60.4, and Firefox < 64.

## References
- https://access.redhat.com/errata/RHSA-2018:3831
- https://access.redhat.com/errata/RHSA-2018:3833
- https://lists.debian.org/debian-lts-announce/2018/12/msg00002.html
- http://www.securityfocus.com/bid/106168
- https://access.redhat.com/errata/RHSA-2019:0160
- https://www.debian.org/security/2018/dsa-4354
- https://access.redhat.com/errata/RHSA-2019:0159
- https://usn.ubuntu.com/3844-1/
- https://security.gentoo.org/glsa/201903-04
- https://usn.ubuntu.com/3868-1/
- https://www.debian.org/security/2019/dsa-4362
- https://www.mozilla.org/security/advisories/mfsa2018-29/
- https://www.mozilla.org/security/advisories/mfsa2018-30/
- https://www.mozilla.org/security/advisories/mfsa2018-31/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1504452
