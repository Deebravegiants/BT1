# [C] Electron: Buffer performs incorrect byte length calculations resulting in heap buffer under/overflow

## Summary
Severity: Critical
Advisory: GHSA-q6m5-f73j-m9mc
CVE: CVE-2026-54257
CWE: CWE-120
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-q6m5-f73j-m9mc
Type: github-advisory

## Affected
- npm: `electron` — affected >=42.3.1 <42.3.3

## Details
### Impact
Most apps will crash and some may perform incorrect buffer allocations in the Node.js `Buffer` API resulting in unexpected truncation or allocation.

### Workarounds
No workarounds. Do not use these impacted Electron releases

### Fixed Versions
* `42.3.3`

### For more information
If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-q6m5-f73j-m9mc
- https://nvd.nist.gov/vuln/detail/CVE-2026-54257
- https://github.com/electron/electron
