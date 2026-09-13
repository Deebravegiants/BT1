# [H] Capgo - Cross-Organization Authorization Bypass via Scoped API Key Privilege Inheritance

## Summary
Severity: High
Advisory: CVE-2026-56246
Aliases: GHSA-ccm4-hf72-p28m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-56246
Type: osv

## Details
Capgo before 12.128.2 contains a broken access control vulnerability in the organization management API where a scoped API key (limited_to_orgs) inherits its owner-user's permissions, allowing destructive cross-organization actions. When a user is an admin in two organizations and creates a write-mode API key restricted to one organization, that key can still perform destructive operations (e.g., DELETE /organization, DELETE /organization/members) against another organization. The root cause is route-level authorization (rbac_check_permission_direct) that evaluates the key owner's user privileges before enforcing the API key's limited_to_orgs scope.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56246.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-ccm4-hf72-p28m
- https://nvd.nist.gov/vuln/detail/CVE-2026-56246
- https://www.vulncheck.com/advisories/capgo-cross-organization-authorization-bypass-via-scoped-api-key-privilege-inheritance
