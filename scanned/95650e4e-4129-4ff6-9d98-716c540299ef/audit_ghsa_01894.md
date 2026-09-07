# [M] Dolibarr Cross Site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jqfp-m5f8-vg28
CVE: CVE-2021-42220
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-jqfp-m5f8-vg28
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <14.0.3

## Details
A Cross Site Scripting (XSS) vulnerability exists in Dolibarr before 14.0.3 via the ticket creation flow. Exploitation requires that an admin copies the payload into a box.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42220
- https://github.com/Dolibarr/dolibarr
- https://packetstormsecurity.com/files/164544/Dolibarr-ERP-CRM-14.0.2-Cross-Site-Scripting-Privilege-Escalation.html
- https://truedigitalsecurity.com/advisory-summary-2021
