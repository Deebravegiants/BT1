# [H] CVE-2016-5278

## Summary
Severity: High
Advisory: CVE-2016-5278
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-09-22
Source: https://osv.dev/vulnerability/CVE-2016-5278
Type: osv

## Details
Heap-based buffer overflow in the nsBMPEncoder::AddImageFrame function in Mozilla Firefox before 49.0, Firefox ESR 45.x before 45.4, and Thunderbird < 45.4 allows remote attackers to execute arbitrary code via a crafted image data that is mishandled during the encoding of an image frame to an image.

## References
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2016-3090545.html
- http://www.securitytracker.com/id/1036852
- http://www.securityfocus.com/bid/93049
- http://www.debian.org/security/2016/dsa-3674
- http://www.mozilla.org/security/announce/2016/mfsa2016-85.html
- https://security.gentoo.org/glsa/201701-15
- https://www.mozilla.org/security/advisories/mfsa2016-88/
- http://rhn.redhat.com/errata/RHSA-2016-1912.html
- https://www.mozilla.org/security/advisories/mfsa2016-86/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1294677
