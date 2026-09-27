# [C] GLPI DataInjection Plugin Authenticated SQL Injection via CSV Import

## Summary
Severity: Critical
Advisory: CVE-2026-11321
Aliases: GHSA-57qv-j6r6-pcc4
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-11321
Type: osv

## Details
The DataInjection plugin for GLPI 2.15.6 (GLPI 11 builds) concatenates user-supplied CSV field values directly into SQL queries during CSV import, without parameterization or escaping, resulting in authenticated SQL injection. An authenticated user with access to the Data injection feature can embed SQL expressions such as SLEEP() in a mapped field (for example Serial Number) to manipulate the generated query and extract database information via time-based blind injection.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11321.json
- https://github.com/pluginsGLPI/datainjection/security/advisories/GHSA-57qv-j6r6-pcc4
- https://nvd.nist.gov/vuln/detail/CVE-2026-11321
- https://www.vulncheck.com/advisories/glpi-datainjection-plugin-authenticated-sql-injection-via-csv-import
- https://github.com/pluginsGLPI/datainjection/releases/tag/2.15.7
- https://github.com/pluginsGLPI/datainjection
