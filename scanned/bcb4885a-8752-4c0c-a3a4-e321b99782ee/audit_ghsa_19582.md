# [H] Remix and React Router allow URL manipulation via Host / X-Forwarded-Host headers

## Summary
Severity: High
Advisory: GHSA-4q56-crqp-v477
CVE: CVE-2025-31137
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-01
Source: https://github.com/advisories/GHSA-4q56-crqp-v477
Type: github-advisory

## Affected
- npm: `@react-router/express` — affected >=7.0.0 <7.4.1
- npm: `@remix-run/express` — affected >=2.11.1 <2.16.3

## Details
### Impact

We received a report about a vulnerability in Remix/React Router that affects all Remix 2 and React Router 7 consumers using the Express adapter. Basically, this vulnerability allows anyone to spoof the URL used in an incoming `Request` by putting a URL pathname in the port section of a URL that is part of a `Host` or `X-Forwarded-Host` header sent to a Remix/React Router request handler.

### Patches

This issue has been patched and released in Remix 2.16.3 React Router 7.4.1.

### Credits

- Rachid Allam (zhero;)
- Yasser Allam (inzo_)

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-4q56-crqp-v477
- https://nvd.nist.gov/vuln/detail/CVE-2025-31137
- https://github.com/remix-run/react-router
