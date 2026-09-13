# [M] SQL injection through plugin controller in GLPI

## Summary
Severity: Medium
Advisory: CVE-2022-35946
Aliases: GHSA-92q5-pfr8-r9r2
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:N)
Published: 2022-09-14
Source: https://osv.dev/vulnerability/CVE-2022-35946
Type: osv

## Details
GLPI stands for Gestionnaire Libre de Parc Informatique and is a Free Asset and IT Management Software package, that provides ITIL Service Desk features, licenses tracking and software auditing. In affected versions request input is not properly validated in the plugin controller and can be used to access low-level API of Plugin class. An attacker can, for instance, alter database data. Attacker must have "General setup" update rights to be able to perform this attack. Users are advised to upgrade to version 10.0.3. Users unable to upgrade should remove the `front/plugin.form.php` script.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/35xxx/CVE-2022-35946.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-92q5-pfr8-r9r2
- https://nvd.nist.gov/vuln/detail/CVE-2022-35946
- https://github.com/glpi-project/glpi/commit/f542ec8378afbd8038aeca5975b15eca3f0574c8
