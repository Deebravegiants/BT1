# [M] Cache poisoning in @sveltejs/adapter-vercel

## Summary
Severity: Medium
Advisory: GHSA-9pq4-5hcf-288c
CVE: CVE-2026-27118
CWE: CWE-346
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-9pq4-5hcf-288c
Type: github-advisory

## Affected
- npm: `@sveltejs/adapter-vercel` — affected >=0 <6.3.2

## Details
Versions of `@sveltejs/adapter-vercel` prior to 6.3.2 are vulnerable to cache poisoning. An internal query parameter intended for Incremental Static Regeneration (ISR) is accessible on all routes, allowing an attacker to cause sensitive user-specific responses to be cached and served to other users.

Successful exploitation requires a victim to visit an attacker-controlled link while authenticated.

Existing deployments are protected by Vercel's WAF, but users should upgrade as soon as possible.

## References
- https://github.com/sveltejs/kit/security/advisories/GHSA-9pq4-5hcf-288c
- https://nvd.nist.gov/vuln/detail/CVE-2026-27118
- https://github.com/sveltejs/kit
