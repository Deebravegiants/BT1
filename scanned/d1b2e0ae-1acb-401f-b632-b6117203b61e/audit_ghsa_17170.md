# [H] Content-Security-Policy header generation in middleware could be compromised by malicious injections

## Summary
Severity: High
Advisory: GHSA-w387-5qqw-7g8m
CVE: CVE-2024-29896
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-03-29
Source: https://github.com/advisories/GHSA-w387-5qqw-7g8m
Type: github-advisory

## Affected
- npm: `@kindspells/astro-shield` — affected >=1.2.0 <1.3.0

## Details
### Impact

When the following conditions are met:
- Automated CSP headers generation for SSR content is enabled
- The web application serves content that can be partially controlled by external users

Then it is possible that the CSP headers generation feature might be "allow-listing" malicious injected resources like inlined JS, or references to external malicious scripts.

### Patches
Available in version 1.3.0 .

### Workarounds
- Do not enable CSP headers generation.
- Use it only for dynamically generated content that cannot be controlled by external users in any way.

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/KindSpells/astro-shield/security/advisories/GHSA-w387-5qqw-7g8m
- https://nvd.nist.gov/vuln/detail/CVE-2024-29896
- https://github.com/KindSpells/astro-shield/commit/41b84576d37fa486a57005ea297658d0bc38566d
- https://github.com/KindSpells/astro-shield/commit/ad3abf5577bae9be420b7ddf376337a5b8817869
- https://github.com/KindSpells/astro-shield
- https://github.com/KindSpells/astro-shield/compare/1.2.0...1.3.0
