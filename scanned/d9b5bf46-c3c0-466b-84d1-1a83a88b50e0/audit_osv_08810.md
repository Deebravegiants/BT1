# [C] CVE-2016-6223

## Summary
Severity: Critical
Advisory: CVE-2016-6223
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-6223
Type: osv

## Details
The TIFFReadRawStrip1 and TIFFReadRawTile1 functions in tif_read.c in libtiff before 4.0.7 allows remote attackers to cause a denial of service (crash) or possibly obtain sensitive information via a negative index in a file-content buffer.

## References
- http://www.securityfocus.com/bid/91741
- http://www.debian.org/security/2017/dsa-3762
- https://security.gentoo.org/glsa/201701-16
- http://libtiff.maptools.org/v4.0.7.html
- http://www.openwall.com/lists/oss-security/2016/07/13/3
- http://www.openwall.com/lists/oss-security/2016/07/14/4
