# [C] CVE-2018-12392

## Summary
Severity: Critical
Advisory: CVE-2018-12392
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-28
Source: https://osv.dev/vulnerability/CVE-2018-12392
Type: osv

## Details
When manipulating user events in nested loops while opening a document through script, it is possible to trigger a potentially exploitable crash due to poor event handling. This vulnerability affects Firefox < 63, Firefox ESR < 60.3, and Thunderbird < 60.3.

## References
- https://www.mozilla.org/security/advisories/mfsa2018-26/
- https://lists.debian.org/debian-lts-announce/2018/11/msg00008.html
- https://www.mozilla.org/security/advisories/mfsa2018-28/
- http://www.securityfocus.com/bid/105718
- http://www.securityfocus.com/bid/105769
- https://access.redhat.com/errata/RHSA-2018:3005
- https://access.redhat.com/errata/RHSA-2018:3532
- https://usn.ubuntu.com/3868-1/
- https://www.debian.org/security/2018/dsa-4324
- https://www.debian.org/security/2018/dsa-4337
- http://www.securitytracker.com/id/1041944
- https://lists.debian.org/debian-lts-announce/2018/11/msg00011.html
- https://security.gentoo.org/glsa/201811-04
- https://www.mozilla.org/security/advisories/mfsa2018-27/
- https://access.redhat.com/errata/RHSA-2018:3006
- https://access.redhat.com/errata/RHSA-2018:3531
- https://security.gentoo.org/glsa/201811-13
- https://usn.ubuntu.com/3801-1/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1492823
