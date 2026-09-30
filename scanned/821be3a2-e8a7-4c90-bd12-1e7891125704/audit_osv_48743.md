# [C] CVE-2018-12377

## Summary
Severity: Critical
Advisory: CVE-2018-12377
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-18
Source: https://osv.dev/vulnerability/CVE-2018-12377
Type: osv

## Details
A use-after-free vulnerability can occur when refresh driver timers are refreshed in some circumstances during shutdown when the timer is deleted while still in use. This results in a potentially exploitable crash. This vulnerability affects Firefox < 62, Firefox ESR < 60.2, and Thunderbird < 60.2.1.

## References
- https://usn.ubuntu.com/3793-1/
- https://www.debian.org/security/2018/dsa-4327
- https://www.mozilla.org/security/advisories/mfsa2018-20/
- https://access.redhat.com/errata/RHSA-2018:2693
- https://access.redhat.com/errata/RHSA-2018:3458
- https://lists.debian.org/debian-lts-announce/2018/11/msg00011.html
- https://security.gentoo.org/glsa/201810-01
- https://security.gentoo.org/glsa/201811-13
- https://www.mozilla.org/security/advisories/mfsa2018-25/
- http://www.securityfocus.com/bid/105280
- http://www.securitytracker.com/id/1041610
- https://access.redhat.com/errata/RHSA-2018:2692
- https://www.debian.org/security/2018/dsa-4287
- https://access.redhat.com/errata/RHSA-2018:3403
- https://usn.ubuntu.com/3761-1/
- https://www.mozilla.org/security/advisories/mfsa2018-21/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1470260
