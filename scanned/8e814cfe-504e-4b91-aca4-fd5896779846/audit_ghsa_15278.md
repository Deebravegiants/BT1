# [H] Filament Excel Vulnerable to Path Traversal Attack on Export Download Endpoint

## Summary
Severity: High
Advisory: GHSA-m3px-vjxr-fx4m
CVE: CVE-2024-42485
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-12
Source: https://github.com/advisories/GHSA-m3px-vjxr-fx4m
Type: github-advisory

## Affected
- Packagist: `pxlrbt/filament-excel` — affected >=2.0.0-alpha <2.3.3
- Packagist: `pxlrbt/filament-excel` — affected >=0 <1.1.14

## Details
### Impact
The export download route `/filament-excel/{path}` allowed downloading any file without login when the webserver allows `../` in the URL. 

### Patches
Patched with Version v2.3.3

### Credits
Thanks to Kevin Pohl for reporting this.

## References
- https://github.com/pxlrbt/filament-excel/security/advisories/GHSA-m3px-vjxr-fx4m
- https://nvd.nist.gov/vuln/detail/CVE-2024-42485
- https://github.com/pxlrbt/filament-excel/commit/af36f933b032aefccc87d17431b6e74673b04af5
- https://github.com/pxlrbt/filament-excel/commit/bda42891a4b0c15d5dab5da8c53a006ddadccfb7
- https://github.com/pxlrbt/filament-excel
- https://github.com/pxlrbt/filament-excel/releases/tag/v1.1.14
