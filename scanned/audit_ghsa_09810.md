# [M] zrok: Broken ownership check in DELETE /api/v2/unaccess allows non-admin to delete global frontend records

## Summary
Severity: Medium
Advisory: GHSA-3jpj-v3xr-5h6g
CVE: CVE-2026-40304
CWE: CWE-284, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-3jpj-v3xr-5h6g
Type: github-advisory

## Affected
- Go: `github.com/openziti/zrok` — affected >=0
- Go: `github.com/openziti/zrok/v2` — affected >=0 <2.0.1

## Details
Summary
The unaccess handler (controller/unaccess.go) contains a logical error in its ownership guard: when a frontend record has environment_id = NULL (the marker for admin-created global frontends), the condition short-circuits to false and allows the deletion to proceed without any ownership verification. A non-admin user who knows a global frontend token can call DELETE /api/v2/unaccess with any of their own environment IDs and permanently delete the global frontend, taking down all public shares routed through it.

Attack Vector: Network — the endpoint is a standard HTTP API call.

Attack Complexity: High — successful exploitation requires prior knowledge of a global frontend token. These tokens are not returned to non-admin users by any standard API endpoint; obtaining one requires an out-of-band step (e.g., leaked server logs, admin documentation for a self-hosted instance, or social engineering).

Privileges Required: Low — a valid user account with at least one registered environment is required; no admin privileges needed.

User Interaction: None.

Scope: Unchanged — the impact stays within the same server instance.

Confidentiality Impact: None — no data is disclosed.

Integrity Impact: None — no data is improperly modified; the record is deleted (not corrupted).

Availability Impact: High — deleting a global frontend disrupts every public share routed through it on the instance, constituting a platform-wide availability impact.

Affected Component
controller/unaccess.go — unaccessHandler.Handle (line 56)

## References
- https://github.com/openziti/zrok/security/advisories/GHSA-3jpj-v3xr-5h6g
- https://nvd.nist.gov/vuln/detail/CVE-2026-40304
- https://github.com/openziti/zrok
- https://github.com/openziti/zrok/releases/tag/v2.0.1
