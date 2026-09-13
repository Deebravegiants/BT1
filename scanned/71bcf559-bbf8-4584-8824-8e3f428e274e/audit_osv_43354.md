# [M] CamaleonCMS 2.9.1 Authenticated SQL Injection via Post Slug Field

## Summary
Severity: Medium
Advisory: CVE-2026-73331
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73331
Type: osv

## Details
CamaleonCMS 2.9.1 contains an authenticated SQL injection vulnerability that allows authenticated attackers with post creation or editing privileges to submit a crafted slug value containing SQL syntax that the database backend evaluates as part of an inadequately parameterized query. Attackers can supply malicious slug payloads using boolean- or union-style blind SQL injection techniques to extract sensitive data from the underlying SQLite database, including administrative credentials and configuration values stored in application tables.

## References
- https://enrik-m.github.io/posts/Camaleon-CMS-Vulnerabilties/#44-stored-xss-via-draft-post-title
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73331.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73331
- https://www.vulncheck.com/advisories/camaleoncms-authenticated-sql-injection-via-post-slug-field
- https://github.com/owen2345/camaleon-cms
