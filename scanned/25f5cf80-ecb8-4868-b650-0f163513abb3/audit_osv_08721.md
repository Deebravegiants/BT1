# [C] CVE-2016-5407

## Summary
Severity: Critical
Advisory: CVE-2016-5407
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-5407
Type: osv

## Details
The (1) XvQueryAdaptors and (2) XvQueryEncodings functions in X.org libXv before 1.0.11 allow remote X servers to trigger out-of-bounds memory access operations via vectors involving length specifications in received data.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3IA7BLB4C3JOYVU6UASGUJQJKUF6TO7E/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AE2VJOFA3EZA566RERQB54TFY56FROZR/
- http://www.openwall.com/lists/oss-security/2016/10/04/2
- http://www.openwall.com/lists/oss-security/2016/10/04/4
- http://www.securityfocus.com/bid/93368
- http://www.securitytracker.com/id/1036945
- https://lists.x.org/archives/xorg-announce/2016-October/002720.html
- https://security.gentoo.org/glsa/201704-03
- https://cgit.freedesktop.org/xorg/lib/libXv/commit/?id=d9da580b46a28ab497de2e94fdc7b9ff953dab17
