# [M] CVE-2017-1000472

## Summary
Severity: Medium
Advisory: CVE-2017-1000472
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-01-03
Source: https://osv.dev/vulnerability/CVE-2017-1000472
Type: osv

## Details
The ZipCommon::isValidPath() function in Zip/src/ZipCommon.cpp in POCO C++ Libraries before 1.8 does not properly restrict the filename value in the ZIP header, which allows attackers to conduct absolute path traversal attacks during the ZIP decompression, and possibly create or overwrite arbitrary files, via a crafted ZIP file, related to a "file path injection vulnerability".

## References
- https://lists.debian.org/debian-lts-announce/2018/01/msg00013.html
- https://www.debian.org/security/2018/dsa-4083
- https://github.com/pocoproject/poco/issues/1968
