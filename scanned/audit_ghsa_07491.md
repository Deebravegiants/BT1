# [H] Next.js: Denial of Service in App Router using Server Actions

## Summary
Severity: High
Advisory: GHSA-m99w-x7hq-7vfj
CVE: CVE-2026-64641
CWE: CWE-834
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-m99w-x7hq-7vfj
Type: github-advisory

## Affected
- npm: `next` — affected >=13.0.0 <15.5.21
- npm: `next` — affected >=16.0.0 <16.2.11

## Details
## Impact

Crafted requests targeting Next.js applications using App Router with at least one Server Action can lead to excessive CPU usage blocking processing of further requests in the same process.

## Workarounds

No workaround exists besides upgrading. Applications using Pages Router or not using Server Actions are not vulnerable.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-m99w-x7hq-7vfj
- https://github.com/vercel/next.js/pull/96013
- https://github.com/vercel/next.js/commit/019628571641dec57aaf349ba0c360e3964e6f12
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.21
- https://github.com/vercel/next.js/releases/tag/v16.2.11
