# [H] Account takeover via SQL Injection in UI layout preferences in GLPI

## Summary
Severity: High
Advisory: CVE-2023-41320
Aliases: GHSA-mv2r-gpw3-g476
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-09-26
Source: https://osv.dev/vulnerability/CVE-2023-41320
Type: osv

## Details
GLPI stands for Gestionnaire Libre de Parc Informatique is a Free Asset and IT Management Software package, that provides ITIL Service Desk features, licenses tracking and software auditing. UI layout preferences management can be hijacked to lead to SQL injection. This injection can be use to takeover an administrator account. Users are advised to upgrade to version 10.0.10. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41320.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-mv2r-gpw3-g476
- https://nvd.nist.gov/vuln/detail/CVE-2023-41320
