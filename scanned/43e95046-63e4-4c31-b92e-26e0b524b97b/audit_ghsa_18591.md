# [H] Bagisto is vulnerable to XSS through Admin Panel's product creation path

## Summary
Severity: High
Advisory: GHSA-29mf-w486-v3vc
CVE: CVE-2025-60880
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:H (CVSS_V3)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-29mf-w486-v3vc
Type: github-advisory

## Affected
- Packagist: `bagisto/bagisto` — affected >=2.3.6 <2.3.7

## Details
An authenticated stored XSS vulnerability exists in the Bagisto 2.3.6 admin panel's product creation path, allowing an attacker to upload a crafted SVG file containing malicious JavaScript code. This vulnerability can be exploited by an authenticated admin user to execute arbitrary JavaScript in the browser, potentially leading to session hijacking, data theft, or unauthorized actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-60880
- https://github.com/bagisto/bagisto/commit/9ec40c99c34a83f311ffbb7c1039a59ff9d655cc
- https://gist.github.com/daman-preet-singh/cd431f4c30a585bb87d3c69e4a8eec98
- https://github.com/Shenal01/CVE-2025-60880
- https://github.com/bagisto/bagisto
- https://github.com/darylldoyle/svg-sanitizer/releases
