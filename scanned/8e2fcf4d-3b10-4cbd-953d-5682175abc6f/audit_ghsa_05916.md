# [M] Fleet: Observer-class users can view team enroll secrets and credential-bearing configuration via target search endpoint

## Summary
Severity: Medium
Advisory: GHSA-88p2-jj8w-j8qg
CVE: CVE-2026-48786
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-12
Source: https://github.com/advisories/GHSA-88p2-jj8w-j8qg
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.87.0

## Details
### Summary

The target search endpoint (`POST /api/latest/fleet/targets`) returned team enroll secrets and full team configuration, including credential-bearing agent options, to observer-class users. Other team-facing endpoints mask these fields for observers; the target search endpoint did not apply the same sanitization.

### Impact

An authenticated user with Observer, Observer+, or Technician role (global or team-scoped) could retrieve unmasked team enroll secrets and team agent options by performing a target search against an observer-runnable query.

With a leaked team enroll secret, an attacker could enroll unauthorized hosts into the affected team. If the team's agent options contained credentials such as AWS secret access keys or proxy passwords, those values were also exposed.

### Patches

- v4.87.0

### Workarounds

If an immediate upgrade is not possible, administrators should:

- Rotate team enroll secrets for any team that may have been exposed
- Rotate any credentials stored in team agent options (AWS keys, proxy passwords, session tokens)
- Restrict Observer and Technician roles to fully trusted users until the patch is applied

### Credits

Fleet thanks @fuzzztf for responsibly reporting this issue.

### For more information

If there are any questions or comments about this advisory:

Send an email to [security@fleetdm.com](mailto:security@fleetdm.com)
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-88p2-jj8w-j8qg
- https://github.com/fleetdm/fleet
- https://github.com/fleetdm/fleet/releases/tag/fleet-v4.87.0
