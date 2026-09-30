# [C] SPIP referer_spam < 1.3.0 Unauthenticated SQL Injection

## Summary
Severity: Critical
Advisory: CVE-2026-27743
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27743
Type: osv

## Details
The SPIP referer_spam plugin versions prior to 1.3.0 contain an unauthenticated SQL injection vulnerability in the referer_spam_ajouter and referer_spam_supprimer action handlers. The handlers read the url parameter from a GET request and interpolate it directly into SQL LIKE clauses without input validation or parameterization. The endpoints do not enforce authorization checks and do not use SPIP action protections such as securiser_action(), allowing remote attackers to execute arbitrary SQL queries.

## References
- https://git.spip.net/spip-contrib-extensions/referer_spam
- https://plugins.spip.net/referer_spam.html
- https://blog.spip.net/Mise-a-jour-de-securite-sortie-de-SPIP-4-4-10.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27743.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27743
- https://www.vulncheck.com/advisories/spip-referer-spam-unauthenticated-sql-injection
- https://git.spip.net/spip-contrib-extensions/referer_spam/-/commit/33682df73cd5f7e9c72d8c4d5088611fa2441683
- https://chocapikk.com/posts/2026/spip-plugins-vulnerabilities/
