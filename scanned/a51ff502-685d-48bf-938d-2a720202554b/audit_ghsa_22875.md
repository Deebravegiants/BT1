# [M] Dolibarr Stored Cross-site Scripting via file upload

## Summary
Severity: Medium
Advisory: GHSA-fvf9-2hjp-w936
CVE: CVE-2020-13239
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fvf9-2hjp-w936
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected 11.0.4

## Details
The DMS/ECM module in Dolibarr 11.0.4 renders user-uploaded .html files in the browser when the attachment parameter is removed from the direct download link. This causes XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13239
- https://github.com/Dolibarr/dolibarr
- https://www.dubget.com/stored-xss-via-file-upload.html
