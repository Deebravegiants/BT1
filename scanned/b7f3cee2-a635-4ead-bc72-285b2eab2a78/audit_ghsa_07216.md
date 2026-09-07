# [H] Next.js: Server-Side Request Forgery in rewrites via attacker-controlled destination hostname

## Summary
Severity: High
Advisory: GHSA-p9j2-gv94-2wf4
CVE: CVE-2026-64645
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-p9j2-gv94-2wf4
Type: github-advisory

## Affected
- npm: `next` — affected >=12.0.0 <15.5.21
- npm: `next` — affected >=16.0.0 <16.2.11

## Details
## Impact

A `rewrites()` or `redirects()` rule that builds its external destination hostname from request-controlled input can be pointed at an arbitrary hostname, regardless of the rule's hostname suffix. For a rewrite, Next.js proxies the request to that arbitrary host and serves the response from the application's origin, leading to Server-Side Request forgery. A `redirects()` rule configured this way is vulnerable to an Open Redirect.

This affects any destination that puts a dynamic segment in the hostname, whether from the path:

```javascript
// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/:tenant',
        destination: 'https://:tenant.api.example.com',
      },
    ]
  },
}
```

or from a `has` capture:

```javascript
// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/',
        has: [{ type: 'query', key: 'region', value: '(?<region>.+)' }],
        destination: 'https://:region.api.example.com',
      },
    ]
  },
}
```

## Workarounds

If you cannot upgrade immediately, do not build the hostname of an external `rewrites()` or `redirects()` destination from user-controlled input. If a dynamic subdomain is required, constrain the value to hostname-safe characters:  `value: '(?<region>[a-z0-9-]+)'`.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-p9j2-gv94-2wf4
- https://github.com/vercel/next.js/commit/35f501357e9b0fe7c950b0d6aa8fcf5343f707e9
- https://github.com/vercel/next.js/commit/d3033266c6dff23f7be71e19341fe3a8c6e2c599
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.21
- https://github.com/vercel/next.js/releases/tag/v16.2.11
