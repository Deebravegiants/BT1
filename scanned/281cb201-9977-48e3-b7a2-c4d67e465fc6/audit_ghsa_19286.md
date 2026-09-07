# [M] Chrome PHP is missing encoding in `CssSelector`

## Summary
Severity: Medium
Advisory: GHSA-3432-fmrf-7vmh
CVE: CVE-2025-48883
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-3432-fmrf-7vmh
Type: github-advisory

## Affected
- Packagist: `chrome-php/chrome` — affected >=0 <1.14.0

## Details
### Impact

CSS Selector expressions are not properly encoded, which can lead to XSS (cross-site scripting) vulnerabilities.

### Patches

This is patched in v1.14.0.

### Workarounds

Users can apply encoding manually to their selectors, if they are unable to upgrade.

## References
- https://github.com/chrome-php/chrome/security/advisories/GHSA-3432-fmrf-7vmh
- https://nvd.nist.gov/vuln/detail/CVE-2025-48883
- https://github.com/chrome-php/chrome/pull/691
- https://github.com/chrome-php/chrome/commit/34b2b8d1691f4e3940b1e1e95d388fffe81169c8
- https://github.com/chrome-php/chrome
