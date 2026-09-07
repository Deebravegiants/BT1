# [H] Dolibarr vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-6ppg-rgrg-f573
CVE: CVE-2024-31503
CWE: CWE-284, CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-6ppg-rgrg-f573
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0

## Details
Incorrect access control in Dolibarr ERP CRM versions 19.0.0 and before, allows authenticated attackers to steal victim users' session cookies and CSRF protection tokens via user interaction with a crafted web page, leading to account takeover.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31503
- https://github.com/Dolibarr/dolibarr
- https://github.com/alexbsec/CVEs/blob/master/2024/CVE-2024-31503.md
