# [H] CVE-2018-5996

## Summary
Severity: High
Advisory: CVE-2018-5996
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-31
Source: https://osv.dev/vulnerability/CVE-2018-5996
Type: osv

## Details
Insufficient exception handling in the method NCompress::NRar3::CDecoder::Code of 7-Zip before 18.00 and p7zip can lead to multiple memory corruptions within the PPMd code, allows remote attackers to cause a denial of service (segmentation fault) or execute arbitrary code via a crafted RAR archive.

## References
- http://www.securitytracker.com/id/1040831
- https://github.com/p7zip-project/p7zip/issues/32
- https://github.com/p7zip-project/p7zip/issues/8
- https://0patch.blogspot.si/2018/02/two-interesting-micropatches-for-7-zip.html
- https://landave.io/2018/01/7-zip-multiple-memory-corruptions-via-rar-and-zip/
