# [M] Unauthenticated Local File Inclusion

## Summary
Severity: Medium
Advisory: CVE-2022-31062
Aliases: GHSA-q33f-jcjf-p4v9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-06-20
Source: https://osv.dev/vulnerability/CVE-2022-31062
Type: osv

## Details
### Impact A plugin public script can be used to read content of system files. ### Patches Upgrade to version 1.0.2. ### Workarounds `b/deploy/index.php` file can be deleted if deploy feature is not used.

## References
- http://packetstormsecurity.com/files/171654/GLPI-Glpiinventory-1.0.1-Local-File-Inclusion.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31062.json
- https://github.com/glpi-project/glpi-inventory-plugin/security/advisories/GHSA-q33f-jcjf-p4v9
- https://nvd.nist.gov/vuln/detail/CVE-2022-31062
