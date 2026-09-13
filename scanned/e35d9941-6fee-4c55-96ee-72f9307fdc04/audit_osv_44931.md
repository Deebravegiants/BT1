# [H] SOGo < 5.12.8 SQL Injection via addUserInAcls endpoint

## Summary
Severity: High
Advisory: CVE-2026-8851
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/CVE-2026-8851
Type: osv

## Details
SOGo versions 5.12.7 and prior contains a SQL injection vulnerability in the Access Control List management functionality that allows authenticated users to extract arbitrary data from the database by injecting SQL subqueries through the uid parameter of the addUserInAcls endpoint. Attackers can inject malicious SQL code to write extracted data into the sogo_acl table and retrieve it through the /acls API, establishing an out-of-band data exfiltration channel.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8851.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8851
- https://www.vulncheck.com/advisories/sogo-sql-injection-via-adduserinacls-endpoint
- https://github.com/Alinto/sogo/releases/tag/SOGo-5.12.8
- https://www.sogo.nu/news/2026/sogo-v5128-released.html
