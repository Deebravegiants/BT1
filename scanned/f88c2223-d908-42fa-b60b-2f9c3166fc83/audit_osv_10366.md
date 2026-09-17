# [H] CVE-2017-15120

## Summary
Severity: High
Advisory: CVE-2017-15120
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-15120
Type: osv

## Details
An issue has been found in the parsing of authoritative answers in PowerDNS Recursor before 4.0.8, leading to a NULL pointer dereference when parsing a specially crafted answer containing a CNAME of a different class than IN. An unauthenticated remote attacker could cause a denial of service.

## References
- http://www.securityfocus.com/bid/106335
- https://www.debian.org/security/2017/dsa-4063
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-15120
- http://seclists.org/oss-sec/2017/q4/382
- https://doc.powerdns.com/recursor/security-advisories/powerdns-advisory-2017-08.html
