# [M] CPU exhaustion in SvelteKit remote form deserialization (experimental only)

## Summary
Severity: Medium
Advisory: GHSA-88qp-p4qg-rqm6
CWE: CWE-843
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-88qp-p4qg-rqm6
Type: github-advisory

## Affected
- npm: `@sveltejs/kit` — affected >=2.49.0 <2.52.2

## Details
Versions of `@sveltejs/kit` prior to 2.52.2 with remote functions enabled are vulnerable to CPU exhaustion. Malformed form data can cause the server to become unresponsive while processing a request, resulting in denial of service.

Only applications using both `experimental.remoteFunctions` and `form` are vulnerable.

## References
- https://github.com/sveltejs/kit/security/advisories/GHSA-88qp-p4qg-rqm6
- https://github.com/sveltejs/kit/commit/3e607b314aec9e5f278d32847945b8b6323e1cb8
- https://github.com/sveltejs/kit
- https://github.com/sveltejs/kit/releases/tag/@sveltejs/kit@2.52.2
