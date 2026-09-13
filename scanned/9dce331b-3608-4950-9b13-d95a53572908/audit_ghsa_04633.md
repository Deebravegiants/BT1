# [M] Statamic Vulnerable to CSV formula injection in form submission exports

## Summary
Severity: Medium
Advisory: GHSA-h77m-qrj7-jxcw
CVE: CVE-2026-54243
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-h77m-qrj7-jxcw
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=6.0.0 <6.20.1
- Packagist: `statamic/cms` — affected >=0 <5.73.24

## Details
### Impact

Form submission values were not neutralized for spreadsheet formula characters when exported to CSV. A submission containing a value beginning with a formula trigger character (e.g.  = ,  + ,  - ,  @ ) could be interpreted as a live formula when a Control Panel user opens the export in a spreadsheet application. Form submissions can come from unauthenticated front-end visitors, so the malicious value can be supplied by an anonymous user and is later triggered by an editor opening the export.

Exploitation affects the spreadsheet application used to open the export, not the Statamic application or server; the data at risk is the form submission data the exporting user is already authorized to view.


### Patches

This has been fixed in 5.73.24 and 6.20.1.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-h77m-qrj7-jxcw
- https://github.com/statamic/cms
