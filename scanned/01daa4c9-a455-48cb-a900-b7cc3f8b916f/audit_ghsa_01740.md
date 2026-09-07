# [H] Information disclosure through error object in auth0.js

## Summary
Severity: High
Advisory: GHSA-prfq-f66g-43mp
CVE: CVE-2020-5263
CWE: CWE-522
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-04-10
Source: https://github.com/advisories/GHSA-prfq-f66g-43mp
Type: github-advisory

## Affected
- npm: `auth0-js` — affected >=8.0.0 <9.13.2

## Details
## Overview
Between versions 8.0.0 and  9.13.1(inclusive), in the case of an (authentication) error, the error object returned by the library contains the original request of the user, which may include the plaintext password the user entered. 

If the error object is exposed or logged without modification, the application risks password exposure.

## Am I affected?
You are affected by this vulnerability if all of the following conditions apply:

- You are using Auth0.js version between 8.0.0 and 9.13.1(inclusive).
- You store or display error objects without filtering. 

## How to fix that?
Developers should upgrade auth0.js to version 9.13.2 or later where user inputted passwords are masked in errors. If upgrading is not possible, a temporary fix may include not storing the error object or displaying it publicly without modification.

## Will this update impact my users?

This fix patches the Auth0.js and may require changes in application code due to password no longer available in error object, but it will not impact your users, their current state, or any existing sessions.

## References
- https://github.com/auth0/auth0.js/security/advisories/GHSA-prfq-f66g-43mp
- https://nvd.nist.gov/vuln/detail/CVE-2020-5263
- https://github.com/auth0/auth0.js/commit/355ca749b229fb93142f0b3978399b248d710828
