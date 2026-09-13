# [M] @backstage/plugin-auth-backend: OAuth redirect URI allowlist bypass

## Summary
Severity: Medium
Advisory: GHSA-wqvh-63mv-9w92
CVE: CVE-2026-32235
CWE: CWE-20, CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-wqvh-63mv-9w92
Type: github-advisory

## Affected
- npm: `@backstage/plugin-auth-backend` — affected >=0 <0.27.1

## Details
### Impact

The experimental OIDC provider in `@backstage/plugin-auth-backend` is vulnerable to a redirect URI allowlist bypass. Instances that have enabled experimental Dynamic Client Registration or Client ID Metadata Documents and configured `allowedRedirectUriPatterns` are affected.

A specially crafted redirect URI can pass the allowlist validation while resolving to an attacker-controlled host. If a victim approves the resulting OAuth consent request, their authorization code is sent to the attacker, who can exchange it for a valid access token.

This requires victim interaction and that one of the experimental features is explicitly enabled, which is not the default.

### Patches

Upgrade to `@backstage/plugin-auth-backend` version 0.27.1 or later.

### Workarounds

Disable experimental Dynamic Client Registration and Client ID Metadata Documents features if they are not required.

### References

- [RFC 6749 Section 3.1.2 - Redirection Endpoint](https://datatracker.ietf.org/doc/html/rfc6749#section-3.1.2)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-wqvh-63mv-9w92
- https://nvd.nist.gov/vuln/detail/CVE-2026-32235
- https://github.com/backstage/backstage/commit/6042dd0c7f0706e0f473dafa92799ecf19c825ec
- https://github.com/backstage/backstage
