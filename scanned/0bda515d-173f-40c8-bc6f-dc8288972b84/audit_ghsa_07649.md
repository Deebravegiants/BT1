# [M]  Memory exhaustion in SvelteKit remote form deserialization (experimental only)

## Summary
Severity: Medium
Advisory: GHSA-vrhm-gvg7-fpcf
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-vrhm-gvg7-fpcf
Type: github-advisory

## Affected
- npm: `@sveltejs/kit` — affected >=2.49.0 <2.52.2

## Details
Versions of `@sveltejs/kit` prior to 2.52.2 with remote functions enabled can be vulnerable to memory exhaustion. Malformed form data can cause the server process to crash due to excessive memory allocation, resulting in denial of service.

Only applications using both `experimental.remoteFunctions` and `form` are vulnerable.

## References
- https://github.com/sveltejs/kit/security/advisories/GHSA-vrhm-gvg7-fpcf
- https://github.com/sveltejs/kit/commit/f47c01bd8100328c24fdb8522fe35913b0735f35
- https://github.com/sveltejs/kit
- https://github.com/sveltejs/kit/releases/tag/@sveltejs/kit@2.52.2
