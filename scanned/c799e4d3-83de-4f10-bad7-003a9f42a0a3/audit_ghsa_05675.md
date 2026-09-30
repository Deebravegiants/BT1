# [H] Seroval affected by Denial of Service via Array serialization

## Summary
Severity: High
Advisory: GHSA-66fc-rw6m-c2q6
CVE: CVE-2026-23957
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-66fc-rw6m-c2q6
Type: github-advisory

## Affected
- npm: `seroval` — affected >=0 <1.4.1

## Details
Overriding encoded array lengths by replacing them with an excessively large value causes the deserialization process to **significantly increase processing time**.  

**Mitigation**:  
`Seroval` no longer encodes array lengths.
Instead, it computes length using `Array.prototype.length` during deserialization.

## References
- https://github.com/lxsmnsyc/seroval/security/advisories/GHSA-66fc-rw6m-c2q6
- https://nvd.nist.gov/vuln/detail/CVE-2026-23957
- https://github.com/lxsmnsyc/seroval/commit/ce9408ebc87312fcad345a73c172212f2a798060
- https://github.com/lxsmnsyc/seroval
