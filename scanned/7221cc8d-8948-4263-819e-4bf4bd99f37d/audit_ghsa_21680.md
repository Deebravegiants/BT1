# [M] Limited ability to spoof SAML authentication with missing audience verification in Fleet

## Summary
Severity: Medium
Advisory: GHSA-ch68-7cf4-35vr
CVE: CVE-2022-23600
CWE: CWE-284, CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-07
Source: https://github.com/advisories/GHSA-ch68-7cf4-35vr
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.9.1

## Details
### Impact

This impacts deployments using SAML SSO in two specific cases:

1. A malicious or compromised Service Provider (SP) could reuse the SAML response to log into Fleet as a user -- only if the user has an account with the same email in Fleet, _and_ the user signs into the malicious SP via SAML SSO from the same Identity Provider (IdP) configured with Fleet.
2. A user with an account in Fleet could reuse a SAML response intended for another SP to log into Fleet. This is only a concern if the user is blocked from Fleet in the IdP, but continues to have an account in Fleet. If the user is blocked from the IdP entirely, this cannot be exploited.

### Patches
Fleet 4.9.1 resolves this issue.

### Workarounds and good practices
* Reduce the length of sessions on your IdP to reduce the window for malicious re-use.
* Limit the amount of SAML Service Providers/Applications used by user accounts with access to Fleet.
* When removing access to Fleet in the IdP, delete the Fleet user from Fleet as well.

### For more information
If you have any questions or comments about this advisory:
* Join us in the #fleet channel of [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw).
* Email us at [security@fleetdm.com](mailto:security@fleetdm.com).

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-ch68-7cf4-35vr
- https://nvd.nist.gov/vuln/detail/CVE-2022-23600
- https://github.com/fleetdm/fleet/commit/35d5a7b285f15ddd47486fa656e8b1acf3d48374
- https://github.com/fleetdm/fleet
