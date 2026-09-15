# [M] Improper Neutralization of Formula Elements in a CSV File in pimcore/pimcore

## Summary
Severity: Medium
Advisory: GHSA-pp2h-95hm-hv9r
CVE: CVE-2021-37702
CWE: CWE-1236
Ecosystem: Packagist
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-pp2h-95hm-hv9r
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.1.1

## Details
### Impact
Data Object CSV import allows formular injection. 

### Patches
Problem is patched in 10.1.1

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/9992.patch

### References
https://cwe.mitre.org/data/definitions/1236.html

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-pp2h-95hm-hv9r
- https://nvd.nist.gov/vuln/detail/CVE-2021-37702
- https://github.com/pimcore/pimcore/pull/9992
- https://github.com/pimcore/pimcore
