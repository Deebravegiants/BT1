# [H] seroval affected by Denial of Service via RegExp serialization

## Summary
Severity: High
Advisory: GHSA-hx9m-jf43-8ffr
CVE: CVE-2026-23956
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-hx9m-jf43-8ffr
Type: github-advisory

## Affected
- npm: `seroval` — affected >=0.2.0 <1.4.1

## Details
Overriding RegExp serialization with extremely large patterns can **exhaust JavaScript runtime memory** during deserialization. Additionally, overriding RegExp serialization with patterns that trigger **catastrophic backtracking** can lead to ReDoS (Regular Expression Denial of Service).  

**Mitigation**:  
`Seroval` introduces `disabledFeatures` (a bitmask) in serialization/deserialization methods, with `Feature.RegExp` as a dedicated flag. **Users are recommended to configure `disabledFeatures` to disable RegExp serialization entirely.**

## References
- https://github.com/lxsmnsyc/seroval/security/advisories/GHSA-hx9m-jf43-8ffr
- https://nvd.nist.gov/vuln/detail/CVE-2026-23956
- https://github.com/lxsmnsyc/seroval/commit/ce9408ebc87312fcad345a73c172212f2a798060
- https://github.com/lxsmnsyc/seroval
- https://github.com/lxsmnsyc/seroval/blob/v0.2.0/packages/seroval/src/index.ts#L90
