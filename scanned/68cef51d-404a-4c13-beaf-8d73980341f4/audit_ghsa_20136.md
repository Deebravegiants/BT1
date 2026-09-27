# [M] jsonwebtoken vulnerable to signature validation bypass due to insecure default algorithm in jwt.verify()

## Summary
Severity: Medium
Advisory: GHSA-qwph-4952-7xr6
CVE: CVE-2022-23540
CWE: CWE-287, CWE-327, CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2022-12-22
Source: https://github.com/advisories/GHSA-qwph-4952-7xr6
Type: github-advisory

## Affected
- npm: `jsonwebtoken` — affected >=0 <9.0.0

## Details
# Overview

In versions <=8.5.1 of jsonwebtoken library, lack of algorithm definition and a falsy secret or key in the `jwt.verify()` function can lead to signature validation bypass due to defaulting to the `none` algorithm for signature verification.

# Am I affected?
You will be affected if all the following are true in the `jwt.verify()` function:
- a token with no signature is received
- no algorithms are specified 
- a falsy (e.g. null, false, undefined) secret or key is passed 

# How do I fix it?
 
Update to version 9.0.0 which removes the default support for the none algorithm in the `jwt.verify()` method. 

# Will the fix impact my users?

There will be no impact, if you update to version 9.0.0 and you don’t need to allow for the `none` algorithm. If you need 'none' algorithm, you have to explicitly specify that in `jwt.verify()` options.

## References
- https://github.com/auth0/node-jsonwebtoken/security/advisories/GHSA-qwph-4952-7xr6
- https://nvd.nist.gov/vuln/detail/CVE-2022-23540
- https://github.com/auth0/node-jsonwebtoken/commit/e1fa9dcc12054a8681db4e6373da1b30cf7016e3
- https://github.com/auth0/node-jsonwebtoken
- https://security.netapp.com/advisory/ntap-20240621-0007
