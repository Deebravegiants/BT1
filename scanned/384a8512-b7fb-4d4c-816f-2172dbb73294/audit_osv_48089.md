# [H] CVE-2017-17969

## Summary
Severity: High
Advisory: CVE-2017-17969
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-30
Source: https://osv.dev/vulnerability/CVE-2017-17969
Type: osv

## Details
Heap-based buffer overflow in the NCompress::NShrink::CDecoder::CodeReal method in 7-Zip before 18.00 and p7zip allows remote attackers to cause a denial of service (out-of-bounds write) or potentially execute arbitrary code via a crafted ZIP archive.

## References
- https://usn.ubuntu.com/3913-1/
- http://www.securitytracker.com/id/1040831
- https://lists.debian.org/debian-lts-announce/2018/02/msg00003.html
- https://www.debian.org/security/2018/dsa-4104
- https://github.com/p7zip-project/p7zip/issues/7
- https://0patch.blogspot.si/2018/02/two-interesting-micropatches-for-7-zip.html
- https://landave.io/2018/01/7-zip-multiple-memory-corruptions-via-rar-and-zip/
