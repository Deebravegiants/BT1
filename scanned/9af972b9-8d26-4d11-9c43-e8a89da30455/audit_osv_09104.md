# [C] CVE-2016-7944

## Summary
Severity: Critical
Advisory: CVE-2016-7944
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-7944
Type: osv

## Details
Integer overflow in X.org libXfixes before 5.0.3 on 32-bit platforms might allow remote X servers to gain privileges via a length value of INT_MAX, which triggers the client to stop reading data and get out of sync.

## References
- http://www.openwall.com/lists/oss-security/2016/10/04/2
- http://www.openwall.com/lists/oss-security/2016/10/04/4
- http://www.securityfocus.com/bid/93361
- http://www.securitytracker.com/id/1036945
- https://cgit.freedesktop.org/xorg/lib/libXfixes/commit/?id=61c1039ee23a2d1de712843bed3480654d7ef42e
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4CE6VJWBMOWLSCH4OP4TAEPIA7NP53ON/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GE43MDCRGS4R7MRRZNVSLREHRLU5OHCV/
- https://lists.x.org/archives/xorg-announce/2016-October/002720.html
- https://security.gentoo.org/glsa/201704-03
