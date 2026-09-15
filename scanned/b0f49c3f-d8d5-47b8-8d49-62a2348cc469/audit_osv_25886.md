# [H] GLPI Remote code execution from LDAP server configuration form on PHP 7.4

## Summary
Severity: High
Advisory: CVE-2023-46726
Aliases: GHSA-qc92-gxc6-5f95
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-13
Source: https://osv.dev/vulnerability/CVE-2023-46726
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 10.0.0 and prior to version 10.0.11, on PHP 7.4 only, the LDAP server configuration form can be used to execute arbitrary code previously uploaded as a GLPI document. Version 10.0.11 contains a patch for the issue.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46726.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-qc92-gxc6-5f95
- https://nvd.nist.gov/vuln/detail/CVE-2023-46726
- https://github.com/glpi-project/glpi/commit/42ba2b031bec0b3889317db25f3adf9080fc11b2
