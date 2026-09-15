# [M] glpi vulnerable to Unauthorized access to data export

## Summary
Severity: Medium
Advisory: CVE-2023-23610
Aliases: GHSA-6565-hm87-24hf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-25
Source: https://osv.dev/vulnerability/CVE-2023-23610
Type: osv

## Details
GLPI is a Free Asset and IT Management Software package. Versions prior to 9.5.12 and 10.0.6 are vulnerable to Improper Privilege Management. Any user having access to the standard interface can export data of almost any GLPI item type, even those on which user is not allowed to access (including assets, tickets, users, ...). This issue is patched in 10.0.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23610.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-6565-hm87-24hf
- https://nvd.nist.gov/vuln/detail/CVE-2023-23610
