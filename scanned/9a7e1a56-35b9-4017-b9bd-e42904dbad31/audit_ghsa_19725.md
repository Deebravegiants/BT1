# [H] Redoc Prototype Pollution via `Module.mergeObjects` Component

## Summary
Severity: High
Advisory: GHSA-9rhg-254w-fh9x
CVE: CVE-2024-57083
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-03-28
Source: https://github.com/advisories/GHSA-9rhg-254w-fh9x
Type: github-advisory

## Affected
- npm: `redoc` — affected >=0 <2.4.0

## Details
A prototype pollution in the component Module.mergeObjects (redoc/bundles/redoc.lib.js:2) of redoc <= 2.2.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57083
- https://github.com/Redocly/redoc/issues/2499
- https://github.com/Redocly/redoc/pull/2638
- https://github.com/Redocly/redoc
