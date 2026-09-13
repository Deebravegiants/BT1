# [C] CVE-2016-7947

## Summary
Severity: Critical
Advisory: CVE-2016-7947
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-7947
Type: osv

## Details
Multiple integer overflows in X.org libXrandr before 1.5.1 allow remote X servers to trigger out-of-bounds write operations via a crafted response.

## References
- http://www.openwall.com/lists/oss-security/2016/10/04/2
- http://www.openwall.com/lists/oss-security/2016/10/04/4
- http://www.securityfocus.com/bid/93365
- http://www.securitytracker.com/id/1036945
- https://cgit.freedesktop.org/xorg/lib/libXrandr/commit/?id=a0df3e1c7728205e5c7650b2e6dce684139254a6
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/74FFOHWYIKQZTJLRJWDMJ4W3WYBELUUG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y7662OZWCSTLRPKS6R3E4Y4M26BSVAAM/
- https://lists.x.org/archives/xorg-announce/2016-October/002720.html
- https://security.gentoo.org/glsa/201704-03
