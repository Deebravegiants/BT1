# [M] OIDC claims not updated from Identity Provider in Pomerium

## Summary
Severity: Medium
Advisory: GHSA-j6wp-3859-vxfg
CVE: CVE-2021-41230
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-j6wp-3859-vxfg
Type: github-advisory

## Affected
- Go: `github.com/pomerium/pomerium` — affected >=0.14.0 <0.15.6

## Details
### Impact
Changes to the OIDC claims of a user after initial login are not reflected in policy evaluation when using [`allowed_idp_claims`](https://www.pomerium.com/reference/#allowed-idp-claims) as part of policy.  If using `allowed_idp_claims` and a user's claims are changed, Pomerium can make incorrect authorization decisions.

### Patches
v0.15.6

### Workarounds
- Clear data on `databroker` service by clearing redis or restarting the in-memory databroker to force claims to be updated

### References
https://github.com/pomerium/pomerium/pull/2724

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Pomerium](https://github.com/pomerium/pomerium)
* Email us at [security@pomerium.com](mailto:security@pomerium.com)

## References
- https://github.com/pomerium/pomerium/security/advisories/GHSA-j6wp-3859-vxfg
- https://nvd.nist.gov/vuln/detail/CVE-2021-41230
- https://github.com/pomerium/pomerium/pull/2724
- https://github.com/pomerium/pomerium/commit/f20542c4bf2cc691e4c324f7ec79e02e46d95511
- https://github.com/pomerium/pomerium
- https://pkg.go.dev/vuln/GO-2021-0258
