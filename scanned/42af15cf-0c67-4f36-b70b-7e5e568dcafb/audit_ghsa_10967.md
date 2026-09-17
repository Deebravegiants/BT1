# [H] Parse Server exposes auth data via verify password endpoint

## Summary
Severity: High
Advisory: GHSA-wp76-gg32-8258
CVE: CVE-2026-34215
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-wp76-gg32-8258
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.7.0-alpha.7
- npm: `parse-server` — affected >=0 <8.6.63

## Details
### Impact

The verify password endpoint returns unsanitized authentication data, including MFA TOTP secrets, recovery codes, and OAuth access tokens. An attacker who knows a user's password can extract the MFA secret to generate valid MFA codes, defeating multi-factor authentication protection.

### Patches

The verify password endpoint now sanitizes authentication data through auth adapter hooks before returning the response, consistent with login and user retrieval endpoints.

### Workarounds

There is no known workaround.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-wp76-gg32-8258
- https://nvd.nist.gov/vuln/detail/CVE-2026-34215
- https://github.com/parse-community/parse-server/pull/10278
- https://github.com/parse-community/parse-server/pull/10279
- https://github.com/parse-community/parse-server/pull/10323
- https://github.com/parse-community/parse-server/pull/10324
- https://github.com/parse-community/parse-server/commit/5b8998e6866bcf75be7b5bb625e27d23bfaf912c
- https://github.com/parse-community/parse-server/commit/770be8647424d92f5425c41fa81065ffbbb171ed
- https://github.com/parse-community/parse-server/commit/875cf10ac979bd60f70e7a0c534e2bc194d6982f
- https://github.com/parse-community/parse-server/commit/a1d4e7b12a12f16d3870dbee582a36765858e94c
- https://github.com/parse-community/parse-server
