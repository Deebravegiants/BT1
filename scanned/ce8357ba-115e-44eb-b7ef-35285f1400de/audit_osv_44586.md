# [C] FeatherPanel before 1.3.7.10 Privilege Escalation via Subuser Permission Update

## Summary
Severity: Critical
Advisory: CVE-2026-84715
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84715
Type: osv

## Details
FeatherPanel versions before 1.3.7.10 fail to validate permissions in the SubuserController updateSubuser handler, allowing authenticated subusers to modify their own permission records. A subuser with minimal permissions can send a crafted request to grant themselves full server control, enabling unauthorized access to sensitive data, backups, and server configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84715.json
- https://github.com/MythicalLTD/FeatherPanel/releases/tag/v1.3.7.10
- https://nvd.nist.gov/vuln/detail/CVE-2026-84715
- https://www.vulncheck.com/advisories/featherpanel-before-1.3.7.10-privilege-escalation-via-subuser-permission-update
- https://github.com/MythicalLTD/FeatherPanel/commit/06ef8dcac471201748516ca743694159cb846a9d
- https://github.com/MythicalLTD/FeatherPanel
- https://github.com/MythicalLTD/FeatherPanel/blob/376b003aa9685b74153d239d2b3f64a752cdc0f0/backend/app/Controllers/User/Server/SubuserController.php#L454
- https://github.com/MythicalLTD/FeatherPanel/blob/376b003aa9685b74153d239d2b3f64a752cdc0f0/backend/app/Helpers/ServerGateway.php
