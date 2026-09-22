# [H] Daytona: Cross-org IDOR in organization role update/delete — any org owner can rewrite or destroy another org's roles

## Summary
Severity: High
Advisory: GHSA-qxvm-pcfm-qc39
CVE: CVE-2026-54322
CWE: CWE-639, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-qxvm-pcfm-qc39
Type: github-advisory

## Affected
- Go: `github.com/daytonaio/daytona` — affected >=0 <0.185.0

## Details
### Summary
Daytona's organization role update and delete endpoints authorized the caller as an owner of the organization named in the request path, but resolved and mutated the target role by its identifier alone, without verifying the role belonged to that organization. An authenticated user who owns any organization (organizations are self-service) could therefore modify the permissions of, or delete, a role belonging to a different organization, given that role's identifier.

### Impact
This is a cross-tenant broken access control (IDOR) issue affecting multi-tenant deployments, including the managed Daytona platform. Using a target role's identifier, an attacker with owner rights over their own organization could:

- Overwrite the target role's name and permission set, escalating or stripping privileges for every member and API key in the victim organization that holds that role.
- Delete the target role, removing the associated permissions from its holders.
- Observe the victim role's current permission set returned in the update response (limited information disclosure).

Exploitation requires knowledge of the target role's identifier, which is not enumerable across organizations and is not exposed to non-members through the API.

### Affected versions
All versions up to and including 0.184.0.

### Patches
Fixed in 0.185.0. The role update, delete, and role-assignment lookups are now scoped to the caller's organization, so a role belonging to another organization resolves to "not found" before any read or mutation. The managed Daytona platform was updated on release of 0.185.0.

### Workarounds
None. Upgrade to 0.185.0. Single-organization self-hosted deployments are not exploitable, as the issue requires a second organization to target.

### Credit
Reported by @vnth4nhnt.

## References
- https://github.com/daytonaio/daytona/security/advisories/GHSA-qxvm-pcfm-qc39
- https://nvd.nist.gov/vuln/detail/CVE-2026-54322
- https://github.com/daytonaio/daytona
