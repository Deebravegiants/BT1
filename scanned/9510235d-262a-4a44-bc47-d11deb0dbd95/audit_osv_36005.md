# [M] Shlink Blind SQL Injection via tags/stats orderBy Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-18737
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-18737
Type: osv

## Details
Shlink contains a blind SQL injection vulnerability that allows any authenticated API key holder to inject arbitrary SQL fragments by supplying an unvalidated direction value in the orderBy query parameter of the tag statistics endpoint. Attackers can craft a malicious direction string containing SQL subqueries that flows unsanitized into a Doctrine QueryBuilder ORDER BY clause, enabling time-based, boolean-oracle, and error-based extraction of sensitive data including long URLs, visitor records, IP addresses, geolocation data, user agents, and hashed API key secrets from any tenant.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18737.json
- https://github.com/theopaid/SQL-injection-in-GET-rest-v-n-tags-stats-via-the-orderBy-parameter-shlink-
- https://nvd.nist.gov/vuln/detail/CVE-2026-18737
- https://www.vulncheck.com/advisories/shlink-blind-sql-injection-via-tags-stats-orderby-parameter
- https://github.com/shlinkio/shlink
