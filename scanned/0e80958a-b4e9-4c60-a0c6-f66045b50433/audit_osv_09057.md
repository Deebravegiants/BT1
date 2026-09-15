# [M] CVE-2016-7530

## Summary
Severity: Medium
Advisory: CVE-2016-7530
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2016-7530
Type: osv

## Details
The quantum handling code in ImageMagick allows remote attackers to cause a denial of service (divide-by-zero error or out-of-bounds write) via a crafted file.

## References
- http://www.securityfocus.com/bid/93131
- https://bugs.launchpad.net/bugs/1539053
- https://bugs.launchpad.net/bugs/1539067
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1378762
- https://github.com/ImageMagick/ImageMagick/commit/63346f34f9d19179599b5b256e5e8d3dda46435c
- https://github.com/ImageMagick/ImageMagick/commit/b5ed738f8060266bf4ae521f7e3ed145aa4498a3
- https://github.com/ImageMagick/ImageMagick/commit/c4e63ad30bc42da691f2b5f82a24516dd6b4dc70
- https://github.com/ImageMagick/ImageMagick/issues/105
- https://github.com/ImageMagick/ImageMagick/issues/110
