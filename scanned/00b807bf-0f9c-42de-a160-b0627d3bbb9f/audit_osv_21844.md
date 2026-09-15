# [M] Directory Traversal in OpenLiteSpeed Web Server

## Summary
Severity: Medium
Advisory: CVE-2022-0072
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2022-10-27
Source: https://osv.dev/vulnerability/CVE-2022-0072
Type: osv

## Details
Directory Traversal vulnerability in LiteSpeed Technologies OpenLiteSpeed Web Server and LiteSpeed Web Server dashboards allows Path Traversal. This affects versions from 1.5.11 through 1.5.12, from 1.6.5 through 1.6.20.1, from 1.7.0 before 1.7.16.1

## References
- https://github.com/litespeedtech/openlitespeed/blob/v1.7.16.1/src/main/httpserver.cpp#L2060-L2061
- https://github.com/litespeedtech/openlitespeed/blob/v1.7.16/src/main/httpserver.cpp#L2060-L2061
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0072.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-0072
- https://github.com/litespeedtech/openlitespeed
