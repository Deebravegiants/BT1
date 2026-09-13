# [H] CVE-2018-12393

## Summary
Severity: High
Advisory: CVE-2018-12393
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-28
Source: https://osv.dev/vulnerability/CVE-2018-12393
Type: osv

## Details
A potential vulnerability was found in 32-bit builds where an integer overflow during the conversion of scripts to an internal UTF-16 representation could result in allocating a buffer too small for the conversion. This leads to a possible out-of-bounds write. *Note: 64-bit builds are not vulnerable to this issue.*. This vulnerability affects Firefox < 63, Firefox ESR < 60.3, and Thunderbird < 60.3.

## References
- http://www.securityfocus.com/bid/105718
- http://www.securitytracker.com/id/1041944
- https://lists.debian.org/debian-lts-announce/2018/11/msg00011.html
- https://security.gentoo.org/glsa/201811-13
- http://www.securityfocus.com/bid/105769
- https://access.redhat.com/errata/RHSA-2018:3005
- https://access.redhat.com/errata/RHSA-2018:3531
- https://access.redhat.com/errata/RHSA-2018:3532
- https://lists.debian.org/debian-lts-announce/2018/11/msg00008.html
- https://security.gentoo.org/glsa/201811-04
- https://www.debian.org/security/2018/dsa-4324
- https://usn.ubuntu.com/3801-1/
- https://usn.ubuntu.com/3868-1/
- https://www.debian.org/security/2018/dsa-4337
- https://www.mozilla.org/security/advisories/mfsa2018-26/
- https://www.mozilla.org/security/advisories/mfsa2018-27/
- https://www.mozilla.org/security/advisories/mfsa2018-28/
- https://access.redhat.com/errata/RHSA-2018:3006
- https://bugzilla.mozilla.org/show_bug.cgi?id=1495011
