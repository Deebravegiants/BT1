# [H] CVE-2018-12363

## Summary
Severity: High
Advisory: CVE-2018-12363
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-10-18
Source: https://osv.dev/vulnerability/CVE-2018-12363
Type: osv

## Details
A use-after-free vulnerability can occur when script uses mutation events to move DOM nodes between documents, resulting in the old document that held the node being freed but the node still having a pointer referencing it. This results in a potentially exploitable crash. This vulnerability affects Thunderbird < 60, Thunderbird < 52.9, Firefox ESR < 60.1, Firefox ESR < 52.9, and Firefox < 61.

## References
- http://www.securitytracker.com/id/1041193
- https://access.redhat.com/errata/RHSA-2018:2112
- https://access.redhat.com/errata/RHSA-2018:2113
- https://lists.debian.org/debian-lts-announce/2018/06/msg00014.html
- https://usn.ubuntu.com/3714-1/
- https://www.mozilla.org/security/advisories/mfsa2018-17/
- https://www.mozilla.org/security/advisories/mfsa2018-18/
- https://www.mozilla.org/security/advisories/mfsa2018-19/
- https://access.redhat.com/errata/RHSA-2018:2251
- https://security.gentoo.org/glsa/201811-13
- https://www.mozilla.org/security/advisories/mfsa2018-15/
- http://www.securityfocus.com/bid/104560
- https://lists.debian.org/debian-lts-announce/2018/07/msg00013.html
- https://www.debian.org/security/2018/dsa-4235
- https://www.debian.org/security/2018/dsa-4244
- https://access.redhat.com/errata/RHSA-2018:2252
- https://security.gentoo.org/glsa/201810-01
- https://usn.ubuntu.com/3705-1/
- https://www.mozilla.org/security/advisories/mfsa2018-16/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1464784
