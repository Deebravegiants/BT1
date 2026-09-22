# [M] @cat5th/key-serializer Prototype Pollution vulnerability

## Summary
Severity: Medium
Advisory: GHSA-whpx-g542-7c7v
CVE: CVE-2024-39018
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-whpx-g542-7c7v
Type: github-advisory

## Affected
- npm: `@cat5th/key-serializer` — affected >=0

## Details
harvey-woo cat5th/key-serializer v0.2.5 was discovered to contain a prototype pollution via the function "query". This vulnerability allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39018
- https://gist.github.com/mestrtee/be75c60307b2292884cc03cebd361f3f
- https://github.com/harvey-woo/key-serializer
