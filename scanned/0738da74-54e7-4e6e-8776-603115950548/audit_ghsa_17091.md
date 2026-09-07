# [M] URL Redirection to Untrusted Site in OAuth2/OpenID in directus

## Summary
Severity: Medium
Advisory: GHSA-fr3w-2p22-6w7p
CVE: CVE-2024-28239
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-12
Source: https://github.com/advisories/GHSA-fr3w-2p22-6w7p
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <10.10.0

## Details
### Summary
The authentication API has a `redirect` parameter that can be exploited as an open redirect vulnerability as the user tries to log in via the API URL https://docs.directus.io/reference/authentication.html#login-using-sso-providers /auth/login/google?redirect for example.

### Details
There's a redirect that is done after successful login via the Auth API GET request to `directus/auth/login/google?redirect=http://malicious-fishing-site.com`, which I think is here: https://github.com/directus/directus/blob/main/api/src/auth/drivers/oauth2.ts#L394. While credentials don't seem to be passed to the attacker site, the user can be phished into clicking a legitimate directus site and be taken to a malicious site made to look like a an error message "Your password needs to be updated" to phish out the current password.

### PoC
Turn on any auth provider in Directus instance. Form a link to `directus-instance/auth/login/:provider_id?redirect=http://malicious-fishing-site.com`, login and get taken to malicious-site. Tested on the `ory` OAuth2 integration.

### Impact
Users who login via OAuth2 into Directus.

## References
- https://github.com/directus/directus/security/advisories/GHSA-fr3w-2p22-6w7p
- https://nvd.nist.gov/vuln/detail/CVE-2024-28239
- https://github.com/directus/directus/commit/5477d7d61babd7ffc2f835d399bf79611b15b203
- https://docs.directus.io/reference/authentication.html#login-using-sso-providers
- https://github.com/directus/directus
