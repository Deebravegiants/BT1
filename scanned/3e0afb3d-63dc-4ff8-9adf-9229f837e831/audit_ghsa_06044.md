# [M] SvelteKit: ReDoS (O(n^2)) in content negotiation — unauthenticated DoS via the Accept header

## Summary
Severity: Medium
Advisory: GHSA-29g2-3rmr-qm68
CVE: CVE-2026-66062
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-29g2-3rmr-qm68
Type: github-advisory

## Affected
- npm: `@sveltejs/kit` — affected >=0 <2.70.2

## Details
### Impact
SvelteKit is vulnerable to remote CPU-exhaustion DoS attacks via specifically-crafted `Accept` headers. The impact is mitigated by default header length limits on most platforms, but in the case of raised or absent limits a denial of service is possible.

### Patches
The vulnerability is patched in `@sveltejs/kit` version 2.70.2.

## References
- https://github.com/sveltejs/kit/security/advisories/GHSA-29g2-3rmr-qm68
- https://github.com/sveltejs/kit/commit/82712fc02c24b1dcf5b25d7a52129cd8455f04f5
- https://github.com/sveltejs/kit
- https://github.com/sveltejs/kit/releases/tag/@sveltejs/kit@2.70.2
