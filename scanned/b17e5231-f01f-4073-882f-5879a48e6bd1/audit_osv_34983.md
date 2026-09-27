# [C] CVE-2025-67108

## Summary
Severity: Critical
Advisory: CVE-2025-67108
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-67108
Type: osv

## Details
eProsima Fast-DDS v3.3 was discovered to contain improper validation for ticket revocation, resulting in insecure communications and connections.

## References
- https://gist.github.com/lkloliver/81b5d5a8328d712dbfd497bf11dbe913
- https://github.com/eProsima/Fast-DDS/blob/master/src/cpp/security/accesscontrol/Permissions.cpp#L263
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67108.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67108
