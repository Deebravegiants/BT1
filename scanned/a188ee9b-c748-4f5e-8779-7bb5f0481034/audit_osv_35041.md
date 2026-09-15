# [H] Second order SQL injection available to user with low privilege

## Summary
Severity: High
Advisory: CVE-2025-6791
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-6791
Type: osv

## Details
In the monitoring event logs page, it is possible to alter the http request to insert a reflect payload in the DB. Caused by an Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') vulnerability in Centreon web (Monitoring event logs modules) allows SQL Injection.This issue affects web: 24.10.0, 24.04.0, 23.10.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/6xxx/CVE-2025-6791.json
- https://github.com/centreon/centreon/releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-6791
- https://thewatch.centreon.com/latest-security-bulletins-64/cve-2025-6791-centreon-web-all-versions-high-severity-4900
