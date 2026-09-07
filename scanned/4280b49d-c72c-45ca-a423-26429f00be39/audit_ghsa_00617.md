# [C] Exposure of Sensitive information in authentikat-jwt

## Summary
Severity: Critical
Advisory: GHSA-3rhm-67j6-42jq
CVE: CVE-2017-18239
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-3rhm-67j6-42jq
Type: github-advisory

## Affected
- Maven: `com.jason-goodwin:authentikat-jwt_2.12` — affected >=0 <0.4.6

## Details
A time-sensitive equality check on the JWT signature in the JsonWebToken.validate method in main/scala/authentikat/jwt/JsonWebToken.scala in authentikat-jwt (aka com.jason-goodwin/authentikat-jwt) version 0.4.5 and earlier allows the supplier of a JWT token to guess bit after bit of the signature by repeating validation requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18239
- https://github.com/jasongoodwin/authentikat-jwt/issues/12
- https://github.com/jasongoodwin/authentikat-jwt/pull/36
- https://github.com/jasongoodwin/authentikat-jwt/commit/2d2fa0d40ac8f2f7aa7e9b070fa1a25eee082cb0
- https://github.com/advisories/GHSA-3rhm-67j6-42jq
- https://github.com/jasongoodwin/authentikat-jwt
