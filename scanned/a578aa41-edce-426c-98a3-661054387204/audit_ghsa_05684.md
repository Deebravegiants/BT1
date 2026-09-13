# [H] Seroval affected by Denial of Service via Deeply Nested Objects

## Summary
Severity: High
Advisory: GHSA-3j22-8qj3-26mx
CVE: CVE-2026-24006
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-3j22-8qj3-26mx
Type: github-advisory

## Affected
- npm: `seroval` — affected >=0 <1.4.1

## Details
Serialization of objects with extreme depth can **exceed the maximum call stack limit**.  

**Mitigation**:  
`Seroval` introduces a `depthLimit` parameter in serialization/deserialization methods. **An error will be thrown if the depth limit is reached.**

## References
- https://github.com/lxsmnsyc/seroval/security/advisories/GHSA-3j22-8qj3-26mx
- https://nvd.nist.gov/vuln/detail/CVE-2026-24006
- https://github.com/lxsmnsyc/seroval/commit/ce9408ebc87312fcad345a73c172212f2a798060
- https://github.com/lxsmnsyc/seroval
