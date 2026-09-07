# [M] Directus has open redirect in SAML

## Summary
Severity: Medium
Advisory: GHSA-3573-4c68-g8cc
CVE: CVE-2026-22032
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-01-06
Source: https://github.com/advisories/GHSA-3573-4c68-g8cc
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.14.0
- npm: `@directus/api` — affected >=0 <32.1.1

## Details
## Security Advisory: Open Redirect in Directus SAML Authentication

### Summary

An open redirect vulnerability exists in the Directus SAML authentication callback endpoint. The `RelayState` parameter is used in redirects without proper validation against an allowlist of permitted domains.

### Vulnerability Description

During SAML authentication, the `RelayState` parameter is intended to preserve the user's original destination. However, while the login initiation flow validates redirect targets against allowed domains, this validation is not applied to the callback endpoint. This allows an attacker to craft a malicious authentication request that redirects users to an arbitrary external URL upon completion.

The vulnerability is present in both the success and error handling paths of the callback.

### Impact

- **Phishing**: Users can be redirected to attacker-controlled sites that mimic legitimate login pages
- **Credential theft**: Chained attacks may leverage the redirect to capture OAuth tokens or authorization codes
- **Trust erosion**: Users may lose confidence in the application's security posture

This vulnerability can be exploited without authentication.

## References
- https://github.com/directus/directus/security/advisories/GHSA-3573-4c68-g8cc
- https://nvd.nist.gov/vuln/detail/CVE-2026-22032
- https://github.com/directus/directus/commit/dad9576ea9362905cc4de8028d3877caff36dc23
- https://github.com/directus/directus
