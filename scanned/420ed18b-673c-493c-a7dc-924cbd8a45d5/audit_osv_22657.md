# [C] SQL injection in GLPI

## Summary
Severity: Critical
Advisory: CVE-2022-35947
Aliases: GHSA-7p3q-cffg-c8xh
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-09-14
Source: https://osv.dev/vulnerability/CVE-2022-35947
Type: osv

## Details
GLPI stands for Gestionnaire Libre de Parc Informatique and is a Free Asset and IT Management Software package, that provides ITIL Service Desk features, licenses tracking and software auditing. Affected versions have been found to be vulnerable to a SQL injection attack which an attacker could leverage to simulate an arbitrary user login. Users are advised to upgrade to version 10.0.3. Users unable to upgrade should disable the `Enable login with external token` API configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/35xxx/CVE-2022-35947.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-7p3q-cffg-c8xh
- https://nvd.nist.gov/vuln/detail/CVE-2022-35947
- https://github.com/glpi-project/glpi/commit/564309d2c1180d5ba1615f4bbaf6623df81b4962
