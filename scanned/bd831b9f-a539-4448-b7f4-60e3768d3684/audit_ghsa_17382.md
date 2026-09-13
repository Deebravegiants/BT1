# [C] Grav may be vulnerable to SSRF attack via Twig Templates

## Summary
Severity: Critical
Advisory: GHSA-729w-j79f-2c34
CVE: CVE-2025-66844
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-729w-j79f-2c34
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0

## Details
In grav <1.7.49.5, a SSRF (Server-Side Request Forgery) vector may be triggered via Twig templates when page content is processed by Twig and the configuration allows undefined PHP functions to be registered.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66844
- https://github.com/Yohane-Mashiro/grav_cve/issues/2
- https://github.com/getgrav/grav
