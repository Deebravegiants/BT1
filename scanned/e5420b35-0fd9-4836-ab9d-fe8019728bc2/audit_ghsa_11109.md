# [M] Parse Server OAuth2 adapter app ID validation sends wrong token to introspection endpoint

## Summary
Severity: Medium
Advisory: GHSA-69xg-f649-w5g2
CVE: CVE-2026-32269
CWE: CWE-683
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-69xg-f649-w5g2
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.13
- npm: `parse-server` — affected >=8.0.2 <8.6.39

## Details
### Impact

The OAuth2 authentication adapter does not correctly validate app IDs when `appidField` and `appIds` are configured. During app ID validation, a malformed value is sent to the token introspection endpoint instead of the user's actual access token. Depending on the introspection endpoint's behavior, this could either cause all OAuth2 logins to fail, or allow authentication from disallowed app contexts if the endpoint returns valid-looking data for the malformed request.

Deployments using the OAuth2 adapter with `appidField` and `appIds` configured are affected.

### Patches

The fix corrects the parameter alignment in the OAuth2 adapter's app ID validation method to match the expected interface, ensuring the correct access token is sent to the introspection endpoint.

### Workarounds

There is no known workaround.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-69xg-f649-w5g2
- Fix in Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.13
- Fix in Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.39

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-69xg-f649-w5g2
- https://nvd.nist.gov/vuln/detail/CVE-2026-32269
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.39
- https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.13
