# [H] CVE-2018-6359

## Summary
Severity: High
Advisory: CVE-2018-6359
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-27
Source: https://osv.dev/vulnerability/CVE-2018-6359
Type: osv

## Details
The decompileIF function (util/decompile.c) in libming through 0.4.8 is vulnerable to a use-after-free, which may allow attackers to cause a denial of service or unspecified other impact via a crafted SWF file.

## References
- http://www.securityfocus.com/bid/102856
- https://lists.debian.org/debian-lts-announce/2018/03/msg00008.html
- https://security.gentoo.org/glsa/201904-24
- https://github.com/libming/libming/issues/105
