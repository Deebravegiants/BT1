# [M] Eclipse ThreadX NetX Duo HTTP server denial of service

## Summary
Severity: Medium
Advisory: CVE-2025-0726
Aliases: GHSA-pwf8-5q9w-m763
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-02-21
Source: https://osv.dev/vulnerability/CVE-2025-0726
Type: osv

## Details
In NetX HTTP server functionality of Eclipse ThreadX NetX Duo before 
version 6.4.2, an attacker can cause a denial of service by specially 
crafted packets. The core issue is missing closing of a file in case of 
an error condition, resulting in the 404 error for each further file 
request. Users can work-around the issue by disabling the PUT request 
support.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0726.json
- https://github.com/eclipse-threadx/netxduo/security/advisories/GHSA-pwf8-5q9w-m763
- https://nvd.nist.gov/vuln/detail/CVE-2025-0726
- https://github.com/eclipse-threadx/netxduo/commit/c78d650be7377aae1a8704bc0ce5cc6f9f189014
