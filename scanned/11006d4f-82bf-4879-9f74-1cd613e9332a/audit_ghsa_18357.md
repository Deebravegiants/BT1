# [M] mkdocs-include-markdown-plugin susceptible to unvalidated input colliding with substitution placeholders 

## Summary
Severity: Medium
Advisory: GHSA-v39m-5m9j-m9w9
CVE: CVE-2025-59940
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-09-29
Source: https://github.com/advisories/GHSA-v39m-5m9j-m9w9
Type: github-advisory

## Affected
- PyPI: `mkdocs-include-markdown-plugin` — affected >=0 <7.1.8

## Details
### Impact
CWE-20: Improper Input Validation
Low impact

### Patches
Patched in v7.1.8 (commit https://github.com/mondeja/mkdocs-include-markdown-plugin/commit/7466d67aa0de8ffbc427204ad2475fed07678915)

### Workarounds
No

## References
- https://github.com/mondeja/mkdocs-include-markdown-plugin/security/advisories/GHSA-v39m-5m9j-m9w9
- https://nvd.nist.gov/vuln/detail/CVE-2025-59940
- https://github.com/mondeja/mkdocs-include-markdown-plugin/issues/274
- https://github.com/mondeja/mkdocs-include-markdown-plugin/pull/277
- https://github.com/mondeja/mkdocs-include-markdown-plugin/commit/7466d67aa0de8ffbc427204ad2475fed07678915
- https://github.com/mondeja/mkdocs-include-markdown-plugin
