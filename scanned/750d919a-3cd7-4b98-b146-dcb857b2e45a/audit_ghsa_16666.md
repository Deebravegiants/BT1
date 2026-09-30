# [H] Next.js Vulnerable to HTTP Request Smuggling

## Summary
Severity: High
Advisory: GHSA-77r5-gw3j-2mpf
CVE: CVE-2024-34350
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2024-05-09
Source: https://github.com/advisories/GHSA-77r5-gw3j-2mpf
Type: github-advisory

## Affected
- npm: `next` — affected >=13.4.0 <13.5.1

## Details
### Impact
Inconsistent interpretation of a crafted HTTP request meant that requests are treated as both a single request, and two separate requests by Next.js, leading to desynchronized responses. This led to a response queue poisoning vulnerability in the affected Next.js versions.

For a request to be exploitable, the affected route also had to be making use of the [rewrites](https://nextjs.org/docs/app/api-reference/next-config-js/rewrites) feature in Next.js.

### Patches
The vulnerability is resolved in Next.js `13.5.1` and newer. This includes Next.js `14.x`.

### Workarounds
There are no official workarounds for this vulnerability. We recommend that you upgrade to a safe version.

### References
https://portswigger.net/web-security/request-smuggling/advanced/response-queue-poisoning

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-77r5-gw3j-2mpf
- https://nvd.nist.gov/vuln/detail/CVE-2024-34350
- https://github.com/vercel/next.js/commit/44eba020c615f0d9efe431f84ada67b81576f3f5
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/compare/v13.5.0...v13.5.1
