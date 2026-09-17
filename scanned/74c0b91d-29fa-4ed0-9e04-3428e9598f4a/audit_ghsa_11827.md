# [H] Parse Server missing audience validation in Keycloak authentication adapter

## Summary
Severity: High
Advisory: GHSA-48mh-j4p5-7j9v
CVE: CVE-2026-30949
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-48mh-j4p5-7j9v
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.5.2-alpha.5
- npm: `parse-server` — affected >=0 <8.6.18

## Details
### Impact

The Keycloak authentication adapter does not validate the `azp` (authorized party) claim of Keycloak access tokens against the configured `client-id`. A valid access token issued by the same Keycloak realm for a *different* client application can be used to authenticate as any user on the Parse Server that uses the Keycloak adapter. This enables cross-application account takeover in multi-client Keycloak realms.

All Parse Server deployments that use the Keycloak authentication adapter with a Keycloak realm that has multiple client applications are affected.

### Patches

The fix replaces the userinfo HTTP call with local JWT verification and enforces `azp` claim validation against the configured `client-id`.

### Workarounds

None.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-48mh-j4p5-7j9v
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.5
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.18

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-48mh-j4p5-7j9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-30949
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.18
- https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.5
