# [H] Next has a Denial of Service with Server Components - Incomplete Fix Follow-Up

## Summary
Severity: High
Advisory: GHSA-5j59-xgg2-r9c4
CWE: CWE-1395, CWE-400, CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-5j59-xgg2-r9c4
Type: github-advisory

## Affected
- npm: `next` — affected >=13.3.1-canary.0 <14.2.35
- npm: `next` — affected >=15.0.6 <15.0.7
- npm: `next` — affected >=15.1.10 <15.1.11
- npm: `next` — affected >=15.2.7 <15.2.8
- npm: `next` — affected >=15.3.7 <15.3.8
- npm: `next` — affected >=15.4.9 <15.4.10
- npm: `next` — affected >=15.5.8 <15.5.9
- npm: `next` — affected >=15.6.0-canary.59 <15.6.0-canary.60
- npm: `next` — affected >=16.0.9 <16.0.10
- npm: `next` — affected >=16.1.0-canary.17 <16.1.0-canary.19

## Details
It was discovered that the fix for [CVE-2025-55184](https://github.com/advisories/GHSA-2m3v-v2m8-q956) in React Server Components was incomplete and did not fully mitigate denial-of-service conditions across all payload types.  As a result, certain crafted inputs could still trigger excessive resource consumption. 

This vulnerability affects React versions 19.0.2, 19.1.3, and 19.2.2, as well as frameworks that bundle or depend on these versions, including Next.js 13.x, 14.x, 15.x, and 16.x when using the App Router. The issue is tracked upstream as [CVE-2025-67779](https://www.cve.org/CVERecord?id=CVE-2025-67779).

A malicious actor can send a specially crafted HTTP request to a Server Function endpoint that, when deserialized, causes the React Server Components runtime to enter an infinite loop. This can lead to sustained CPU consumption and cause the affected server process to become unresponsive, resulting in a denial-of-service condition in unpatched environments.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-5j59-xgg2-r9c4
- https://nvd.nist.gov/vuln/detail/CVE-2025-67779
- https://github.com/vercel/next.js
- https://nextjs.org/blog/security-update-2025-12-11
- https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components
- https://www.cve.org/CVERecord?id=CVE-2025-55184
- https://www.facebook.com/security/advisories/cve-2025-67779
