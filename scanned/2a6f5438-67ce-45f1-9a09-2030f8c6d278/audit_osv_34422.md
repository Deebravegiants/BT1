# [H] RCE via the backup feature available only to user with high privilege

## Summary
Severity: High
Advisory: CVE-2025-5965
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-5965
Type: osv

## Details
In the backup parameters, a user with high privilege is able to concatenate custom instructions to the backup setup. Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') vulnerability in Centreon Infra Monitoring (Backup configuration in the administration setup modules) allows OS Command Injection.This issue affects Infra Monitoring: from 25.10.0 before 25.10.2, from 24.10.0 before 24.10.15, from 24.04.0 before 24.04.19.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5965.json
- https://github.com/centreon/centreon/releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-5965
- https://thewatch.centreon.com/latest-security-bulletins-64/cve-2025-5965-centreon-web-high-severity-5362
