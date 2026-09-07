# [M] Next.js vulnerable to cross-site scripting in App Router applications using CSP nonces

## Summary
Severity: Medium
Advisory: GHSA-ffhc-5mcf-pf4q
CVE: CVE-2026-44581
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-ffhc-5mcf-pf4q
Type: github-advisory

## Affected
- npm: `next` — affected >=13.4.0 <15.5.16
- npm: `next` — affected >=16.0.0 <16.2.5

## Details
### Impact

App Router applications that rely on CSP nonces can be vulnerable to stored cross-site scripting when deployed behind shared caches. In affected versions, malformed nonce values derived from request headers could be reflected into rendered HTML in an unsafe way, allowing an attacker to poison cached responses and cause script execution for later visitors.

### Fix

We now reject or ignore malformed nonce values before they are embedded into HTML and apply stricter nonce sanitization so request-derived nonce data cannot break out of the intended attribute context.

### Workarounds

If you cannot upgrade immediately, strip inbound `Content-Security-Policy` request headers from untrusted traffic.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-ffhc-5mcf-pf4q
- https://nvd.nist.gov/vuln/detail/CVE-2026-44581
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.16
- https://github.com/vercel/next.js/releases/tag/v16.2.5
