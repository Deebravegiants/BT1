# [H] CVE-2015-3418

## Summary
Severity: High
Advisory: CVE-2015-3418
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2015-3418
Type: osv

## Details
The ProcPutImage function in dix/dispatch.c in X.Org Server (aka xserver and xorg-server) before 1.16.4 allows attackers to cause a denial of service (divide-by-zero and crash) via a zero-height PutImage request.

## References
- https://security.gentoo.org/glsa/201701-64
- http://www.oracle.com/technetwork/topics/security/bulletinapr2015-2511959.html
- http://www.securityfocus.com/bid/74328
- https://cgit.freedesktop.org/xorg/xserver/commit/?id=dc777c346d5d452a53b13b917c45f6a1bad2f20b
- https://lists.x.org/archives/xorg-announce/2015-February/002532.html
