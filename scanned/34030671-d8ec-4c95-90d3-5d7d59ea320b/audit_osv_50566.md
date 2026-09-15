# [M] CVE-2020-21723

## Summary
Severity: Medium
Advisory: CVE-2020-21723
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-21723
Type: osv

## Details
A Segmentation Fault issue discovered StreamSerializer::extractStreams function in streamSerializer.cpp in oggvideotools 0.9.1 allows remote attackers to cause a denial of service (crash) via opening of crafted ogg file.

## References
- https://github.com/xiaoxiongwang/security/tree/master/oggvideotools#segv-occurs-in-function-streamserializerextractstreams-in-streamserializercpp
- https://sourceforge.net/p/oggvideotools/bugs/10/
