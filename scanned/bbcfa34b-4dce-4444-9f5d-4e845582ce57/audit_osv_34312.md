# [M] Nextcloud Tables app allowed to include local file via PhpSpreadsheet when importing a table

## Summary
Severity: Medium
Advisory: CVE-2025-58051
Aliases: GHSA-wpp5-4w35-pxq6
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-58051
Type: osv

## Details
Nextcloud Tables allows you to create your own tables with individual columns. Prior 0.7.6, 0.8.8, and 0.9.5, when importing a table, a user was able to specify files on the server and when their format is supported by the used PhpSpreadsheet library they would be included and their content leaked to the user. It is recommended that the Nextcloud Tables app is upgraded to 0.7.6, 0.8.8 or 0.9.5.

## References
- https://hackerone.com/reports/3249624
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58051.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-wpp5-4w35-pxq6
- https://nvd.nist.gov/vuln/detail/CVE-2025-58051
- https://github.com/nextcloud/tables/pull/1936
