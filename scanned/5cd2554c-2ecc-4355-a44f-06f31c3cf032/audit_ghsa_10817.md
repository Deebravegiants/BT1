# [C] Parse Server: JWT audience validation bypass in Google, Apple, and Facebook authentication adapters

## Summary
Severity: Critical
Advisory: GHSA-x6fw-778m-wr9v
CVE: CVE-2026-30863
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-x6fw-778m-wr9v
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.5.0-alpha.11
- npm: `parse-server` — affected >=0 <8.6.10

## Details
### Impact

The Google, Apple, and Facebook authentication adapters use JWT verification to validate identity tokens. When the adapter's audience configuration option is not set (`clientId` for Google/Apple, `appIds` for Facebook), JWT verification silently skips audience claim validation. This allows an attacker to use a validly signed JWT issued for a different application to authenticate as any user on the target Parse Server.

- For Google and Apple, the vulnerability is exploitable when the server does not configure `clientId`. The adapters accepted this as valid and simply skipped audience validation.
- For Facebook Limited Login, the vulnerability exists regardless of configuration. The adapter validated `appIds` only for Standard Login (Graph API), but the Limited Login JWT path never passed `appIds` as the audience to JWT verification.

### Patches

The fix enforces `clientId` (Google/Apple) and `appIds` (Facebook) as mandatory and passes them to JWT verification for audience validation. While this is technically a breaking change for servers that omit these options, it is not a breaking change as per documentation — all three options are documented as required configuration.

### Workarounds

- Google / Apple: Ensure `clientId` is set in the adapter configuration. When set, JWT verification correctly validates the audience claim even on unpatched versions.
- Facebook Limited Login: There is no workaround. The unpatched adapter does not pass `appIds` to JWT audience validation, so the only mitigation is to upgrade.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-x6fw-778m-wr9v
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.0-alpha.11
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.10

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-x6fw-778m-wr9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-30863
- https://github.com/parse-community/parse-server
