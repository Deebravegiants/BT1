# [M] @grackle-ai/server has Missing Content-Security-Policy and X-Frame-Options Headers

## Summary
Severity: Medium
Advisory: GHSA-3mjm-x6gw-2x42
CWE: CWE-693, CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-3mjm-x6gw-2x42
Type: github-advisory

## Affected
- npm: `@grackle-ai/server` — affected >=0 <0.70.4

## Details
### Impact

The HTTP server does not set `Content-Security-Policy`, `X-Frame-Options`, or `X-Content-Type-Options` headers on any response. This reduces defense-in-depth against XSS, clickjacking, and MIME-sniffing attacks.

While the current XSS attack surface is small (React-markdown is configured safely, no `dangerouslySetInnerHTML`, Vite does not generate source maps), the absence of these headers means any future XSS vulnerability would have no secondary defense layer.

**Affected code:**
- `packages/server/src/index.ts` — all `res.writeHead()` calls only set `Content-Type`, with no security headers

### Patches

0.70.4

**Fix:** Add security headers to all HTML/API responses:
```typescript
res.writeHead(200, {
  "Content-Type": contentType,
  "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:",
  "X-Frame-Options": "DENY",
  "X-Content-Type-Options": "nosniff"
});
```

### Workarounds

Use a reverse proxy (nginx, Caddy) in front of the Grackle server to inject security headers.

### References

- CWE-693: Protection Mechanism Failure
- OWASP: HTTP Security Response Headers
- File: `packages/server/src/index.ts`

## References
- https://github.com/nick-pape/grackle/security/advisories/GHSA-3mjm-x6gw-2x42
- https://github.com/nick-pape/grackle
