# [M] CVE-2016-1626

## Summary
Severity: Medium
Advisory: CVE-2016-1626
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2016-02-14
Source: https://osv.dev/vulnerability/CVE-2016-1626
Type: osv

## Details
The opj_pi_update_decode_poc function in pi.c in OpenJPEG, as used in PDFium in Google Chrome before 48.0.2564.109, miscalculates a certain layer index value, which allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted PDF document.

## References
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00104.html
- http://www.securityfocus.com/bid/83125
- https://code.google.com/p/chromium/issues/detail?id=571480
- https://codereview.chromium.org/1583233008
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00119.html
- http://www.securitytracker.com/id/1035183
- http://www.zerodayinitiative.com/advisories/ZDI-16-171
- https://security.gentoo.org/glsa/201710-26
- http://rhn.redhat.com/errata/RHSA-2016-0241.html
- http://www.debian.org/security/2016/dsa-3486
- https://security.gentoo.org/glsa/201603-09
- http://googlechromereleases.blogspot.com/2016/02/stable-channel-update_9.html
