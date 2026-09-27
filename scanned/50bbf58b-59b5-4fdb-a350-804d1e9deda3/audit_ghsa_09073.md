# [H] Next.js vulnerable to server-side request forgery in applications using WebSocket upgrades

## Summary
Severity: High
Advisory: GHSA-c4j6-fc7j-m34r
CVE: CVE-2026-44578
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-c4j6-fc7j-m34r
Type: github-advisory

## Affected
- npm: `next` — affected >=13.4.13 <15.5.16
- npm: `next` — affected >=16.0.0 <16.2.5

## Details
### Impact

Self-hosted applications using the built-in Node.js server can be vulnerable to server-side request forgery through crafted WebSocket upgrade requests. An attacker can cause the server to proxy requests to arbitrary internal or external destinations, which may expose internal services or cloud metadata endpoints. Vercel-hosted deployments are not affected.

### Fix

We now apply the same safety checks to WebSocket upgrade handling that already existed for normal HTTP requests, so upgrade requests are only proxied when routing has explicitly marked them as safe external rewrites.

### Workarounds

If you cannot upgrade immediately, do not expose the origin server directly to untrusted networks. If WebSocket upgrades are not required, block them at your reverse proxy or load balancer, and restrict origin egress to internal networks and metadata services where possible.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-c4j6-fc7j-m34r
- https://nvd.nist.gov/vuln/detail/CVE-2026-44578
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.16
- https://github.com/vercel/next.js/releases/tag/v16.2.5
