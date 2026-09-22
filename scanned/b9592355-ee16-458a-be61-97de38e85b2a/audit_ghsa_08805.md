# [H] Fleet Windows MDM Azure AD JWT Authentication Bypass

## Summary
Severity: High
Advisory: GHSA-ffg9-j72f-j6xm
CVE: CVE-2026-24899
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-ffg9-j72f-j6xm
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.82.0

## Details
### Summary

A vulnerability in Fleet's Windows MDM enrollment flow allows authentication tokens from any Azure AD tenant to be accepted. Because Fleet validates JWT signatures using Microsoft's multi-tenant JWKS endpoint but does not enforce the `aud` (audience) or `iss` (issuer) claims, any Microsoft-signed Azure AD access token containing the expected scopes can be used to authenticate to Fleet's MDM endpoints.

### Impact

If Windows MDM is enabled, an attacker with access to any Azure AD tenant can obtain a valid Microsoft-signed token and use it to enroll unauthorized devices and interact with Fleet's MDM management APIs. During device management, Fleet may expose sensitive enrollment secrets embedded in MDM command payloads, enabling further unauthorized access.

### Workarounds

If an immediate upgrade is not possible, affected Fleet users should temporarily disable Windows MDM.

### For more information

If you have any questions or comments about this advisory:
Email us at [security@fleetdm.com](mailto:security@fleetdm.com)
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

We thank @zaddy6 for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-ffg9-j72f-j6xm
- https://nvd.nist.gov/vuln/detail/CVE-2026-24899
- https://github.com/fleetdm/fleet
- https://github.com/fleetdm/fleet/releases/tag/fleet-v4.82.0
