# [M] AVideo User_Location Plugin Unauthenticated SQL Injection

## Summary
Severity: Medium
Advisory: CVE-2026-84208
Aliases: GHSA-xj29-cg44-33q6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84208
Type: osv

## Details
AVideo through version 29.0 contains an unauthenticated SQL injection vulnerability in the User_Location plugin's regions.json.php and cities.json.php endpoints. The country and region GET parameters are passed directly into SQL queries without escaping or prepared statement binding, allowing unauthenticated attackers to execute UNION-based SQL injection to read arbitrary database contents including password hashes and sensitive data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84208.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-xj29-cg44-33q6
- https://nvd.nist.gov/vuln/detail/CVE-2026-84208
- https://www.vulncheck.com/advisories/avideo-user-location-plugin-unauthenticated-sql-injection
