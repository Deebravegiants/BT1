# [M] CVE-2018-11439

## Summary
Severity: Medium
Advisory: CVE-2018-11439
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-05-30
Source: https://osv.dev/vulnerability/CVE-2018-11439
Type: osv

## Details
The TagLib::Ogg::FLAC::File::scan function in oggflacfile.cpp in TagLib 1.11.1 allows remote attackers to cause information disclosure (heap-based buffer over-read) via a crafted audio file.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00022.html
- https://lists.debian.org/debian-lts-announce/2021/09/msg00020.html
- http://seclists.org/fulldisclosure/2018/May/49
