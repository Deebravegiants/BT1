# [H] Improper handling of CSS at-rules in lettersanitizer

## Summary
Severity: High
Advisory: GHSA-7r3r-gq8p-v9jj
CVE: CVE-2022-31103
CWE: CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-23
Source: https://github.com/advisories/GHSA-7r3r-gq8p-v9jj
Type: github-advisory

## Affected
- npm: `lettersanitizer` — affected >=0 <1.0.2

## Details
### Impact

All versions of lettersanitizer below 1.0.2 are affected by a denial of service issue when processing a CSS at-rule `@keyframes`.

This package is depended on by [react-letter](https://github.com/mat-sz/react-letter), therefore everyone using react-letter is also at risk.

### Patches

The problem has been patched in version 1.0.2.

### Workarounds

There is no workaround besides upgrading.

### References

The issue was originally reported in the react-letter repository: https://github.com/mat-sz/react-letter/issues/17

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [lettersanitizer](https://github.com/mat-sz/lettersanitizer/issues)
* Email me at [contact@matsz.dev](mailto:contact@matsz.dev)

## References
- https://github.com/mat-sz/lettersanitizer/security/advisories/GHSA-7r3r-gq8p-v9jj
- https://nvd.nist.gov/vuln/detail/CVE-2022-31103
- https://github.com/mat-sz/react-letter/issues/17
- https://github.com/mat-sz/lettersanitizer/commit/96d3dfe2ef0465d47324ed4d13e91ba0816a173f
- https://github.com/mat-sz/lettersanitizer
