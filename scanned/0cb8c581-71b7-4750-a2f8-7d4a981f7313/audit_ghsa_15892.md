# [M] Express ressource injection

## Summary
Severity: Medium
Advisory: GHSA-cm5g-3pgc-8rg4
CVE: CVE-2024-10491
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-29
Source: https://github.com/advisories/GHSA-cm5g-3pgc-8rg4
Type: github-advisory

## Affected
- npm: `express` — affected >=0 <4.0.0-rc1

## Details
A vulnerability has been identified in the Express response.links function, allowing for arbitrary resource injection in the Link header when unsanitized data is used.

The issue arises from improper sanitization in `Link` header values, which can allow a combination of characters like `,`, `;`, and `<>` to preload malicious resources.

This vulnerability is especially relevant for dynamic parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10491
- https://github.com/expressjs/express/issues/6222
- https://github.com/expressjs/express
- https://www.herodevs.com/vulnerability-directory/cve-2024-10491
