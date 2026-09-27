# [H] CVE-2017-5507

## Summary
Severity: High
Advisory: CVE-2017-5507
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2017-5507
Type: osv

## Details
Memory leak in coders/mpc.c in ImageMagick before 6.9.7-4 and 7.x before 7.0.4-4 allows remote attackers to cause a denial of service (memory consumption) via vectors involving a pixel cache.

## References
- http://www.debian.org/security/2017/dsa-3799
- http://www.securityfocus.com/bid/95752
- https://github.com/ImageMagick/ImageMagick/blob/6.9.7-4/ChangeLog
- https://github.com/ImageMagick/ImageMagick/blob/7.0.4-4/ChangeLog
- https://security.gentoo.org/glsa/201702-09
- http://www.openwall.com/lists/oss-security/2017/01/16/6
- http://www.openwall.com/lists/oss-security/2017/01/17/5
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=851382
- https://github.com/ImageMagick/ImageMagick/commit/66e283e0a9c141b19fe6c4c39f4a41c0d3188ba8
