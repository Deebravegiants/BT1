# [H] CVE-2020-21724

## Summary
Severity: High
Advisory: CVE-2020-21724
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-21724
Type: osv

## Details
Buffer Overflow vulnerability in ExtractorInformation function in streamExtractor.cpp in oggvideotools 0.9.1 allows remaote attackers to run arbitrary code via opening of crafted ogg file.

## References
- https://github.com/xiaoxiongwang/security/tree/master/oggvideotools#segv-and-heap-overflow-detected-in-line-17-of-streamextractorcpp
- https://sourceforge.net/p/oggvideotools/bugs/9/
