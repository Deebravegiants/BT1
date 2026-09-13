# [H] CVE-2016-7945

## Summary
Severity: High
Advisory: CVE-2016-7945
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-7945
Type: osv

## Details
Multiple integer overflows in X.org libXi before 1.7.7 allow remote X servers to cause a denial of service (out-of-bounds memory access or infinite loop) via vectors involving length fields.

## References
- http://www.openwall.com/lists/oss-security/2016/10/04/2
- http://www.openwall.com/lists/oss-security/2016/10/04/4
- http://www.securityfocus.com/bid/93364
- http://www.securitytracker.com/id/1036945
- https://cgit.freedesktop.org/xorg/lib/libXi/commit/?id=19a9cd607de73947fcfb104682f203ffe4e1f4e5
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/C3NTWIWSQ575GREBVAOUQUIMDL5CDVGP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KVTZ2XLPKLASQUIQA2GMKKAUOQIUMM7I/
- https://lists.x.org/archives/xorg-announce/2016-October/002720.html
- https://security.gentoo.org/glsa/201704-03
