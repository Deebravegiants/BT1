# [M] SQL injection in ITIL actors in GLPI

## Summary
Severity: Medium
Advisory: CVE-2023-42461
Aliases: GHSA-x3jp-69f2-p84w
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-09-26
Source: https://osv.dev/vulnerability/CVE-2023-42461
Type: osv

## Details
GLPI stands for Gestionnaire Libre de Parc Informatique is a Free Asset and IT Management Software package, that provides ITIL Service Desk features, licenses tracking and software auditing. The ITIL actors input field from the Ticket form can be used to perform a SQL injection. Users are advised to upgrade to version 10.0.10. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42461.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-x3jp-69f2-p84w
- https://nvd.nist.gov/vuln/detail/CVE-2023-42461
