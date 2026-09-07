# [M] pimcore/admin-ui-classic-bundle Full Path Disclosure via re-export document

## Summary
Severity: Medium
Advisory: GHSA-c8hj-w239-5gvf
CVE: CVE-2023-47636
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-11-15
Source: https://github.com/advisories/GHSA-c8hj-w239-5gvf
Type: github-advisory

## Affected
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=0 <1.2.1

## Details
### Impact
Full Path Disclosure (FPD) vulnerabilities enable the attacker to see the path to the webroot/file. e.g.: /home/omg/htdocs/file/. Certain vulnerabilities, such as using the load_file() (within a SQL Injection) query to view the page source, require the attacker to have the full path to the file they wish to view.

In the case of pimcore, the fopen() function here doesn't have an error handle when the file doesn't exist on the server so the server response raises the full path "fopen(/var/www/html/var/tmp/export-{ uniqe id}.csv)"

### Patches
Apply patch https://github.com/pimcore/admin-ui-classic-bundle/commit/10d178ef771097604a256c1192b098af9ec57a87.patch

### Workarounds
Update to version 1.2.1 or apply [patches](https://github.com/pimcore/admin-ui-classic-bundle/commit/10d178ef771097604a256c1192b098af9ec57a87.patch) manually

### References
https://huntr.com/bounties/4af4db18-9fd4-43e9-8bc6-c88aaf76839c/

## References
- https://github.com/pimcore/admin-ui-classic-bundle/security/advisories/GHSA-c8hj-w239-5gvf
- https://nvd.nist.gov/vuln/detail/CVE-2023-47636
- https://github.com/pimcore/admin-ui-classic-bundle/commit/10d178ef771097604a256c1192b098af9ec57a87
- https://github.com/pimcore/admin-ui-classic-bundle
- https://huntr.com/bounties/4af4db18-9fd4-43e9-8bc6-c88aaf76839c
