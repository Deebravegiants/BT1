# [H] Account takeover via Kanban feature in GLPI

## Summary
Severity: High
Advisory: CVE-2023-41326
Aliases: GHSA-5wj6-hp4c-j5q9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-09-26
Source: https://osv.dev/vulnerability/CVE-2023-41326
Type: osv

## Details
GLPI stands for Gestionnaire Libre de Parc Informatique is a Free Asset and IT Management Software package, that provides ITIL Service Desk features, licenses tracking and software auditing. A logged user from any profile can hijack the Kanban feature to alter any user field, and end-up with stealing its account. Users are advised to upgrade to version 10.0.10. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41326.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-5wj6-hp4c-j5q9
- https://nvd.nist.gov/vuln/detail/CVE-2023-41326
