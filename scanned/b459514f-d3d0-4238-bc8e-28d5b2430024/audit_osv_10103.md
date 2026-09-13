# [H] CVE-2017-13723

## Summary
Severity: High
Advisory: CVE-2017-13723
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/CVE-2017-13723
Type: osv

## Details
In X.Org Server (aka xserver and xorg-server) before 1.19.4, a local attacker authenticated to the X server could overflow a global buffer, causing crashes of the X server or potentially other problems by injecting large or malformed XKB related atoms and accessing them via xkbcomp.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00032.html
- http://www.debian.org/security/2017/dsa-4000
- http://www.openwall.com/lists/oss-security/2017/10/04/10
- http://www.securityfocus.com/bid/101253
- https://cgit.freedesktop.org/xorg/xserver/commit/?id=94f11ca5cf011ef123bd222cabeaef6f424d76ac
- https://lists.x.org/archives/xorg-announce/2017-October/002808.html
- https://security.gentoo.org/glsa/201710-30
