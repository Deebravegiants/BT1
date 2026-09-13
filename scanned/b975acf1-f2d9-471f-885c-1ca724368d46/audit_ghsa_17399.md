# [H] auth0/node-jws Improperly Verifies HMAC Signature

## Summary
Severity: High
Advisory: GHSA-869p-cjfg-cm3x
CVE: CVE-2025-65945
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-12-04
Source: https://github.com/advisories/GHSA-869p-cjfg-cm3x
Type: github-advisory

## Affected
- npm: `jws` — affected >=0 <3.2.3
- npm: `jws` — affected >=4.0.0 <4.0.1

## Details
### Overview
An improper signature verification vulnerability exists when using auth0/node-jws with the HS256 algorithm under specific conditions.

### Am I Affected?
You are affected by this vulnerability if you meet all of the following preconditions:

1. Application uses the auth0/node-jws implementation of JSON Web Signatures, versions <=3.2.2 || 4.0.0
2. Application uses the jws.createVerify() function for HMAC algorithms
3. Application uses user-provided data from the JSON Web Signature Protected Header or Payload in the HMAC secret lookup routines

You are NOT affected by this vulnerability if you meet any of the following preconditions:
1. Application uses the jws.verify() interface (note: `auth0/node-jsonwebtoken` users fall into this category and are therefore NOT affected by this vulnerability)
2. Application uses only asymmetric algorithms (e.g. RS256)
3. Application doesn’t use user-provided data from the JSON Web Signature Protected Header or Payload in the HMAC secret lookup routines

### Fix
Upgrade auth0/node-jws version to version 3.2.3 or 4.0.1

### Acknowledgement
Okta would like to thank Félix Charette for discovering this vulnerability.

## References
- https://github.com/auth0/node-jws/security/advisories/GHSA-869p-cjfg-cm3x
- https://nvd.nist.gov/vuln/detail/CVE-2025-65945
- https://github.com/auth0/node-jws/commit/34c45b2c04434f925b638de6a061de9339c0ea2e
- https://github.com/auth0/node-jws/commit/4f6e73f24df42f07d632dec6431ade8eda8d11a6
- https://github.com/auth0/node-jws
- https://github.com/auth0/node-jws/releases/tag/v3.2.3
- https://github.com/auth0/node-jws/releases/tag/v4.0.1
