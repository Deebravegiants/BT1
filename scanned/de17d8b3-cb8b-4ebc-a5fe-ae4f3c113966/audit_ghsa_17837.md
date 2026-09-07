# [M] Cross Site Scripting vulnerability in store2

## Summary
Severity: Medium
Advisory: GHSA-w5hq-hm5m-4548
CVE: CVE-2024-57556
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-24
Source: https://github.com/advisories/GHSA-w5hq-hm5m-4548
Type: github-advisory

## Affected
- npm: `store2` — affected >=0 <2.14.4

## Details
Cross Site Scripting vulnerability in nbubna store v.2.14.2 and before allows a remote attacker to execute arbitrary code via the store.deep.js component

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57556
- https://github.com/nbubna/store/issues/127
- https://github.com/nbubna/store/pull/128
- https://github.com/nbubna/store
