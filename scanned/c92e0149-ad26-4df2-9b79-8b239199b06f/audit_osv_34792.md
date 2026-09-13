# [M] GLPI Database Inventory Plugin Vulnerable to Stored Object Injection

## Summary
Severity: Medium
Advisory: CVE-2025-65035
Aliases: GHSA-xc3r-32rx-3j4j
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-19
Source: https://osv.dev/vulnerability/CVE-2025-65035
Type: osv

## Details
pluginsGLPI's Database Inventory Plugin "manages" the Teclib' inventory agents in order to perform an inventory of the databases present on the workstation. Prior to version 1.1.2, in certain conditions (database write access must first be obtained through another vulnerability or misconfiguration), user-controlled data is stored insecurely in the database via computergroup, and is later unserialized on every page load, allowing arbitrary PHP object instantiation. Version 1.1.2 fixes the issue.

## References
- https://github.com/pluginsGLPI/databaseinventory/blob/1.1.2/CHANGELOG.md#112---2025-11-25
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65035.json
- https://github.com/pluginsGLPI/databaseinventory/security/advisories/GHSA-xc3r-32rx-3j4j
- https://nvd.nist.gov/vuln/detail/CVE-2025-65035
- https://github.com/pluginsGLPI/databaseinventory/commit/08c7055d2c5fc744cb092d7d56a608e359c56f1a
