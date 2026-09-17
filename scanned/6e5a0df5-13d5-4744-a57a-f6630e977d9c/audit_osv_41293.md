# [C] Missing Authorization in Prospero Flow CRM permission save endpoint allows privilege escalation

## Summary
Severity: Critical
Advisory: CVE-2026-59233
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-59233
Type: osv

## Details
Missing Authorization in the permission management component in Roskus Prospero Flow CRM before 5.2.1 allows any authenticated user to grant any role, including their own, the complete set of application permissions via a crafted POST request to the permission save endpoint, which performs no authorization check before synchronizing the submitted permissions to the specified role.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59233.json
- https://github.com/Roskus/prospero-flow-crm/releases/tag/v5.5.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-59233
- https://github.com/Roskus/prospero-flow-crm/commit/86a7d6557bd111518a221f4575ad6e36087e19d3
- https://github.com/Roskus/prospero-flow-crm
- https://secur0.com/en/cna/cve-list/cve-2026-59233-missing-authorization-in-prospero-flow-crm-permission-endpoint
