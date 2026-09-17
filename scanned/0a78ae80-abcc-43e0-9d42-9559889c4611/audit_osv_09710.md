# [C] CVE-2017-10979

## Summary
Severity: Critical
Advisory: CVE-2017-10979
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-10979
Type: osv

## Details
An FR-GV-202 issue in FreeRADIUS 2.x before 2.2.10 allows "Write overflow in rad_coalesce()" - this allows remote attackers to cause a denial of service (daemon crash) or possibly execute arbitrary code.

## References
- http://www.securityfocus.com/bid/99901
- http://www.debian.org/security/2017/dsa-3930
- http://www.securitytracker.com/id/1038914
- https://access.redhat.com/errata/RHSA-2017:1759
- http://freeradius.org/security/fuzzer-2017.html
