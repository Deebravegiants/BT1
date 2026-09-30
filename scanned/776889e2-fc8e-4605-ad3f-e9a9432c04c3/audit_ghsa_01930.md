# [H] Incorrect Authorization in ORY Oathkeeper

## Summary
Severity: High
Advisory: GHSA-vfvf-6gx5-mqv6
CVE: CVE-2021-32701
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-24
Source: https://github.com/advisories/GHSA-vfvf-6gx5-mqv6
Type: github-advisory

## Affected
- Go: `github.com/ory/oathkeeper` — affected >=0.38.0-beta.2 <0.38.12-beta.1

## Details
ORY Oathkeeper is an Identity & Access Proxy (IAP) and Access Control Decision API that authorizes HTTP requests based on sets of Access Rules. When you make a request to an endpoint that requires the scope `foo` using an access token granted with that `foo` scope, introspection will be valid and that token will be cached. The problem comes when a second requests to an endpoint that requires the scope `bar` is made before the cache has expired. Whether the token is granted or not to the `bar` scope, introspection will be valid. A patch will be released with `v0.38.12-beta.1`. Per default, caching is disabled for the `oauth2_introspection` authenticator. When caching is disabled, this vulnerability does not exist. The cache is checked in [`func (a *AuthenticatorOAuth2Introspection) Authenticate(...)`](https://github.com/ory/oathkeeper/blob/6a31df1c3779425e05db1c2a381166b087cb29a4/pipeline/authn/authenticator_oauth2_introspection.go#L152). From [`tokenFromCache()`](https://github.com/ory/oathkeeper/blob/6a31df1c3779425e05db1c2a381166b087cb29a4/pipeline/authn/authenticator_oauth2_introspection.go#L97) it seems that it only validates the token expiration date, but ignores whether the token has or not the proper scopes. The vulnerability was introduced in PR #424. During review, we failed to require appropriate test coverage by the submitter which is the primary reason that the vulnerability passed the review process.

## References
- https://github.com/ory/oathkeeper/security/advisories/GHSA-qvp4-rpmr-xwrr
- https://nvd.nist.gov/vuln/detail/CVE-2021-32701
- https://github.com/ory/oathkeeper/pull/424
- https://github.com/ory/oathkeeper/commit/1f9f625c1a49e134ae2299ee95b8cf158feec932
