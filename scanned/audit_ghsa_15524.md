# [H] Session is cached for OpenID and OAuth2 if `redirect` is not used

## Summary
Severity: High
Advisory: GHSA-cff8-x7jv-4fm8
CVE: CVE-2024-45596
CWE: CWE-384, CWE-524
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-10
Source: https://github.com/advisories/GHSA-cff8-x7jv-4fm8
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <10.13.3
- npm: `directus` — affected >=11.0.0-rc.1 <11.1.0
- npm: `@directus/api` — affected >=0 <21.0.1
- npm: `@directus/api` — affected >=22.0.0 <22.2.0

## Details
### Summary
Unauthenticated user can access credentials of last authenticated user via OpenID or OAuth2 where the authentication URL did not include `redirect` query string.

For example:
- Project is configured with OpenID or OAuth2
- Project is configured with cache enabled
- User tries to login via SSO link, but without `redirect` query string
- After successful login, credentials are cached
- If an unauthenticated user tries to login via SSO link, it will return the credentials of the other last user

The SSO link is something like `https://directus.example.com/auth/login/openid/callback`, where `openid` is the name of the OpenID provider configured in Directus

### Details
This happens because on that endpoint for both OpenId and Oauth2 Directus is using the `respond` middleware, which by default will try to cache GET requests that met some conditions. Although, those conditions do not include this scenario, when an unauthenticated request returns user credentials.
For OpenID, this can be seen here:
https://github.com/directus/directus/blob/main/api/src/auth/drivers/openid.ts#L453-L459
And for OAuth2 can be seen here
https://github.com/directus/directus/blob/main/api/src/auth/drivers/oauth2.ts#L422-L428

### PoC
- Create a new Directus project
- Set `CACHE_ENABLED` to true
- Set `CACHE_STORE` to `redis` for reliable results (if using memory with multiple nodes, it may only happen sometimes, due to cache being different for different nodes)
- Configure `REDIS` with redis string or redis host, port, user, etc.
- Set `AUTH_PROVIDERS` to `openid`
- Set `PUBLIC_URL` to the the main URL of your project . 	For example, `PUBLIC_URL: http://localhost:8055`
- Configure `AUTH_OPENID_CLIENT_ID`, `AUTH_OPENID_CLIENT_SECRET`, `AUTH_OPENID_ISSUER_URL` with proper OpenID configurations
- Be sure that on OpenID external app you have configured Redirect URI to `http://localhost:8055/auth/login/openid/callback`
- Run Directus
- Open the SSO link like `http://localhost:8055/auth/login/openid/callback`
- Do the authentication on the OpenID external webpage
- Verify that it you got redirected to a page with a JSON including `access_token` property
- Be sure all anonymous mode windows are closed
- Open an anonymous window and go to the SSO Link `http://localhost:8055/auth/login/openid/callback` and see you have the same credentials, even though you don't have any session because you are in anonymous mode

### Impact
All projects using OpenID or OAuth 2, that does not include `redirect` query string on loggin in users.

## References
- https://github.com/directus/directus/security/advisories/GHSA-cff8-x7jv-4fm8
- https://nvd.nist.gov/vuln/detail/CVE-2024-45596
- https://github.com/directus/directus/commit/4aace0bbe57232e38cd6a287ee475293e46dc91b
- https://github.com/directus/directus/commit/769fa22797bff5a9231599883b391e013f122e52
- https://github.com/directus/directus
- https://github.com/directus/directus/blob/main/api/src/auth/drivers/oauth2.ts#L422-L428
- https://github.com/directus/directus/blob/main/api/src/auth/drivers/openid.ts#L453-L459
