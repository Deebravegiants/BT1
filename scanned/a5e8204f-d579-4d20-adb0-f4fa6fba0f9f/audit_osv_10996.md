# [C] CVE-2017-5581

## Summary
Severity: Critical
Advisory: CVE-2017-5581
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-28
Source: https://osv.dev/vulnerability/CVE-2017-5581
Type: osv

## Details
Buffer overflow in the ModifiablePixelBuffer::fillRect function in TigerVNC before 1.7.1 allows remote servers to execute arbitrary code via an RRE message with subrectangle outside framebuffer boundaries.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0630.html
- http://www.securityfocus.com/bid/95789
- https://access.redhat.com/errata/RHSA-2017:2000
- https://github.com/TigerVNC/tigervnc/releases/tag/v1.7.1
- https://security.gentoo.org/glsa/201702-19
- http://www.openwall.com/lists/oss-security/2017/01/22/1
- http://www.openwall.com/lists/oss-security/2017/01/25/6
- https://github.com/TigerVNC/tigervnc/commit/18c020124ff1b2441f714da2017f63dba50720ba
- https://github.com/TigerVNC/tigervnc/pull/399
