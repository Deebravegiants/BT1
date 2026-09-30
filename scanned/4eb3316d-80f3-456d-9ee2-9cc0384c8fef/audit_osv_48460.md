# [C] CVE-2017-7824

## Summary
Severity: Critical
Advisory: CVE-2017-7824
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-7824
Type: osv

## Details
A buffer overflow occurs when drawing and validating elements with the ANGLE graphics library, used for WebGL content. This is due to an incorrect value being passed within the library during checks and results in a potentially exploitable crash. This vulnerability affects Firefox < 56, Firefox ESR < 52.4, and Thunderbird < 52.4.

## References
- http://www.securityfocus.com/bid/101053
- https://access.redhat.com/errata/RHSA-2017:2831
- https://access.redhat.com/errata/RHSA-2017:2885
- https://lists.debian.org/debian-lts-announce/2017/11/msg00000.html
- https://www.debian.org/security/2017/dsa-4014
- https://www.mozilla.org/security/advisories/mfsa2017-21/
- http://www.securitytracker.com/id/1039465
- https://security.gentoo.org/glsa/201803-14
- https://www.debian.org/security/2017/dsa-3987
- https://www.mozilla.org/security/advisories/mfsa2017-22/
- https://www.mozilla.org/security/advisories/mfsa2017-23/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1398381
