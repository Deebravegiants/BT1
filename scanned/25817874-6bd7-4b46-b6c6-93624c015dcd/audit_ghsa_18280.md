# [H] Fides Webserver API is Vulnerable to OAuth Client Privilege Escalation

## Summary
Severity: High
Advisory: GHSA-hjfh-p8f5-24wr
CVE: CVE-2025-57817
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-08
Source: https://github.com/advisories/GHSA-hjfh-p8f5-24wr
Type: github-advisory

## Affected
- PyPI: `ethyca-fides` — affected >=0 <2.69.1

## Details
### Summary
The OAuth client creation and update endpoints of the Fides Webserver API do not properly authorize scope assignment. This allows highly privileged users with `client:create` or `client:update` permissions to escalate their privileges to owner-level.

### Details
When creating or updating OAuth clients, the API validates only that requested scopes exist in the system registry. It does not verify that the requester already possesses the scopes they are assigning, allowing these users to assign arbitrary scopes to OAuth clients.

### Impact
This allows contributor-level users to escalate to owner-equivalent privileges, gaining access to user management, system configuration, and permission assignment capabilities they should not possess.

### Patches
The vulnerability has been patched in Fides version `2.69.1`. Users are advised to upgrade to this version or later to secure their systems against this threat.

### Workarounds
There are no workarounds.

### Risk Level
This vulnerability has been assigned a severity of HIGH. Contributor users are already highly privileged, only a handful of scopes are not already available to them, but these scopes can be abused for high impact.

## References
- https://github.com/ethyca/fides/security/advisories/GHSA-hjfh-p8f5-24wr
- https://nvd.nist.gov/vuln/detail/CVE-2025-57817
- https://github.com/ethyca/fides/commit/2ffd125e1089a09b84c27fb5279a05960cbf2452
- https://github.com/ethyca/fides
- https://github.com/ethyca/fides/releases/tag/2.69.1
