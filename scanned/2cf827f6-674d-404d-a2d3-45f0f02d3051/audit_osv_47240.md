# [M] CVE-2016-1628

## Summary
Severity: Medium
Advisory: CVE-2016-1628
CVSS: 6.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2016-02-21
Source: https://osv.dev/vulnerability/CVE-2016-1628
Type: osv

## Details
pi.c in OpenJPEG, as used in PDFium in Google Chrome before 48.0.2564.109, does not validate a certain precision value, which allows remote attackers to execute arbitrary code or cause a denial of service (out-of-bounds read) via a crafted JPEG 2000 image in a PDF document, related to the opj_pi_next_rpcl, opj_pi_next_pcrl, and opj_pi_next_cprl functions.

## References
- http://www.securityfocus.com/bid/83125
- http://www.securitytracker.com/id/1035183
- https://code.google.com/p/chromium/issues/detail?id=571479
- https://codereview.chromium.org/1590593002
- http://rhn.redhat.com/errata/RHSA-2016-0241.html
- http://www.debian.org/security/2016/dsa-3486
- http://www.debian.org/security/2017/dsa-4013
- http://www.zerodayinitiative.com/advisories/ZDI-16-172/
- https://security.gentoo.org/glsa/201710-26
- https://security.gentoo.org/glsa/201603-09
- http://googlechromereleases.blogspot.com/2016/02/stable-channel-update_9.html
