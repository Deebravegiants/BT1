# [H] Authorization header is not sanitized in an error object in auth0

## Summary
Severity: High
Advisory: GHSA-5jpf-pj32-xx53
CVE: CVE-2020-15125
CWE: CWE-209
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-07-29
Source: https://github.com/advisories/GHSA-5jpf-pj32-xx53
Type: github-advisory

## Affected
- npm: `auth0` — affected >=0 <2.27.1

## Details
### Overview
Versions before and including `2.27.0` use a block list of specific keys that should be sanitized from the request object contained in the error object.  When a request to Auth0 management API fails, the key for `Authorization` header is not sanitized and the `Authorization` header value can be logged exposing a bearer token.

### Am I affected?
You are affected by this vulnerability if all of the following conditions apply:

- You are using `auth0` npm package
- You are using a Machine to Machine application authorized to use Auth0's management API https://auth0.com/docs/flows/concepts/client-credentials

### How to fix that?
Upgrade to version `2.27.1`

### Will this update impact my users?
The fix provided in patch will not affect your users.

### Credit
http://github.com/osdiab

## References
- https://github.com/auth0/node-auth0/security/advisories/GHSA-5jpf-pj32-xx53
- https://nvd.nist.gov/vuln/detail/CVE-2020-15125
- https://github.com/auth0/node-auth0/pull/507
- https://github.com/auth0/node-auth0/pull/507/commits/62ca61b3348ec8e74d7d00358661af1a8bc98a3c
- https://github.com/auth0/node-auth0/tree/v2.27.1
