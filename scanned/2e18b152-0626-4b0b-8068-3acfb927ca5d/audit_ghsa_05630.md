# [H] Next.js HTTP request deserialization can lead to DoS when using insecure React Server Components

## Summary
Severity: High
Advisory: GHSA-h25m-26qc-wcjf
CWE: CWE-400, CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-h25m-26qc-wcjf
Type: github-advisory

## Affected
- npm: `next` — affected >=13.0.0 <15.0.8
- npm: `next` — affected >=15.1.1-canary.0 <15.1.12
- npm: `next` — affected >=15.2.0-canary.0 <15.2.9
- npm: `next` — affected >=15.3.0-canary.0 <15.3.9
- npm: `next` — affected >=15.4.0-canary.0 <15.4.11
- npm: `next` — affected >=15.5.1-canary.0 <15.5.10
- npm: `next` — affected >=15.6.0-canary.0 <15.6.0-canary.61
- npm: `next` — affected >=16.0.0-beta.0 <16.0.11
- npm: `next` — affected >=16.1.0-canary.0 <16.1.5

## Details
A vulnerability affects certain React Server Components packages for versions 19.0.x, 19.1.x, and 19.2.x and frameworks that use the affected packages, including Next.js 13.x, 14.x, 15.x, and 16.x using the App Router. The issue is tracked upstream as [CVE-2026-23864](https://github.com/facebook/react/security/advisories/GHSA-83fc-fqcc-2hmg).

A specially crafted HTTP request can be sent to any App Router Server Function endpoint that, when deserialized, may trigger excessive CPU usage, out-of-memory exceptions, or server crashes. This can result in denial of service in unpatched environments.

## References
- https://github.com/facebook/react/security/advisories/GHSA-83fc-fqcc-2hmg
- https://github.com/vercel/next.js/security/advisories/GHSA-h25m-26qc-wcjf
- https://nvd.nist.gov/vuln/detail/CVE-2026-23864
- https://github.com/vercel/next.js
- https://vercel.com/changelog/summary-of-cve-2026-23864
