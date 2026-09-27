# [C] Fleet has a JWT signature bypass vulnerability in Azure AD MDM enrollment 

## Summary
Severity: Critical
Advisory: GHSA-63m5-974w-448v
CVE: CVE-2026-23518
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-63m5-974w-448v
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet` — affected >=4.78.0 <4.78.3
- Go: `github.com/fleetdm/fleet` — affected >=4.77.0 <4.77.1
- Go: `github.com/fleetdm/fleet` — affected >=4.76.0 <4.76.2
- Go: `github.com/fleetdm/fleet` — affected >=4.75.0 <4.75.2
- Go: `github.com/fleetdm/fleet` — affected >=0 <4.43.5-0.20260112202845-e225ef57912c

## Details
### Summary

A vulnerability in Fleet’s Windows MDM enrollment flow could allow an attacker to submit forged authentication tokens that are not properly validated. Because JWT signatures were not verified, Fleet could accept attacker-controlled identity claims, enabling enrollment of unauthorized devices under arbitrary Azure AD user identities.

### Impact

If Windows MDM is enabled, an attacker can enroll rogue devices by submitting a forged JWT containing arbitrary identity claims. Due to missing JWT signature verification, Fleet accepts these claims without validating that the token was issued by Azure AD, allowing enrollment under any Azure AD user identity.

### Patches

- 4.78.3
- 4.77.1
- 4.76.2
- 4.75.2
- 4.53.3

### Workarounds

If an immediate upgrade is not possible, affected Fleet users should temporarily disable Windows MDM.

### For more information

If you have any questions or comments about this advisory:

Email us at [security@fleetdm.com](mailto:security@fleetdm.com)
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

We thank @secfox-ai for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-63m5-974w-448v
- https://nvd.nist.gov/vuln/detail/CVE-2026-23518
- https://github.com/fleetdm/fleet/commit/e225ef57912c8f4ac8977e24b5ebe1d9fd875257
- https://github.com/fleetdm/fleet
- https://pkg.go.dev/vuln/GO-2026-4335
