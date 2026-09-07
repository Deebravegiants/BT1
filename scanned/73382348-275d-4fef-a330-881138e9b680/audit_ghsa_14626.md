# [M] Cross-site Scripting vulnerability in SimpleXLSXEx::readThemeColors, SimpleXLSXEx::getColorValue and SimpleXLSX::toHTMLEx

## Summary
Severity: Medium
Advisory: GHSA-r87q-fj25-f8jf
CVE: CVE-2024-56364
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-r87q-fj25-f8jf
Type: github-advisory

## Affected
- Packagist: `shuchkin/simplexlsx` — affected >=1.0.12 <1.1.13

## Details
### Impact
When calling the extended toHTMLEx method, it is possible to execute arbitrary JavaScript code.

### Patches
The supplied patch resolves this vulnerability for SimpleXLSX. Use 1.1.13

### Workarounds
Don't use data publication via toHTMLEx

***
This vulnerability was discovered by Aleksey Solovev (Positive Technologies)

## References
- https://github.com/shuchkin/simplexlsx/security/advisories/GHSA-r87q-fj25-f8jf
- https://nvd.nist.gov/vuln/detail/CVE-2024-56364
- https://github.com/shuchkin/simplexlsx/commit/71a5e3d40d14e33161f8a40b3fd02de542218ef0
- https://github.com/shuchkin/simplexlsx
