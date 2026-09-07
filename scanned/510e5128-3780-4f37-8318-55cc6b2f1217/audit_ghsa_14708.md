# [M] Cross-site Scripting vulnerability in SimpleXLSXEx::readXfs and SimpeXLSX::toHTMLEx

## Summary
Severity: Medium
Advisory: GHSA-x6mh-rjwm-8ph7
CVE: CVE-2024-55878
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-12
Source: https://github.com/advisories/GHSA-x6mh-rjwm-8ph7
Type: github-advisory

## Affected
- Packagist: `shuchkin/simplexlsx` — affected >=1.0.12 <1.1.12

## Details
### Impact
When calling the extended toHTMLEx method, it is possible to execute arbitrary JavaScript code.

### Patches
The supplied patch resolves this vulnerability for SimpleXLSX. Use 1.1.12

### Workarounds
Don't use direct publication via toHTMLEx

***
This vulnerability was discovered by Aleksey Solovev (Positive Technologies)

## References
- https://github.com/shuchkin/simplexlsx/security/advisories/GHSA-x6mh-rjwm-8ph7
- https://nvd.nist.gov/vuln/detail/CVE-2024-55878
- https://github.com/shuchkin/simplexlsx/commit/cb4e716259e83d18e89292a4f1b721f4d34e28c2
- https://github.com/shuchkin/simplexlsx
