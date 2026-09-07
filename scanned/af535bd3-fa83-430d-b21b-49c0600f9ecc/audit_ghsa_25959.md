# [H] URL Redirection to Untrusted Site ('Open Redirect') in express-openid-connect

## Summary
Severity: High
Advisory: GHSA-7p99-3798-f85c
CVE: CVE-2022-24794
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2022-03-31
Source: https://github.com/advisories/GHSA-7p99-3798-f85c
Type: github-advisory

## Affected
- npm: `express-openid-connect` — affected >=0 <2.7.2

## Details
### Impact
Users of the `requiresAuth` middleware, either directly or through the default `authRequired` option, are vulnerable to an Open Redirect when the middleware is applied to a catch all route.

If all routes under `example.com` are protected with the `requiresAuth` middleware, a visit to `http://example.com//google.com` will be redirected to `google.com` after login because the original url reported by the Express framework is not properly sanitised.

### Am I affected?
You are affected by this vulnerability if you are using the `requiresAuth` middleware on a catch all route or the default `authRequired` option and `express-openid-connect` version `<=2.7.1`.

### How to fix that?
Upgrade to version `>=2.7.2`

### Will this update impact my users?
The fix provided in the patch will not affect your users.

## References
- https://github.com/auth0/express-openid-connect/security/advisories/GHSA-7p99-3798-f85c
- https://nvd.nist.gov/vuln/detail/CVE-2022-24794
- https://github.com/auth0/express-openid-connect/commit/0947b92164a2c5f661ebcc183d37e7f21de719ad
- https://github.com/auth0/express-openid-connect
