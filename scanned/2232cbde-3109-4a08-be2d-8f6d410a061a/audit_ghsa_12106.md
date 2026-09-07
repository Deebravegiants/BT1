# [M] Fleet's user account creation via invite does not enforce invited email address

## Summary
Severity: Medium
Advisory: GHSA-4f9r-x588-pp2h
CVE: CVE-2026-34389
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-4f9r-x588-pp2h
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.81.0

## Details
### Summary

Fleet contained an issue in the user invitation flow where the email address provided during invite acceptance was not validated against the email address associated with the invite. An attacker who obtained a valid invite token could create an account under an arbitrary email address while inheriting the role granted by the invite, including global admin.

### Impact

If an attacker gains access to a valid invite token, they can create a Fleet user account with an email address of their choosing while inheriting the invite’s assigned role and team memberships.

This issue:

- Requires possession of a valid invite token
- Does not bypass authentication controls beyond invite-based account creation
- Does not expose data without successful account creation

### Workarounds

If upgrading immediately is not possible:

- Treat invite links as sensitive credentials and avoid sharing them in public or semi-public channels (e.g., Slack, Teams).
- Revoke and reissue invites if there is any concern that an invite link may have been exposed.
- Prefer issuing invites with the minimum required privileges and elevating roles after account creation when appropriate.

### For more information

If there are any questions or comments about this advisory:

Send an email to [security@fleetdm.com](mailto:security@fleetdm.com)

### Credits

Fleet thanks @fuzzztf for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-4f9r-x588-pp2h
- https://nvd.nist.gov/vuln/detail/CVE-2026-34389
- https://github.com/fleetdm/fleet
