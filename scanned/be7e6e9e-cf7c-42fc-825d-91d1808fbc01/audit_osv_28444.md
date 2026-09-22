# [C] Apache Fineract: SQL injection vulnerabilities in offices API endpoint

## Summary
Severity: Critical
Advisory: CVE-2024-32838
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2024-32838
Type: osv

## Details
SQL Injection vulnerability in various API endpoints - offices, dashboards, etc. Apache Fineract versions 1.9 and before have a vulnerability that allows an authenticated attacker to inject malicious data into some of the REST API endpoints' query parameter. 
Users are recommended to upgrade to version 1.10.1, which fixes this issue.

A SQL Validator has been implemented which allows us to configure a series of tests and checks against our SQL queries that will allow us to validate and protect against nearly all potential SQL injection attacks.

## References
- http://www.openwall.com/lists/oss-security/2025/02/12/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32838.json
- https://lists.apache.org/thread/7l88h17pn9nf8zpx5bbojk7ko5oxo1dy
- https://nvd.nist.gov/vuln/detail/CVE-2024-32838
