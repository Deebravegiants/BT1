# [C] A user with low privileges can inject SSTI templates that can lead to RCE in open-tickets

## Summary
Severity: Critical
Advisory: CVE-2026-14453
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:H)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-14453
Type: osv

## Details
This vulnerability is a critical Server-Side Template Injection (SSTI) in Centreon's centreon-open-tickets module that leads to Remote Code Execution. The message_confirm field is stored without sanitization and rendered via Smarty with no security policy enabled, allowing any authenticated user, to inject and execute arbitrary code on the server. This results in disclosure of environment secrets and could impact platform availability of Centreon Infra Monitoring product.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14453.json
- https://github.com/centreon/centreon/releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-14453
