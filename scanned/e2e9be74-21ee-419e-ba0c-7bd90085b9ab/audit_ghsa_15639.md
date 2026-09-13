# [H] Next.js Denial of Service (DoS) condition

## Summary
Severity: High
Advisory: GHSA-fq54-2j52-jc42
CVE: CVE-2024-39693
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-fq54-2j52-jc42
Type: github-advisory

## Affected
- npm: `next` — affected >=13.3.1 <13.5.0

## Details
### Impact
A Denial of Service (DoS) condition was identified in Next.js. Exploitation of the bug can trigger a crash, affecting the availability of the server.

**This vulnerability can affect all Next.js deployments on the affected versions.**

### Patches
This vulnerability was resolved in Next.js 13.5 and later. We recommend that users upgrade to a safe version.

### Workarounds
There are no official workarounds for this vulnerability.

#### Credit
* Thai Vu of [flyseccorp.com](http://flyseccorp.com/)
* Aonan Guan (@0dd), Senior Cloud Security Engineer

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-fq54-2j52-jc42
- https://nvd.nist.gov/vuln/detail/CVE-2024-39693
- https://github.com/vercel/next.js
