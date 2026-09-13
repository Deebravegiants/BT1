# [H] CVE-2016-6823

## Summary
Severity: High
Advisory: CVE-2016-6823
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/CVE-2016-6823
Type: osv

## Details
Integer overflow in the BMP coder in ImageMagick before 7.0.2-10 allows remote attackers to cause a denial of service (crash) via crafted height and width values, which triggers an out-of-bounds write.

## References
- http://www.securityfocus.com/bid/93158
- http://www.openwall.com/lists/oss-security/2016/09/26/3
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=834504
- https://github.com/ImageMagick/ImageMagick/commit/4cc6ec8a4197d4c008577127736bf7985d632323
