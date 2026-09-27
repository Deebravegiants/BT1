# [M] GLPI vulnerable to unauthorized access to User data

## Summary
Severity: Medium
Advisory: CVE-2023-34106
Aliases: GHSA-923r-hqh4-wj7c
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-34106
Type: osv

## Details
GLPI is a free asset and IT management software package. Versions of the software starting with 0.68 and prior to 10.0.8 have an incorrect rights check on a on a file accessible by an authenticated user. This allows access to the list of all users and their personal information. Users should upgrade to version 10.0.8 to receive a patch.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34106.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-923r-hqh4-wj7c
- https://nvd.nist.gov/vuln/detail/CVE-2023-34106
