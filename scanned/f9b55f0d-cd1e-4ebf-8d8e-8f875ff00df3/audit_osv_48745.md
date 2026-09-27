# [H] CVE-2018-12379

## Summary
Severity: High
Advisory: CVE-2018-12379
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-18
Source: https://osv.dev/vulnerability/CVE-2018-12379
Type: osv

## Details
When the Mozilla Updater opens a MAR format file which contains a very long item filename, an out-of-bounds write can be triggered, leading to a potentially exploitable crash. This requires running the Mozilla Updater manually on the local system with the malicious MAR file in order to occur. This vulnerability affects Firefox < 62, Firefox ESR < 60.2, and Thunderbird < 60.2.1.

## References
- https://security.gentoo.org/glsa/201810-01
- https://security.gentoo.org/glsa/201811-13
- https://www.mozilla.org/security/advisories/mfsa2018-25/
- http://www.securityfocus.com/bid/105280
- https://access.redhat.com/errata/RHSA-2018:2692
- https://access.redhat.com/errata/RHSA-2018:2693
- https://access.redhat.com/errata/RHSA-2018:3458
- https://lists.debian.org/debian-lts-announce/2018/11/msg00011.html
- https://www.debian.org/security/2018/dsa-4327
- https://www.mozilla.org/security/advisories/mfsa2018-20/
- https://www.mozilla.org/security/advisories/mfsa2018-21/
- http://www.securitytracker.com/id/1041610
- https://access.redhat.com/errata/RHSA-2018:3403
- https://bugzilla.mozilla.org/show_bug.cgi?id=1473113
