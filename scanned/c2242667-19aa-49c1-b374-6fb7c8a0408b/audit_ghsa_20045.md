# [M] jsonwebtoken's insecure implementation of key retrieval function could lead to Forgeable Public/Private Tokens from RSA to HMAC

## Summary
Severity: Medium
Advisory: GHSA-hjrf-2m68-5959
CVE: CVE-2022-23541
CWE: CWE-1259, CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-12-22
Source: https://github.com/advisories/GHSA-hjrf-2m68-5959
Type: github-advisory

## Affected
- npm: `jsonwebtoken` — affected >=0 <9.0.0

## Details
# Overview

Versions `<=8.5.1` of `jsonwebtoken` library can be misconfigured so that passing a poorly implemented key retrieval function (referring to the `secretOrPublicKey` argument from the [readme link](https://github.com/auth0/node-jsonwebtoken#jwtverifytoken-secretorpublickey-options-callback)) will result in incorrect verification of tokens. There is a possibility of using a different algorithm and key combination in verification  than the one that was used to sign the tokens. Specifically, tokens signed with an asymmetric public key could be verified with a symmetric HS256 algorithm. This can lead to successful validation of forged tokens. 

# Am I affected?

You will be affected if your application is supporting usage of both symmetric key and asymmetric key in jwt.verify() implementation with the same key retrieval function. 

# How do I fix it?
 
Update to version 9.0.0.

# Will the fix impact my users?

There is no impact for end users

## References
- https://github.com/auth0/node-jsonwebtoken/security/advisories/GHSA-hjrf-2m68-5959
- https://nvd.nist.gov/vuln/detail/CVE-2022-23541
- https://github.com/auth0/node-jsonwebtoken/commit/e1fa9dcc12054a8681db4e6373da1b30cf7016e3
- https://github.com/auth0/node-jsonwebtoken
- https://github.com/auth0/node-jsonwebtoken/releases/tag/v9.0.0
- https://security.netapp.com/advisory/ntap-20240621-0007
