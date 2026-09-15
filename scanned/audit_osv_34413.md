# [H] RCE via the poller reload feature available only to user with high privilege

## Summary
Severity: High
Advisory: CVE-2025-5946
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-14
Source: https://osv.dev/vulnerability/CVE-2025-5946
Type: osv

## Details
Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') vulnerability in Centreon Infra Monitoring (Poller reload setup in the configuration modules) allows OS Command Injection.
On the poller parameters page, a user with high privilege is able to concatenate custom instructions into the poller reload command.

This issue affects Infra Monitoring: from 24.10.0 before 24.10.13, from 24.04.0 before 24.04.18, from 23.10.0 before 23.10.28.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5946.json
- https://github.com/centreon/centreon/releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-5946
- https://thewatch.centreon.com/latest-security-bulletins-64/cve-2025-5946-centreon-web-all-versions-high-severity-5104
