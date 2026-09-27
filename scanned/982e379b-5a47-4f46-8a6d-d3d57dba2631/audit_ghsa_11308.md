# [H] Parse Server crash via deeply nested query condition operators

## Summary
Severity: High
Advisory: GHSA-9xp9-j92r-p88v
CVE: CVE-2026-32944
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-9xp9-j92r-p88v
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.21
- npm: `parse-server` — affected >=0 <8.6.45

## Details
### Impact

An unauthenticated attacker can crash the Parse Server process by sending a single request with deeply nested query condition operators. This terminates the server and denies service to all connected clients.

### Patches

A depth limit for query condition operator nesting has been added via the `requestComplexity.queryDepth` server option. The option is disabled by default to avoid a breaking change. To mitigate, upgrade and set the option to a value appropriate for your app.

### Workarounds

None.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-9xp9-j92r-p88v
- https://nvd.nist.gov/vuln/detail/CVE-2026-32944
- https://github.com/parse-community/parse-server/pull/10202
- https://github.com/parse-community/parse-server/pull/10203
- https://github.com/parse-community/parse-server
