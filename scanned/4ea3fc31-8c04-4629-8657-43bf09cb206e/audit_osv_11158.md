# [M] CVE-2017-6430

## Summary
Severity: Medium
Advisory: CVE-2017-6430
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6430
Type: osv

## Details
The compile_tree function in ef_compiler.c in the Etterfilter utility in Ettercap 0.8.2 and earlier allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted filter.

## References
- http://www.securityfocus.com/archive/1/540223/100/0/threaded
- http://www.securitytracker.com/id/1038057
- http://www.debian.org/security/2017/dsa-3874
- http://www.securityfocus.com/bid/96582
- https://github.com/LocutusOfBorg/ettercap/commit/626dc56686f15f2dda13c48f78c2a666cb6d8506
- https://github.com/Ettercap/ettercap/issues/782
