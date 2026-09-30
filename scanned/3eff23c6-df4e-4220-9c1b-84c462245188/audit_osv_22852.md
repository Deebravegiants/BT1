# [M] Improper access to debug panel in GLPI

## Summary
Severity: Medium
Advisory: CVE-2022-39370
Aliases: GHSA-6c2p-wgx9-vrjc
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-11-03
Source: https://osv.dev/vulnerability/CVE-2022-39370
Type: osv

## Details
GLPI stands for Gestionnaire Libre de Parc Informatique. GLPI is a Free Asset and IT Management Software package that provides ITIL Service Desk features, licenses tracking and software auditing. Connected users may gain access to debug panel through the GLPI update script. This issue has been patched, please upgrade to 10.0.4. As a workaround, delete the `install/update.php` script.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39370.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-6c2p-wgx9-vrjc
- https://nvd.nist.gov/vuln/detail/CVE-2022-39370
