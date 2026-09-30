# [C] GLPI vulnerable to unallowed PHP script execution

## Summary
Severity: Critical
Advisory: CVE-2023-42802
Aliases: GHSA-rrh2-x4ch-pq3m
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-11-02
Source: https://osv.dev/vulnerability/CVE-2023-42802
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 10.0.7 and prior to version 10.0.10, an unverified object instantiation allows one to upload malicious PHP files to unwanted directories. Depending on web server configuration and available system libraries, malicious PHP files can then be executed through a web server request. Version 10.0.10 fixes this issue. As a workaround, remove write access on `/ajax` and `/front` files to the web server.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42802.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-rrh2-x4ch-pq3m
- https://nvd.nist.gov/vuln/detail/CVE-2023-42802
