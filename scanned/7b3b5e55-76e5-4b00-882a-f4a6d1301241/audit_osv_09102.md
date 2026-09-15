# [C] CVE-2016-7942

## Summary
Severity: Critical
Advisory: CVE-2016-7942
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-7942
Type: osv

## Details
The XGetImage function in X.org libX11 before 1.6.4 might allow remote X servers to gain privileges via vectors involving image type and geometry, which triggers out-of-bounds read operations.

## References
- http://www.openwall.com/lists/oss-security/2016/10/04/2
- http://www.openwall.com/lists/oss-security/2016/10/04/4
- http://www.securityfocus.com/bid/93363
- http://www.securitytracker.com/id/1036945
- https://cgit.freedesktop.org/xorg/lib/libX11/commit/?id=8ea762f94f4c942d898fdeb590a1630c83235c17
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GMCVDXMFPXR7QGMKDG22WPPJCXH2X3L7/
- https://lists.x.org/archives/xorg-announce/2016-October/002720.html
- https://usn.ubuntu.com/3758-1/
- https://usn.ubuntu.com/3758-2/
- https://security.gentoo.org/glsa/201704-03
