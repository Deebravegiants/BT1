# [M] SQL injection using custom CSS administration form in GLPI

## Summary
Severity: Medium
Advisory: CVE-2022-21720
Aliases: GHSA-5hg4-r64r-rf83
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-01-28
Source: https://osv.dev/vulnerability/CVE-2022-21720
Type: osv

## Details
GLPI is a free asset and IT management software package. Prior to version 9.5.7, an entity administrator is capable of retrieving normally inaccessible data via SQL injection. Version 9.5.7 contains a patch for this issue. As a workaround, disabling the `Entities` update right prevents exploitation of this vulnerability.

## References
- https://github.com/glpi-project/glpi/releases/tag/9.5.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21720.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-5hg4-r64r-rf83
- https://nvd.nist.gov/vuln/detail/CVE-2022-21720
- https://github.com/glpi-project/glpi/commit/5c3eee696b503fdf502f506b00d15cf5b324b326
