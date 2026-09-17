# [M] Zitadel is missing enforcement of organization scopes

## Summary
Severity: Medium
Advisory: GHSA-g2pf-ww5m-2r9m
CVE: CVE-2026-33132
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-g2pf-ww5m-2r9m
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=4.0.0-rc.1 <4.12.3
- Go: `github.com/zitadel/zitadel` — affected >=3.0.0-rc.1 <3.4.9
- Go: `github.com/zitadel/zitadel` — affected >=0 <1.80.0-v2.20.0.20260317120401-d90285929ca0

## Details
### Summary

A vulnerability in Zitadel's OAuth2/OIDC interface, which allowed users to bypass organization enforcement during authentication.

### Impact

Zitadel allows applications to enforce an organzation context during authentication using [scopes](https://zitadel.com/docs/apis/openidoauth/scopes#reserved-scopes) (`urn:zitadel:iam:org:id:{id}` and `urn:zitadel:iam:org:domain:primary:{domainname}`). If enforced, a user needs to be part of the required organization to sign in.

While this was properly enforced for OAuth2/OIDC authorization requests in login V1, corresponding controls were missing for device authorization requests and all login V2 and OIDC API V2 endpoints.
This allowed users to bypass the restriction and sign in with users from other organizations.

Note that this enforcement allows for an additional check during authentication and applications relying on authorizations / roles assignments are not affected by this bypass.

### Affected Versions

Systems running one of the following versions are affected:
- **4.x**: `4.0.0` through `4.12.2` (including RC versions)
- **3.x**: `3.0.0` through `3.4.8` (including RC versions)

### Patches

The vulnerability has been addressed in the latest releases. The patch resolves the issue by validating the provided scopes and enforcing the organization existence when processing the authorization request. Additionally it will prevent the use of a session of a user which does not belong to the required organization on the OIDC service endpoints ([CreateCallback](https://zitadel.com/docs/reference/api/oidc/zitadel.oidc.v2.OIDCService.CreateCallback) and [Authorize or Deny Device Authorization](https://zitadel.com/docs/reference/api/oidc/zitadel.oidc.v2.OIDCService.AuthorizeOrDenyDeviceAuthorization) endpoints).

4.x: Upgrade to >=[4.12.3](https://github.com/zitadel/zitadel/releases/tag/v4.12.3)
3.x: Update to >=[3.4.9](https://github.com/zitadel/zitadel/releases/tag/v3.4.9)

### Workarounds

The recommended solution is to upgrade to a patched version. 

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

### Credits

Thanks to @motoki317 for reporting this vulnerability.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-g2pf-ww5m-2r9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-33132
- https://github.com/zitadel/zitadel/commit/d90285929ca019fa817f31551fd0883429dda2a8
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v3.4.9
- https://github.com/zitadel/zitadel/releases/tag/v4.12.3
