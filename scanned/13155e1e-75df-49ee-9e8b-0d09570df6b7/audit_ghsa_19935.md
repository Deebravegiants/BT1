# [H] jsonwebtoken unrestricted key type could lead to legacy keys usage 

## Summary
Severity: High
Advisory: GHSA-8cf7-32gw-wr33
CVE: CVE-2022-23539
CWE: CWE-327
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-12-22
Source: https://github.com/advisories/GHSA-8cf7-32gw-wr33
Type: github-advisory

## Affected
- npm: `jsonwebtoken` — affected >=0 <9.0.0

## Details
# Overview

Versions `<=8.5.1` of `jsonwebtoken` library could be misconfigured so that legacy, insecure key types are used for signature verification. For example, DSA keys could be used with the RS256 algorithm. 

# Am I affected?

You are affected if you are using an algorithm and a key type other than the combinations mentioned below

| Key type |  algorithm                                    |
|----------|------------------------------------------|
| ec           | ES256, ES384, ES512                      |
| rsa          | RS256, RS384, RS512, PS256, PS384, PS512 |
| rsa-pss  | PS256, PS384, PS512                      |

And for Elliptic Curve algorithms:

| `alg` | Curve      |
|-------|------------|
| ES256 | prime256v1 |
| ES384 | secp384r1  |
| ES512 | secp521r1  |

# How do I fix it?

Update to version 9.0.0. This version validates for asymmetric key type and algorithm combinations. Please refer to the above mentioned algorithm / key type combinations for the valid secure configuration. After updating to version 9.0.0, If you still intend to continue with signing or verifying tokens using invalid key type/algorithm value combinations, you’ll need to set the `allowInvalidAsymmetricKeyTypes` option to `true` in the `sign()` and/or `verify()` functions.

# Will the fix impact my users?

There will be no impact, if you update to version 9.0.0 and you already use a valid secure combination of key type and algorithm. Otherwise,  use the  `allowInvalidAsymmetricKeyTypes` option  to `true` in the `sign()` and `verify()` functions to continue usage of invalid key type/algorithm combination in 9.0.0 for legacy compatibility.

## References
- https://github.com/auth0/node-jsonwebtoken/security/advisories/GHSA-8cf7-32gw-wr33
- https://nvd.nist.gov/vuln/detail/CVE-2022-23539
- https://github.com/auth0/node-jsonwebtoken/commit/e1fa9dcc12054a8681db4e6373da1b30cf7016e3
- https://github.com/auth0/node-jsonwebtoken
- https://security.netapp.com/advisory/ntap-20240621-0007
