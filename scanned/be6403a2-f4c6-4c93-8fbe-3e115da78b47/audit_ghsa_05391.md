# [M] Next.js has Unbounded Memory Consumption via PPR Resume Endpoint 

## Summary
Severity: Medium
Advisory: GHSA-5f7q-jpqc-wp7h
CVE: CVE-2025-59472
CWE: CWE-400, CWE-409, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-5f7q-jpqc-wp7h
Type: github-advisory

## Affected
- npm: `next` — affected >=16.0.0-beta.0 <16.1.5
- npm: `next` — affected >=15.0.0-canary.0
- npm: `next` — affected >=15.0.1-canary.0
- npm: `next` — affected >=15.0.2-canary.0
- npm: `next` — affected >=15.0.3-canary.0
- npm: `next` — affected >=15.0.4-canary.0
- npm: `next` — affected >=15.1.1-canary.0
- npm: `next` — affected >=15.2.0-canary.0
- npm: `next` — affected >=15.2.1-canary.0
- npm: `next` — affected >=15.2.2-canary.0
- npm: `next` — affected >=15.3.0-canary.0
- npm: `next` — affected >=15.3.1-canary.0
- npm: `next` — affected >=15.4.0-canary.0
- npm: `next` — affected >=15.4.2-canary.0
- npm: `next` — affected >=15.5.1-canary.0
- npm: `next` — affected >=15.6.0-canary.0 <15.6.0-canary.61

## Details
A denial of service vulnerability exists in Next.js versions with Partial Prerendering (PPR) enabled when running in minimal mode. The PPR resume endpoint accepts unauthenticated POST requests with the `Next-Resume: 1` header and processes attacker-controlled postponed state data. Two closely related vulnerabilities allow an attacker to crash the server process through memory exhaustion:

1. **Unbounded request body buffering**: The server buffers the entire POST request body into memory using `Buffer.concat()` without enforcing any size limit, allowing arbitrarily large payloads to exhaust available memory.

2. **Unbounded decompression (zipbomb)**: The resume data cache is decompressed using `inflateSync()` without limiting the decompressed output size. A small compressed payload can expand to hundreds of megabytes or gigabytes, causing memory exhaustion.

Both attack vectors result in a fatal V8 out-of-memory error (`FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory`) causing the Node.js process to terminate. The zipbomb variant is particularly dangerous as it can bypass reverse proxy request size limits while still causing large memory allocation on the server.

To be affected, an application must run with `experimental.ppr: true` or `cacheComponents: true` configured along with the NEXT_PRIVATE_MINIMAL_MODE=1 environment variable.

Strongly consider upgrading to 15.6.0-canary.61 or 16.1.5 to reduce risk and prevent availability issues in Next applications.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-5f7q-jpqc-wp7h
- https://nvd.nist.gov/vuln/detail/CVE-2025-59472
- https://github.com/vercel/next.js
- https://vercel.com/changelog/summaries-of-cve-2025-59471-and-cve-2025-59472
