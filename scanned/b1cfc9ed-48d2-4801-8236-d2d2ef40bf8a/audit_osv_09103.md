# [C] CVE-2016-7943

## Summary
Severity: Critical
Advisory: CVE-2016-7943
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-7943
Type: osv

## Details
The XListFonts function in X.org libX11 before 1.6.4 might allow remote X servers to gain privileges via vectors involving length fields, which trigger out-of-bounds write operations.

## References
- http://www.openwall.com/lists/oss-security/2016/10/04/2
- http://www.openwall.com/lists/oss-security/2016/10/04/4
- http://www.securityfocus.com/bid/93362
- http://www.securitytracker.com/id/1036945
- https://cgit.freedesktop.org/xorg/lib/libX11/commit/?id=8c29f1607a31dac0911e45a0dd3d74173822b3c9
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GMCVDXMFPXR7QGMKDG22WPPJCXH2X3L7/
- https://lists.x.org/archives/xorg-announce/2016-October/002720.html
- https://usn.ubuntu.com/3758-1/
- https://usn.ubuntu.com/3758-2/
- https://security.gentoo.org/glsa/201704-03
