# [H] FileManager Deserialization of Untrusted Data vulnerability

## Summary
Severity: High
Advisory: GHSA-8237-957h-h2c2
CVE: CVE-2024-52306
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-8237-957h-h2c2
Type: github-advisory

## Affected
- Packagist: `backpack/filemanager` — affected >=3.0.0 <3.0.9
- Packagist: `backpack/filemanager` — affected >=0 <2.0.2

## Details
### Impact
Deserialization of untrusted data from the `mimes` parameter could lead to remote code execution.

### Patches
Fixed in 3.0.9

### Workarounds
Not needed, a `composer update` will solve it in a non-breaking way.

### References
Reported responsibly [Vladislav Gladkiy](https://github.com/catferq) at [Positive Technologies](https://www.ptsecurity.com/ww-en/).

## References
- https://github.com/Laravel-Backpack/FileManager/security/advisories/GHSA-8237-957h-h2c2
- https://nvd.nist.gov/vuln/detail/CVE-2024-52306
- https://github.com/Laravel-Backpack/FileManager/commit/2830498b85e05fb3c92179053b4d7c4a0fdb880b
- https://github.com/Laravel-Backpack/FileManager
