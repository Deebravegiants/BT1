# [M] Fleet: Password reset tokens remain valid after password change for 24 hours

## Summary
Severity: Medium
Advisory: GHSA-3458-r943-hmx4
CVE: CVE-2026-26060
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-3458-r943-hmx4
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.43.5-0.20260113202849-bbc1aef2987d

## Details
### Summary

A vulnerability in Fleet’s password management logic could allow previously issued password reset tokens to remain valid after a user changes their password. As a result, a stale password reset token could be reused to reset the account password even after a defensive password change.

### Impact

If an attacker had prior access to a valid password reset token, they could reuse that token within its validity window to reset the user’s password after the user has already changed it. This could result in temporary account takeover.

Exploitation requires prior compromise of a password reset token and is further constrained by the token’s 24-hour expiration period. The issue does not allow discovery of reset tokens, does not bypass authentication on its own, and does not affect accounts without an existing valid reset token.

### Workarounds

Until patched, users who believe a password reset token may have been exposed should wait for the token to expire before reusing the account, or contact a Fleet administrator to invalidate active sessions.

### For more information

If there are any questions or comments about this advisory:

Email Fleet at [security@fleetdm.com](mailto:security@fleetdm.com)  
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

Fleet thanks @fuzzztf for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-3458-r943-hmx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-26060
- https://github.com/fleetdm/fleet
