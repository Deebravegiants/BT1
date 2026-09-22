# [H] Rancher has over-inclusive team membership expansion in GitHub App authentication provider

## Summary
Severity: High
Advisory: GHSA-4j6x-2764-m8gh
CVE: CVE-2026-41053
CWE: CWE-303
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-4j6x-2764-m8gh
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.14.0 <2.14.2
- Go: `github.com/rancher/rancher` — affected >=2.13.0 <2.13.6
- Go: `github.com/rancher/rancher` — affected >=0 <0.0.0-20260519172014-d0c047bbc6d2

## Details
### Impact
A vulnerability has been identified within Rancher Manager in the GitHub App authentication provider. When evaluating permissions, the provider incorrectly expands user team memberships to include all teams within the associated GitHub organization, rather than restricting access to the specific teams to which the user actually belongs. 

Specifically, when a user authenticates via the GitHub App provider, Rancher's team membership evaluation logic incorrectly handles cached data. Instead of checking the user-specific list, the evaluation logic iterates over all teams defined within the entire GitHub organization. The authentication provider should consult the correctly cached, per-user membership list to assign the user's specific group permissions. Consequently, any authenticated user who belongs to at least one team in a GitHub organization is mistakenly granted `group principals` for every team within that entire organization during authentication and authorization checks.

This issue allows a malicious user who is a member of a low-privilege team within a GitHub organization to gain unauthorized access to or permissions for any other team in that organization. If those other teams are bound to Rancher login allowlists or RBAC roles (cluster-level, project-level, or global), the attacker can pass access checks that should otherwise fail, inheriting permissions they were never granted.

**Exploitation of this vulnerability requires the following conditions to be met:**
- The GitHub App authentication provider must be enabled and configured for the target GitHub organization.
- The attacker must possess a valid GitHub account with membership in at least one team within that target organization. 
- A separate team within the same GitHub organization must be explicitly mapped to Rancher RBAC roles or specified within Rancher's login allowlist (`allowedPrincipalIds`). 

Please consult the associated  [MITRE ATT&CK - Technique - Valid Accounts](https://attack.mitre.org/techniques/T1078/) for further information about this category of attack.

### Patches
This fix corrects the team listing logic to iterate only the teams stored in the per-user membership cache and includes a one-time startup migration that marks all affected User resources for refresh, forcing Rancher to rebuild `group principals` using the now-corrected logic.

Patched versions of Rancher include releases `v2.14.2` and `v2.13.6`.

### Workarounds
If upgrading to a patched version immediately is not feasible, users are encouraged to  consider these temporary mitigations:
- Disable GitHub App authentication provider and switch to an alternative authentication provider (GitHub OAuth).
- Remove or restrict team-based `group principals` from allowed principalIds.
- Audit and temporarily remove RBAC bindings (`GlobalRoleBindings`, `ClusterRoleTemplateBindings`, `ProjectRoleTemplateBindings`) that reference GitHub App team `principals` until the patch is applied.
- Disable provider refresh and clean up inflated group membership for users (manually or by writing a script).

These workarounds reduce the attack surface but do not eliminate the vulnerability. Existing user sessions and cached principals remain inflated until a provider refresh occurs. Upgrading to a patched version is strongly recommended.

### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-4j6x-2764-m8gh
- https://nvd.nist.gov/vuln/detail/CVE-2026-41053
- https://github.com/rancher/rancher/pull/55093
- https://github.com/rancher/rancher/pull/55147
- https://github.com/rancher/rancher/commit/361d4d57cd09b87f3c53f88af42046ffaa7b57e4
- https://github.com/rancher/rancher/commit/d0c047bbc6d202e953d7557b82cbb354367db6ae
- https://github.com/rancher/rancher
