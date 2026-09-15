# [M] Icinga DB Web hidden/protected custom variables are prone to filter enumeration

## Summary
Severity: Medium
Advisory: CVE-2025-61789
Aliases: GHSA-w57j-28jc-8429
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-61789
Type: osv

## Details
Icinga DB Web provides a graphical interface for Icinga monitoring. Before 1.1.4 and 1.2.3, an authorized user with access to Icinga DB Web, can use a custom variable in a filter that is either protected by icingadb/protect/variables or hidden by icingadb/denylist/variables, to guess values assigned to it. Versions 1.1.4 and 1.2.3 respond with an error if such a custom variable is used.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61789.json
- https://github.com/Icinga/icingadb-web/security/advisories/GHSA-w57j-28jc-8429
- https://nvd.nist.gov/vuln/detail/CVE-2025-61789
- https://github.com/Icinga/icingadb-web/commit/5e982dad40ec379075307ab1693580138e675b18
