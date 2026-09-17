# [M] Strapi does not verify the access or ID tokens issued during the OAuth flow

## Summary
Severity: Medium
Advisory: GHSA-583x-23h9-f5w7
CVE: CVE-2023-22893
Ecosystem: npm
Published: 2023-04-19
Source: https://github.com/advisories/GHSA-583x-23h9-f5w7
Type: github-advisory

## Affected
- npm: `@strapi/plugin-users-permissions` — affected >=3.2.1 <4.6.0

## Details
Strapi 3.2.1 until 4.6.0 does not verify the access or ID tokens issued during the OAuth flow when the AWS Cognito login provider is used for authentication. A remote attacker could forge an ID token that is signed using the 'None' type algorithm to bypass authentication and impersonate any user that use AWS Cognito for authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22893
- https://github.com/strapi/strapi/commit/46f8f98378338f18b5c6139d0157a8f71bf4de83
- https://github.com/strapi/strapi/commit/8bbbd7383a20bb7cb163c8b462baffee559e994f
- https://github.com/strapi/strapi/commit/eeab43b57707d7ef275076d27be6eabc72bd71a7
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/blob/v4.5.6/packages/plugins/users-permissions/server/services/providers-registry.js
- https://github.com/strapi/strapi/releases
- https://strapi.io/blog/security-disclosure-of-vulnerabilities-cve
- https://www.ghostccamm.com/blog/multi_strapi_vulns
