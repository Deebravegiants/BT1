# [H] FacturaScripts is Vulnerable to Stored Cross-Site Scripting (XSS) via XML File Upload

## Summary
Severity: High
Advisory: GHSA-2267-xqcf-gw2m
CVE: CVE-2025-69210
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-30
Source: https://github.com/advisories/GHSA-2267-xqcf-gw2m
Type: github-advisory

## Affected
- Packagist: `facturascripts/facturascripts` — affected >=0 <2025.7
- Packagist: `facturascripts/facturascripts` — affected 2025.11
- Packagist: `facturascripts/facturascripts` — affected 2025.41
- Packagist: `facturascripts/facturascripts` — affected 2025.43

## Details
A stored cross-site scripting (XSS) vulnerability exists in the product file upload functionality.

Authenticated users can upload crafted XML files containing executable JavaScript. These files are later rendered by the application without sufficient sanitization or content-type enforcement, allowing arbitrary JavaScript execution when the file is accessed.

Because product files uploaded by regular users are visible to administrative users, this vulnerability can be leveraged to execute malicious JavaScript in an administrator’s browser session.

## References
- https://github.com/NeoRazorX/facturascripts/security/advisories/GHSA-2267-xqcf-gw2m
- https://nvd.nist.gov/vuln/detail/CVE-2025-69210
- https://github.com/NeoRazorX/facturascripts/commit/e908ade21c84bdc9d51190057482316730c66146
- https://facturascripts.com/publicaciones/ya-disponible-facturascripts-2025-7
- https://github.com/NeoRazorX/facturascripts
- https://github.com/NeoRazorX/facturascripts/releases/tag/v2025.7
