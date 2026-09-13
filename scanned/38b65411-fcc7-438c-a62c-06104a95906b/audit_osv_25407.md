# [H] GLPI vulnerable to unauthenticated access to Dashboard data

## Summary
Severity: High
Advisory: CVE-2023-35940
Aliases: GHSA-qrh8-rg45-45fw
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-35940
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 9.5.0 and prior to version 10.0.8, an incorrect rights check on a file allows an unauthenticated user to be able to access dashboards data. Version 10.0.8 contains a patch for this issue.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35940.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-qrh8-rg45-45fw
- https://nvd.nist.gov/vuln/detail/CVE-2023-35940
