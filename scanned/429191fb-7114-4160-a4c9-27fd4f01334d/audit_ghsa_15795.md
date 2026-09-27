# [H] robinweser fast-loops vulnerable to prototype pollution

## Summary
Severity: High
Advisory: GHSA-3q56-9cc2-46j4
CVE: CVE-2024-39008
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-3q56-9cc2-46j4
Type: github-advisory

## Affected
- npm: `fast-loops` — affected >=0 <1.1.4

## Details
robinweser fast-loops v1.1.3 was discovered to contain a prototype pollution via the function `objectMergeDeep`. This vulnerability allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39008
- https://github.com/robinweser/fast-loops/commit/6743acf64af832b7a0bbecf95cb4c7d95a3b766e
- https://gist.github.com/mestrtee/f09a507c8d59fbbb7fd40880cd9b87ed
- https://github.com/robinweser/fast-loops
