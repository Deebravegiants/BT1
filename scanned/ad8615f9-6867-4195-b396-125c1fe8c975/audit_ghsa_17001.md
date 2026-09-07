# [M] Pimcore TinyMCE Bundle - tinymce CVE-2024-29203, CVE-2024-29881

## Summary
Severity: Medium
Advisory: GHSA-vjwg-28gv-pm8h
CWE: CWE-1395, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-vjwg-28gv-pm8h
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=11.2.0 <11.2.3
- Packagist: `pimcore/pimcore` — affected >=11.0.0-ALPHA1 <11.1.6.5

## Details
### Impact
The TineMCE Bundle uses tinymce version 6.7.3. CVEs for this version exists for <6.8.1:
https://nvd.nist.gov/vuln/detail/CVE-2024-29203
https://nvd.nist.gov/vuln/detail/CVE-2024-29881

### Patches
The package should be updated to at least 6.8.1 to avoid XSS vulnerability.

### Workarounds
Upgrade pimcore to release 11.2.3 or 11.1.6.5.

### References
https://nvd.nist.gov/vuln/detail/CVE-2024-29203
https://nvd.nist.gov/vuln/detail/CVE-2024-29881

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-vjwg-28gv-pm8h
- https://github.com/pimcore/pimcore
