# [M] The wp-enable-svg WordPress plugin does not sanitize SVG files when uploaded

## Summary
Severity: Medium
Advisory: GHSA-j77f-79w9-rghc
CVE: CVE-2024-11184
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-02
Source: https://github.com/advisories/GHSA-j77f-79w9-rghc
Type: github-advisory

## Affected
- Packagist: `mwdelaney/wp-enable-svg` — affected >=0

## Details
The wp-enable-svg WordPress plugin through 0.2 does not sanitize SVG files when uploaded, allowing for authors and above to upload SVGs containing malicious scripts

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11184
- https://github.com/MWDelaney/wp-enable-svg
- https://wpscan.com/vulnerability/fc982bcb-9974-481f-aef4-580ae9edc3c8
