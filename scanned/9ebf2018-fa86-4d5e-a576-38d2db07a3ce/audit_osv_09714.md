# [C] CVE-2017-10984

## Summary
Severity: Critical
Advisory: CVE-2017-10984
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-10984
Type: osv

## Details
An FR-GV-301 issue in FreeRADIUS 3.x before 3.0.15 allows "Write overflow in data2vp_wimax()" - this allows remote attackers to cause a denial of service (daemon crash) or possibly execute arbitrary code.

## References
- http://www.securityfocus.com/bid/99876
- http://www.debian.org/security/2017/dsa-3930
- https://access.redhat.com/errata/RHSA-2017:2389
- http://freeradius.org/security/fuzzer-2017.html
