# [M] Next.js: Unbounded postponed resume buffering can lead to DoS

## Summary
Severity: Medium
Advisory: GHSA-h27x-g6w4-24gq
CVE: CVE-2026-27979
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-h27x-g6w4-24gq
Type: github-advisory

## Affected
- npm: `next` — affected >=16.0.1 <16.1.7

## Details
## Summary
A request containing the `next-resume: 1` header (corresponding with a PPR resume request) would buffer request bodies without consistently enforcing `maxPostponedStateSize` in certain setups. The previous mitigation protected minimal-mode deployments, but equivalent non-minimal deployments remained vulnerable to the same unbounded postponed resume-body buffering behavior.

## Impact
In applications using the App Router with Partial Prerendering capability enabled (via `experimental.ppr` or `cacheComponents`), an attacker could send oversized `next-resume` POST payloads that were buffered without consistent size enforcement in non-minimal deployments, causing excessive memory usage and potential denial of service.

## Patches
Fixed by enforcing size limits across all postponed-body buffering paths and erroring when limits are exceeded.  

## Workarounds
If upgrade is not immediately possible:
- Block requests containing the `next-resume` header, as this is never valid to be sent from an untrusted client.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-h27x-g6w4-24gq
- https://nvd.nist.gov/vuln/detail/CVE-2026-27979
- https://github.com/vercel/next.js/commit/c885d4825f800dd1e49ead37274dcd08cdd6f3f1
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v16.1.7
