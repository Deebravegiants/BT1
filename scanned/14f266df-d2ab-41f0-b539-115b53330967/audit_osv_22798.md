# [M] user session persists even after permanently deleting account in GLPI

## Summary
Severity: Medium
Advisory: CVE-2022-39234
Aliases: GHSA-pgcx-mc58-3gmg
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:L/A:N)
Published: 2022-11-03
Source: https://osv.dev/vulnerability/CVE-2022-39234
Type: osv

## Details
GLPI stands for Gestionnaire Libre de Parc Informatique. GLPI is a Free Asset and IT Management Software package that provides ITIL Service Desk features, licenses tracking and software auditing. Deleted/deactivated user could continue to use their account as long as its cookie is valid. This issue has been patched, please upgrade to version 10.0.4. There are currently no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39234.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-pgcx-mc58-3gmg
- https://nvd.nist.gov/vuln/detail/CVE-2022-39234
