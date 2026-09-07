# [C] @clerk/nextjs auth() and getAuth() methods vulnerable to insecure direct object reference (IDOR) 

## Summary
Severity: Critical
Advisory: GHSA-q6w5-jg5q-47vg
CVE: CVE-2024-22206
CWE: CWE-284, CWE-287, CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-12
Source: https://github.com/advisories/GHSA-q6w5-jg5q-47vg
Type: github-advisory

## Affected
- npm: `@clerk/nextjs` — affected >=4.7.0 <4.29.3

## Details
### Impact
Unauthorized access or privilege escalation due to a logic flaw in `auth()` in the App Router or `getAuth()` in the Pages Router.

### Affected Versions
All applications that that use `@clerk/nextjs` versions in the range of `>= 4.7.0`,`< 4.29.3` in a Next.js backend to authenticate API Routes, App Router, or Route handlers. Specifically, those that call `auth()` in the App Router or `getAuth()` in the Pages Router. Only the `@clerk/nextjs` SDK is impacted. Other SDKs, including other Javascript-based SDKs, are not impacted.

### Patches
Fix included in `@clerk/nextjs@4.29.3`.

### References
- https://clerk.com/changelog/2024-01-12
- https://github.com/clerk/javascript/releases/tag/%40clerk%2Fnextjs%404.29.3

## References
- https://github.com/clerk/javascript/security/advisories/GHSA-q6w5-jg5q-47vg
- https://nvd.nist.gov/vuln/detail/CVE-2024-22206
- https://clerk.com/changelog/2024-01-12
- https://github.com/clerk/javascript
- https://github.com/clerk/javascript/releases/tag/%40clerk%2Fnextjs%404.29.3
