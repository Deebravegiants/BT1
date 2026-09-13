# [M] CVE-2018-12366

## Summary
Severity: Medium
Advisory: CVE-2018-12366
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-10-18
Source: https://osv.dev/vulnerability/CVE-2018-12366
Type: osv

## Details
An invalid grid size during QCMS (color profile) transformations can result in the out-of-bounds read interpreted as a float value. This could leak private data into the output. This vulnerability affects Thunderbird < 60, Thunderbird < 52.9, Firefox ESR < 60.1, Firefox ESR < 52.9, and Firefox < 61.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00013.html
- https://www.debian.org/security/2018/dsa-4244
- https://security.gentoo.org/glsa/201811-13
- https://usn.ubuntu.com/3705-1/
- https://usn.ubuntu.com/3714-1/
- https://www.mozilla.org/security/advisories/mfsa2018-15/
- https://www.mozilla.org/security/advisories/mfsa2018-16/
- http://www.securitytracker.com/id/1041193
- https://access.redhat.com/errata/RHSA-2018:2251
- https://lists.debian.org/debian-lts-announce/2018/06/msg00014.html
- https://security.gentoo.org/glsa/201810-01
- https://www.mozilla.org/security/advisories/mfsa2018-17/
- https://www.mozilla.org/security/advisories/mfsa2018-19/
- https://access.redhat.com/errata/RHSA-2018:2112
- https://www.debian.org/security/2018/dsa-4235
- https://www.mozilla.org/security/advisories/mfsa2018-18/
- http://www.securityfocus.com/bid/104560
- https://access.redhat.com/errata/RHSA-2018:2113
- https://access.redhat.com/errata/RHSA-2018:2252
- https://bugzilla.mozilla.org/show_bug.cgi?id=1464039
