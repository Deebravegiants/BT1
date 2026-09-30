# [H] Strapi Server-Side Request Forgery (SSRF)

## Summary
Severity: High
Advisory: GHSA-p9ff-j98v-p435
CVE: CVE-2024-37818
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-20
Source: https://github.com/advisories/GHSA-p9ff-j98v-p435
Type: github-advisory

## Affected
- npm: `@strapi/strapi` — affected 4.24.4

## Details
Strapi v4.24.4 was discovered to contain a Server-Side Request Forgery (SSRF) via the component /strapi.io/_next/image. This vulnerability allows attackers to scan for open ports or access sensitive information via a crafted GET request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37818
- https://github.com/strapi/strapi
- https://medium.com/%40barkadevaibhav491/server-side-request-forgery-in-strapi-e02d5fe218ab
- https://strapi.io
