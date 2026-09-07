# [M] blinksocks has weak encryption algorithms

## Summary
Severity: Medium
Advisory: GHSA-pqj5-37xf-x5gc
CVE: CVE-2023-50481
Ecosystem: npm
Published: 2023-12-21
Source: https://github.com/advisories/GHSA-pqj5-37xf-x5gc
Type: github-advisory

## Affected
- npm: `blinksocks` — affected >=0

## Details
An issue was discovered in blinksocks version 3.3.8, allows remote attackers to obtain sensitive information via weak encryption algorithms in the component `/presets/ssr-auth-chain.js`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50481
- https://github.com/blinksocks/blinksocks/issues/108
- https://github.com/blinksocks/blinksocks
- https://github.com/tianjk99/Cryptographic-Misuses/blob/main/CVE-2023-50481.md
