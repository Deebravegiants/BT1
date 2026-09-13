# [H] @alizeait/unflatto Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-q8jq-4rm5-4hm5
CVE: CVE-2024-38988
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:N/E:P (CVSS_V4)
Published: 2025-04-01
Source: https://github.com/advisories/GHSA-q8jq-4rm5-4hm5
Type: github-advisory

## Affected
- npm: `@alizeait/unflatto` — affected >=0 <1.0.3

## Details
### Impact
alizeait unflatto <= 1.0.2 was discovered to contain a prototype pollution via the method exports.unflatto at /dist/index.js. This vulnerability allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties.

### Patches
The problem has been patched in 1.0.3


### References
https://github.com/advisories/GHSA-799q-f2px-wx8c

## References
- https://github.com/alizeait/unflatto/security/advisories/GHSA-q8jq-4rm5-4hm5
- https://nvd.nist.gov/vuln/detail/CVE-2024-38988
- https://github.com/alizeait/unflatto/issues/32
- https://github.com/alizeait/unflatto/commit/3c1b120f1dcd44eefe07d4a5022e1baa3c7164d3
- https://gist.github.com/mestrtee/4c5dfb66bea377889c44dd6c8af28713
- https://github.com/alizeait/unflatto
