# [M] CVE-2016-10053

## Summary
Severity: Medium
Advisory: CVE-2016-10053
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-10053
Type: osv

## Details
The WriteTIFFImage function in coders/tiff.c in ImageMagick before 6.9.5-8 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted file.

## References
- http://www.openwall.com/lists/oss-security/2016/12/26/9
- http://www.securityfocus.com/bid/95179
- https://bugzilla.redhat.com/show_bug.cgi?id=1410461
- https://github.com/ImageMagick/ImageMagick/commit/728dc6a600cf4cbdac846964c85cc04339db8ac1
- https://github.com/ImageMagick/ImageMagick/commit/f983dcdf9c178e0cbc49608a78713c5669aa1bb5
