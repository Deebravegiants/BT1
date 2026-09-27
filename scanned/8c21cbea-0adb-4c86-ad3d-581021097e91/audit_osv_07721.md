# [M] Apache Tomcat: Security constraint bypass with HTTP/0.9

## Summary
Severity: Medium
Advisory: BIT-tomcat-2026-24733
Aliases: CVE-2026-24733, GHSA-qq5r-98hh-rxc9
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-24733
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.15

## Details
Improper Input Validation vulnerability in Apache Tomcat.


Tomcat did not limit HTTP/0.9 requests to the GET method. If a security 
constraint was configured to allow HEAD requests to a URI but deny GET 
requests, the user could bypass that constraint on GET requests by 
sending a (specification invalid) HEAD request using HTTP/0.9.


This issue affects Apache Tomcat: from 11.0.0 through 11.0.14, from 10.1.0 through 10.1.49, from 9.0.0 through 9.0.112.


Older, EOL versions are also affected.

Users are recommended to upgrade to version 11.0.15 or later, 10.1.50 or later or 9.0.113 or later, which fixes the issue.

## References
- https://lists.apache.org/thread/6xk3t65qpn1myp618krtfotbjn1qt90f
- https://nvd.nist.gov/vuln/detail/CVE-2026-24733
