# [M] Next.js Allows a Denial of Service (DoS) with Server Actions

## Summary
Severity: Medium
Advisory: GHSA-7m27-7ghc-44w9
CVE: CVE-2024-56332
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-01-03
Source: https://github.com/advisories/GHSA-7m27-7ghc-44w9
Type: github-advisory

## Affected
- npm: `next` — affected >=13.0.0 <13.5.8
- npm: `next` — affected >=14.0.0 <14.2.21
- npm: `next` — affected >=15.0.0 <15.1.2

## Details
### Impact
A Denial of Service (DoS) attack allows attackers to construct requests that leaves requests to Server Actions hanging until the hosting provider cancels the function execution.

_Note: Next.js server is idle during that time and only keeps the connection open. CPU and memory footprint are low during that time._

Deployments without any protection against long running Server Action invocations are especially vulnerable. Hosting providers like Vercel or Netlify set a default maximum duration on function execution to reduce the risk of excessive billing.

This is the same issue as if the incoming HTTP request has an invalid `Content-Length` header or never closes. If the host has no other mitigations to those then this vulnerability is novel.

This vulnerability affects only Next.js deployments using Server Actions.

### Patches

This vulnerability was resolved in Next.js 14.2.21, 15.1.2, and 13.5.8. We recommend that users upgrade to a safe version.

### Workarounds

There are no official workarounds for this vulnerability.

### Credits

Thanks to the PackDraw team for responsibly disclosing this vulnerability.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-7m27-7ghc-44w9
- https://nvd.nist.gov/vuln/detail/CVE-2024-56332
- https://github.com/vercel/next.js
