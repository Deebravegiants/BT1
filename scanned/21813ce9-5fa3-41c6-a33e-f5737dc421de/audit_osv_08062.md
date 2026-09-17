# [C] CVE-2016-10164

## Summary
Severity: Critical
Advisory: CVE-2016-10164
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-01
Source: https://osv.dev/vulnerability/CVE-2016-10164
Type: osv

## Details
Multiple integer overflows in libXpm before 3.5.12, when a program requests parsing XPM extensions on a 64-bit platform, allow remote attackers to cause a denial of service (out-of-bounds write) or execute arbitrary code via (1) the number of extensions or (2) their concatenated length in a crafted XPM file, which triggers a heap-based buffer overflow.

## References
- http://www.debian.org/security/2017/dsa-3772
- http://www.securityfocus.com/bid/95785
- https://access.redhat.com/errata/RHSA-2017:1865
- https://security.gentoo.org/glsa/201701-72
- http://www.openwall.com/lists/oss-security/2017/01/22/2
- http://www.openwall.com/lists/oss-security/2017/01/25/7
- https://cgit.freedesktop.org/xorg/lib/libXpm/commit/?id=d1167418f0fd02a27f617ec5afd6db053afbe185
- https://lists.freedesktop.org/archives/xorg/2016-December/058537.html
