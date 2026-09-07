# [C] Parse Server's OAuth2 adapter shares mutable state across providers via singleton instance

## Summary
Severity: Critical
Advisory: GHSA-2cjm-2gwv-m892
CVE: CVE-2026-32242
CWE: CWE-362
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-2cjm-2gwv-m892
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.11
- npm: `parse-server` — affected >=0 <8.6.37

## Details
### Impact

Parse Server's built-in OAuth2 auth adapter exports a singleton instance that is reused directly across all OAuth2 provider configurations. Under concurrent authentication requests for different OAuth2 providers, one provider's token validation may execute using another provider's configuration, potentially allowing a token that should be rejected by one provider to be accepted because it is validated against a different provider's policy.

Deployments that configure multiple OAuth2 providers via the `oauth2: true` flag are affected.

### Patches

The fix ensures that a new adapter instance is created for each provider instead of reusing the singleton, so each provider's configuration is isolated.

### Workarounds

There is no known workaround. If only a single OAuth2 provider is configured, the race condition cannot occur.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-2cjm-2gwv-m892
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.11
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.37

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-2cjm-2gwv-m892
- https://nvd.nist.gov/vuln/detail/CVE-2026-32242
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.37
- https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.11
