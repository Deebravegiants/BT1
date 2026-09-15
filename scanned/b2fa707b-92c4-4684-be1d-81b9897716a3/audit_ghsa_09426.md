# [H] Auth.js SDK has Improper Permission Checking

## Summary
Severity: High
Advisory: GHSA-8qjv-jj2q-x832
CVE: CVE-2026-42280
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-8qjv-jj2q-x832
Type: github-advisory

## Affected
- npm: `auth0-js` — affected >=8.11.0 <10.0.0

## Details
### Description
Under specific preconditions, the Auth0.js SDK may improperly return user profile information using a valid access token when a specifically crafted invalid ID token is provided.

### Am I Affected?
Users are affected if they meet each of the following preconditions:
- Applications built using Auth0.js version between 8.11.0 and 9.32.0
- The application’s access control relies on rules defined in Auth0 Actions.


### Affected product and versions
auth0.js SDK v8.11.0 to v9.32.0

### Resolution
Upgrade auth0/auth0.js to v10.0.0 or greater.

### Acknowledgements
Okta would like to thank Quan Le (@aleister1102) for their discovery and responsible disclosure.

## References
- https://github.com/auth0/auth0.js/security/advisories/GHSA-8qjv-jj2q-x832
- https://nvd.nist.gov/vuln/detail/CVE-2026-42280
- https://github.com/auth0/auth0.js
