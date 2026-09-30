# [H] Privilege escalation by altering payload in contact form

## Summary
Severity: High
Advisory: CVE-2025-3872
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-24
Source: https://osv.dev/vulnerability/CVE-2025-3872
Type: osv

## Details
Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') vulnerability in Centreon centreon-web (User configuration form modules) allows SQL Injection.


A user with high privileges is able to become administrator by intercepting the contact form request and altering its payload.



This issue affects Centreon: from 22.10.0 before 22.10.28, from 23.04.0 before 23.04.25, from 23.10.0 before 23.10.20, from 24.04.0 before 24.04.10, from 24.10.0 before 24.10.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/3xxx/CVE-2025-3872.json
- https://github.com/centreon/centreon/releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-3872
- https://thewatch.centreon.com/latest-security-bulletins-64/cve-2024-55571-centreon-web-high-severity-4496
