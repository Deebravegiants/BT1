# [M] CVE-2019-13453

## Summary
Severity: Medium
Advisory: CVE-2019-13453
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-13453
Type: osv

## Details
Zipios before 0.1.7 does not properly handle certain malformed zip archives and can go into an infinite loop, causing a denial of service. This is related to zipheadio.h:readUint32() and zipfile.cpp:Zipfile::Zipfile().

## References
- https://lists.debian.org/debian-lts-announce/2022/05/msg00041.html
- http://www.securityfocus.com/bid/109282
- https://salvatoresecurity.com/fun-with-fuzzers-how-i-discovered-three-vulnerabilities-part-2-of-3/
- https://sourceforge.net/p/zipios/news/2019/07/version-017-cve-/
