# [C] Fleet has SAML authentication vulnerability due to improper SAML response validation

## Summary
Severity: Critical
Advisory: GHSA-52jx-g6m5-h735
CVE: CVE-2025-27509
CWE: CWE-285, CWE-74
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-06
Source: https://github.com/advisories/GHSA-52jx-g6m5-h735
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=4.64.0 <4.64.2
- Go: `github.com/fleetdm/fleet/v4` — affected >=4.63.0 <4.63.2
- Go: `github.com/fleetdm/fleet/v4` — affected >=4.62.0 <4.62.4
- Go: `github.com/fleetdm/fleet/v4` — affected >=4.54.0 <4.58.1
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.53.2

## Details
### Summary

A vulnerability in Fleet’s SAML authentication handling could allow an attacker to forge authentication assertions and gain unauthorized access to Fleet. In certain configurations, this could result in the creation of new user accounts, including administrative accounts. This issue affects Fleet deployments using single sign-on (SSO).

### Impact

In vulnerable versions of Fleet, an attacker could craft a specially-formed SAML response to:

- Forge authentication assertions, potentially impersonating legitimate users.
- If Just-In-Time (JIT) provisioning is enabled, the attacker could provision a new administrative user account.
- If MDM enrollment is enabled, certain endpoints could be used to create new accounts tied to forged assertions.

This could allow unauthorized access to Fleet, including administrative access, visibility into device data, and modification of configuration. 

### Patches

This issue is addressed in commit [fc96cc4](https://github.com/fleetdm/fleet/commit/fc96cc4e91047250afb12f65ad70e90b30a7fb1c) and is available in Fleet version 4.64.2.

The following backport versions also address this issue: 

- 4.63.2
- 4.62.4
- 4.58.1
- 4.53.2

### Workarounds

If an immediate upgrade is not possible, Fleet users should temporarily disable [single-sign-on (SSO)](https://fleetdm.com/docs/deploy/single-sign-on-sso) and use password authentication.

### Credit

Thank you @hakivvi, as well as Jeffrey Hofmann and Colby Morgan from the Robinhood Red Team for finding and reporting this vulnerability using our [responsible disclosure process](https://github.com/fleetdm/fleet/blob/main/SECURITY.md).

### For more information

If you have any questions or comments about this advisory:

- Email us at security@fleetdm.com
- Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-52jx-g6m5-h735
- https://nvd.nist.gov/vuln/detail/CVE-2025-27509
- https://github.com/fleetdm/fleet/commit/718c95e47ad010ad6b8ceb3f3460e921fbfc53bb
- https://github.com/fleetdm/fleet
- https://github.com/fleetdm/fleet/releases/tag/fleet-v4.64.2
- https://pkg.go.dev/vuln/GO-2025-3505
