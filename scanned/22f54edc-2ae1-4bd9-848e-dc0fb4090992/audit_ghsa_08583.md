# [M] Svelte: SSR XSS via Insecure Promise Serialization in hydratable

## Summary
Severity: Medium
Advisory: GHSA-f3cj-j4f6-wq85
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-f3cj-j4f6-wq85
Type: github-advisory

## Affected
- npm: `svelte` — affected >=5.46.0 <5.55.7

## Details
Contents of `hydratable` promises were not properly stringified, potentially leading to an XSS exploit. You are vulnerable if all of the following is true:
- you are using `hydratable` (an experimental feature at the time of this report)
- you are passing attacker-controlled input such that a synchronous value is hydrated, then a promise value, e.g. `hydratable('someKey', () => [synchronousValue, promiseValue])`

## References
- https://github.com/sveltejs/svelte/security/advisories/GHSA-f3cj-j4f6-wq85
- https://github.com/sveltejs/svelte/commit/a16ebc67bbcf8f708360195687e1b2719463e1a4
- https://github.com/sveltejs/svelte
- http://github.com/sveltejs/svelte/releases/tag/svelte%405.55.7
