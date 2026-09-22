# [C] billboard.js allows prototype pollution via the function generate

## Summary
Severity: Critical
Advisory: GHSA-65p9-j6pg-72hj
CVE: CVE-2025-49223
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-04
Source: https://github.com/advisories/GHSA-65p9-j6pg-72hj
Type: github-advisory

## Affected
- npm: `billboard.js` — affected >=0 <3.15.1

## Details
billboard.js before 3.15.1 was discovered to contain a prototype pollution via the function generate, which could allow attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49223
- https://github.com/naver/billboard.js/commit/82ea7ac4f5720d6a7f0c2fa5a5dad51a549667bb
- https://cve.naver.com/detail/cve-2025-49223.html
- https://github.com/louay-075/CVE-2025-49223-BillboardJS-PoC
- https://github.com/naver/billboard.js
- https://github.com/naver/billboard.js/blob/938f263feca453fba5a4dc48d86b32cc5b509443/src/core.ts#L95
