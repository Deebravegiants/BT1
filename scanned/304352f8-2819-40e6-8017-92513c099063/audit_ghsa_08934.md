# [H] Next.js has a Middleware / Proxy bypass in App Router applications via segment-prefetch routes

## Summary
Severity: High
Advisory: GHSA-267c-6grr-h53f
CVE: CVE-2026-44575
CWE: CWE-288
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-267c-6grr-h53f
Type: github-advisory

## Affected
- npm: `next` — affected >=15.2.0 <15.5.16
- npm: `next` — affected >=16.0.0 <16.2.5

## Details
### Impact

App Router applications that rely on middleware or proxy-based checks for authorization can allow unauthorized access through transport-specific route variants used for segment prefetching. In affected configurations, specially crafted `.rsc` and segment-prefetch URLs can resolve to the same page without being matched by the intended middleware rule, which can allow protected content to be reached without the expected authorization check.

### Fix

We now include App Router transport variants when generating middleware matchers, so middleware protections are applied consistently to those requests as well as to the normal page URL.

### Workarounds

If you cannot upgrade immediately, enforce authorization in the underlying route or page logic instead of relying solely on middleware.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-267c-6grr-h53f
- https://nvd.nist.gov/vuln/detail/CVE-2026-44575
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.16
- https://github.com/vercel/next.js/releases/tag/v16.2.5
