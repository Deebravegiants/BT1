# [C] SkyPilot Authentication Bypass via Service Account Role Escalation

## Summary
Severity: Critical
Advisory: CVE-2026-75481
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75481
Type: osv

## Details
SkyPilot fails to validate that authenticated users are entitled to grant administrator roles when updating service account permissions. Attackers can create a service account, escalate it to administrator role, and authenticate with its bearer token to gain administrative control over all users and workspaces.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75481.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75481
- https://www.vulncheck.com/advisories/skypilot-authentication-bypass-via-service-account-role-escalation
- https://github.com/skypilot-org/skypilot/issues/9846
- https://github.com/skypilot-org/skypilot/commit/8a3e00259cd374e662cd876c037164bcb070f78e
- https://github.com/skypilot-org/skypilot
- https://github.com/skypilot-org/skypilot/blob/master/sky/users/server.py
