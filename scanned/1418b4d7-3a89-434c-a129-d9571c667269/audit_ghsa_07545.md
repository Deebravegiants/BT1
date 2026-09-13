# [H] Next.js: Server-Side Request Forgery in Server Actions on custom servers

## Summary
Severity: High
Advisory: GHSA-89xv-2m56-2m9x
CVE: CVE-2026-64649
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-89xv-2m56-2m9x
Type: github-advisory

## Affected
- npm: `next` — affected >=14.1.1 <15.5.21
- npm: `next` — affected >=16.0.0 <16.2.11

## Details
## Impact

When a Server Action forwards or redirects a request, an attacker can cause the server to send that outbound request to a malicious host (Server-Side Request Forgery). This requires the attacker's request to control Host-associated headers. In some configurations, it's also possible to obtain internal values that weaken middleware/proxy authorization.

Applications that use Server Actions are affected when the incoming host header is not fixed to a trusted value. This typically occurs on custom servers, or on deployments not behind a proxy that pins the host. Managed hosting pins the host upstream and is not affected; `next start` and standalone output do the same from version 14.2 onward.

## Workarounds

If you cannot upgrade, ensure clients do not control the host header your application receives. Pin or validate `Host` and `X-Forwarded-Host` at your edge or proxy. On version 14.2.0 and later, you can additionally set the `__NEXT_PRIVATE_ORIGIN` environment variable to your deployment's real origin:

```bash
__NEXT_PRIVATE_ORIGIN=https://www.example.com node server.js

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-89xv-2m56-2m9x
- https://github.com/vercel/next.js/commit/b51206321854193208c0805ba42acc49287f942b
- https://github.com/vercel/next.js/commit/e3e5666ccead3a15162793d697af5e48b7cc0498
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.21
- https://github.com/vercel/next.js/releases/tag/v16.2.11
