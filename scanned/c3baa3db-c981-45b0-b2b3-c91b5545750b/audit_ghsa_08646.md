# [H] Next.js vulnerable to Denial of Service via connection exhaustion in applications using Cache Components

## Summary
Severity: High
Advisory: GHSA-mg66-mrh9-m8jx
CVE: CVE-2026-44579
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-mg66-mrh9-m8jx
Type: github-advisory

## Affected
- npm: `next` — affected >=15.0.0 <15.5.16
- npm: `next` — affected >=16.0.0 <16.2.5

## Details
### Impact

Applications using Partial Prerendering through the Cache Components feature can be vulnerable to connection exhaustion through crafted POST requests to a server action. In affected configurations, a malicious request can trigger a request-body handling deadlock that leaves connections open for an extended period, consuming file descriptors and server capacity until legitimate users are denied service.

### Fix

We now treat the header used for resuming Partial Prerendered requests as an internal-only header and strip it from untrusted incoming requests. This header should never be accepted directly from external clients.

### Workarounds

If you cannot upgrade immediately, block requests that would be handled by Next.js if they contain the `Next-Resume` header at the edge.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-mg66-mrh9-m8jx
- https://nvd.nist.gov/vuln/detail/CVE-2026-44579
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.16
- https://github.com/vercel/next.js/releases/tag/v16.2.5
