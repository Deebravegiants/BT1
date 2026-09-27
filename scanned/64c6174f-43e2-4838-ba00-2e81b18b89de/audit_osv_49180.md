# [C] CVE-2018-5159

## Summary
Severity: Critical
Advisory: CVE-2018-5159
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2018-5159
Type: osv

## Details
An integer overflow can occur in the Skia library due to 32-bit integer use in an array without integer overflow checks, resulting in possible out-of-bounds writes. This could lead to a potentially exploitable crash triggerable by web content. This vulnerability affects Thunderbird < 52.8, Thunderbird ESR < 52.8, Firefox < 60, and Firefox ESR < 52.8.

## References
- https://security.gentoo.org/glsa/201811-13
- https://usn.ubuntu.com/3645-1/
- https://www.mozilla.org/security/advisories/mfsa2018-13/
- https://www.debian.org/security/2018/dsa-4199
- https://www.debian.org/security/2018/dsa-4209
- https://www.mozilla.org/security/advisories/mfsa2018-12/
- https://lists.debian.org/debian-lts-announce/2018/05/msg00013.html
- https://www.mozilla.org/security/advisories/mfsa2018-11/
- https://usn.ubuntu.com/3660-1/
- http://www.securitytracker.com/id/1040896
- https://access.redhat.com/errata/RHSA-2018:1414
- https://access.redhat.com/errata/RHSA-2018:1725
- https://access.redhat.com/errata/RHSA-2018:1726
- https://lists.debian.org/debian-lts-announce/2018/05/msg00007.html
- https://security.gentoo.org/glsa/201810-01
- http://www.securityfocus.com/bid/104136
- https://access.redhat.com/errata/RHSA-2018:1415
- https://bugzilla.mozilla.org/show_bug.cgi?id=1441941
- https://www.exploit-db.com/exploits/44759/
