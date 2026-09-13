# [H] SAML authentication vulnerability due to stdlib XML parsing

## Summary
Severity: High
Advisory: GHSA-w3wf-cfx3-6gcx
CVE: CVE-2020-26276
CWE: CWE-290
Ecosystem: Go
Published: 2022-02-11
Source: https://github.com/advisories/GHSA-w3wf-cfx3-6gcx
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <3.5.1

## Details
### Impact
Due to issues in Go's standard library XML parsing, a valid SAML response may be mutated by an attacker to modify the trusted document. This can result in allowing unverified logins from a SAML IdP.

Users that configure Fleet with SSO login may be vulnerable to this issue.

### Patches
This issue is patched in 3.5.1 using https://github.com/mattermost/xml-roundtrip-validator.

### Workarounds
If upgrade to 3.5.1 is not possible, users should disable SSO authentication in Fleet.

### References
See https://mattermost.com/blog/coordinated-disclosure-go-xml-vulnerabilities/ for more information about the underlying vulnerabilities.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@fleetdm.com](mailto:security@fleetdm.com)
* Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-w3wf-cfx3-6gcx
- https://nvd.nist.gov/vuln/detail/CVE-2020-26276
- https://github.com/fleetdm/fleet/commit/57812a532e5f749c8e18c6f6a652eca65c083607
- https://github.com/fleetdm/fleet/blob/master/CHANGELOG.md#fleet-351-dec-14-2020
- https://github.com/mattermost/xml-roundtrip-validator
- https://mattermost.com/blog/coordinated-disclosure-go-xml-vulnerabilities
