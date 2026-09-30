# [M] SPIP interface_traduction_objets < 2.2.2 Authenticated SQL Injection

## Summary
Severity: Medium
Advisory: CVE-2026-27747
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27747
Type: osv

## Details
The SPIP interface_traduction_objets plugin versions prior to 2.2.2 contain an authenticated SQL injection vulnerability in interface_traduction_objets_pipelines.php. When handling translation requests, the plugin reads the id_parent parameter from user-supplied input and concatenates it directly into a SQL WHERE clause in a call to sql_getfetsel() without input validation or parameterization. An authenticated attacker with editor-level privileges can inject crafted SQL expressions into the id_parent parameter to manipulate the backend query. Successful exploitation can result in disclosure or modification of database contents and may lead to denial of service depending on the database configuration and privileges.

## References
- https://git.spip.net/spip-contrib-extensions/interface_traduction_objets
- https://plugins.spip.net/interface_traduction_objets
- https://blog.spip.net/Mise-a-jour-de-securite-sortie-de-SPIP-4-4-10.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27747.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27747
- https://www.vulncheck.com/advisories/spip-interface-traduction-objets-authenticated-sql-injection
- https://git.spip.net/spip-contrib-extensions/interface_traduction_objets/-/commit/db3417b7811774f04c3ff191ca1737fe660ef0be
- https://chocapikk.com/posts/2026/spip-plugins-vulnerabilities/
