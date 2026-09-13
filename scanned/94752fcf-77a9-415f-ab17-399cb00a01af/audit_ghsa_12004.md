# [H] Parse Server's Cloud function dispatch crashes server via prototype chain traversal

## Summary
Severity: High
Advisory: GHSA-4263-jgmp-7pf4
CVE: CVE-2026-32886
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-4263-jgmp-7pf4
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.24
- npm: `parse-server` — affected >=0 <8.6.47

## Details
### Impact

Remote clients can crash the Parse Server process by calling a cloud function endpoint with a crafted function name that traverses the JavaScript prototype chain of a registered cloud function handler, causing a stack overflow.

### Patches

The fix restricts property lookups during cloud function name resolution to own properties only, preventing prototype chain traversal from stored function handlers.

### Workarounds

There is no known workaround.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-4263-jgmp-7pf4
- https://nvd.nist.gov/vuln/detail/CVE-2026-32886
- https://github.com/parse-community/parse-server/pull/10210
- https://github.com/parse-community/parse-server/pull/10211
- https://github.com/parse-community/parse-server
