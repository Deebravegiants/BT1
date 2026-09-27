# [C] CVE-2016-7951

## Summary
Severity: Critical
Advisory: CVE-2016-7951
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-7951
Type: osv

## Details
Multiple integer overflows in X.org libXtst before 1.2.3 allow remote X servers to trigger out-of-bounds memory access operations by leveraging the lack of range checks.

## References
- http://www.openwall.com/lists/oss-security/2016/10/04/2
- http://www.openwall.com/lists/oss-security/2016/10/04/4
- http://www.securityfocus.com/bid/93370
- http://www.securitytracker.com/id/1036945
- https://cgit.freedesktop.org/xorg/lib/libXtst/commit/?id=9556ad67af3129ec4a7a4f4b54a0d59701beeae3
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AFLHX7WNEUXXDAGR324T35L5P6RRR7GE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RVEUZRHYY3AJEKMFQ4DS7DX3Y2AICFP7/
- https://lists.x.org/archives/xorg-announce/2016-October/002720.html
