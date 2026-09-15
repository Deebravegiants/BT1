# [H] SQL Injection on REST API in GLPI

## Summary
Severity: High
Advisory: CVE-2022-39323
Aliases: GHSA-cp6q-9p4x-8hr9
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-11-03
Source: https://osv.dev/vulnerability/CVE-2022-39323
Type: osv

## Details
GLPI stands for Gestionnaire Libre de Parc Informatique. GLPI is a Free Asset and IT Management Software package that provides ITIL Service Desk features, licenses tracking and software auditing. Time based attack using a SQL injection in api REST user_token. This issue has been patched, please upgrade to version 10.0.4. As a workaround, disable login with user_token on API Rest.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39323.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-cp6q-9p4x-8hr9
- https://nvd.nist.gov/vuln/detail/CVE-2022-39323
