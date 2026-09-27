# [H] JumpServer Unauthorized LDAP Configuration Access via WebSocket

## Summary
Severity: High
Advisory: CVE-2025-62795
Aliases: GHSA-7893-256g-m822
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2025-10-30
Source: https://osv.dev/vulnerability/CVE-2025-62795
Type: osv

## Details
JumpServer is an open source bastion host and an operation and maintenance security audit system. Prior to v3.10.21-lts and v4.10.12-lts, a low-privileged authenticated user can invoke LDAP configuration tests and start LDAP synchronization by sending crafted messages to the /ws/ldap/ WebSocket endpoint, bypassing authorization checks and potentially exposing LDAP credentials or causing unintended sync operations. This vulnerability is fixed in v3.10.21-lts and v4.10.12-lts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62795.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-7893-256g-m822
- https://nvd.nist.gov/vuln/detail/CVE-2025-62795
