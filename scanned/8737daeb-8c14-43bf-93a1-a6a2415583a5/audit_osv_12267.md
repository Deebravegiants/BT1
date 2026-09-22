# [H] CVE-2018-11130

## Summary
Severity: High
Advisory: CVE-2018-11130
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-17
Source: https://osv.dev/vulnerability/CVE-2018-11130
Type: osv

## Details
The header::add_FORMAT_descriptor function in header.cpp in VCFtools 0.1.15 allows remote attackers to cause a denial of service (use-after-free) or possibly have unspecified other impact via a crafted vcf file.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00039.html
- https://usn.ubuntu.com/3974-1/
- http://seclists.org/fulldisclosure/2018/May/43
