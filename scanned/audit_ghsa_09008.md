# [M] Svelte: ReDoS in `<svelte:element>` Tag Validation

## Summary
Severity: Medium
Advisory: GHSA-9rmh-mm8f-r9h6
CVE: CVE-2026-42567
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-9rmh-mm8f-r9h6
Type: github-advisory

## Affected
- npm: `svelte` — affected >=5.51.5 <5.55.7

## Details
An internal regex in the Svelte runtime can take exponential time to test in `<svelte:element this={tag}></svelte:element>`. You are only vulnerable to this if you allow tags of unconstrained length. If your application only allows a predetermined list of tags or trims their length before passing them to `svelte:element`, you are safe.

## References
- https://github.com/sveltejs/svelte/security/advisories/GHSA-9rmh-mm8f-r9h6
- https://nvd.nist.gov/vuln/detail/CVE-2026-42567
- https://github.com/sveltejs/svelte
- https://github.com/sveltejs/svelte/releases/tag/svelte%405.55.7
