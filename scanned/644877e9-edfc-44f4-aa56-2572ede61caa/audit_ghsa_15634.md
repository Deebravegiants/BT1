# [M] Pomerium exposed OAuth2 access and ID tokens in user info endpoint response

## Summary
Severity: Medium
Advisory: GHSA-rrqr-7w59-637v
CVE: CVE-2024-39315
CWE: CWE-201
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-05
Source: https://github.com/advisories/GHSA-rrqr-7w59-637v
Type: github-advisory

## Affected
- Go: `github.com/pomerium/pomerium` — affected >=0 <0.26.1

## Details
### Impact

The Pomerium user info page (at `/.pomerium`) unintentionally included serialized OAuth2 access and ID tokens from the logged-in user's session. These tokens are not intended to be exposed to end users.

This issue may be more severe in the presence of an XSS vulnerability in an upstream application proxied through Pomerium. If an attacker could insert a malicious script onto a web page proxied through Pomerium, that script could access these tokens by making a request to the `/.pomerium` endpoint.

Upstream applications that authenticate only the ID token may be vulnerable to user impersonation using a token obtained in this manner.

Note that an OAuth2 access token or ID token by itself is not sufficient to hijack a user's Pomerium session. Upstream applications should not be vulnerable to user impersonation via these tokens provided:
- the application verifies the [Pomerium JWT](https://www.pomerium.com/docs/capabilities/getting-users-identity) for each request,
- the connection between Pomerium and the application is secured by mTLS,
- or the connection between Pomerium and the application is otherwise secured at the network layer.

### Patches
Patched in Pomerium v0.26.1.

### Workarounds
None

### For more information
If you have any questions or comments about this advisory:

- Open an issue in [pomerium/pomerium](https://github.com/pomerium/pomerium/issues)
- Email us at [security@pomerium.com](mailto:security@pomerium.com)

Credit to Vadim Sheydaev, aka Enr1g for reporting this issue.

## References
- https://github.com/pomerium/pomerium/security/advisories/GHSA-rrqr-7w59-637v
- https://nvd.nist.gov/vuln/detail/CVE-2024-39315
- https://github.com/pomerium/pomerium/commit/4c7c4320afb2ced70ba19b46de1ac4383f3daa48
- https://github.com/pomerium/pomerium
