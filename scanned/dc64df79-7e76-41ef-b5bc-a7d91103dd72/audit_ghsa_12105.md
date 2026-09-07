# [H] Parse Server OAuth2 authentication adapter account takeover via identity spoofing

## Summary
Severity: High
Advisory: GHSA-fr88-w35c-r596
CVE: CVE-2026-30967
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-fr88-w35c-r596
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.5.2-alpha.9
- npm: `parse-server` — affected >=0 <8.6.22

## Details
### Impact

The OAuth2 authentication adapter, when configured without the `useridField` option, only verifies that a token is active via the provider's token introspection endpoint, but does not verify that the token belongs to the user identified by `authData.id`. An attacker with any valid OAuth2 token from the same provider can authenticate as any other user.

This affects any Parse Server deployment that uses the generic OAuth2 authentication adapter (configured with `oauth2: true`) without setting the `useridField` option.

### Patches

The vulnerability is fixed by defaulting `useridField` to `sub`, which is the standard subject identifier field defined by [RFC 7662](https://datatracker.ietf.org/doc/html/rfc7662). The adapter now always validates the token's identity against the claimed user ID, even when `useridField` is not explicitly configured.

### Workarounds

Set the `useridField` option to the appropriate field name for your OAuth2 provider (e.g. `sub`) in the Parse Server authentication configuration.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-fr88-w35c-r596
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.9
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.22

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-fr88-w35c-r596
- https://nvd.nist.gov/vuln/detail/CVE-2026-30967
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.22
- https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.9
