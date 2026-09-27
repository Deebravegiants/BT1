# [C] SQL Injection vulnerability via sortBy in beanFeed

## Summary
Severity: Critical
Advisory: CVE-2026-40329
Aliases: GHSA-3xpq-q494-8qq4
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-40329
Type: osv

## Details
Masa CMS is an open source content management system. In versions 7.5.2 and earlier, a SQL injection vulnerability exists in the beanFeed.cfc component within the getQuery function's processing of the sortBy parameter. The application fails to properly sanitize or parameterize this input before incorporating it into dynamic SQL statements. An unauthenticated remote attacker can execute arbitrary SQL commands against the database, potentially gaining access to sensitive data, modifying or deleting records, or escalating privileges to administrative control.

This issue has been fixed in versions 7.2.10, 7.3.15, 7.4.10, and 7.5.3. As a workaround, configure WAF rules to block malicious SQL patterns in the sortBy parameter sent to beanFeed.cfc.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40329.json
- https://github.com/MasaCMS/MasaCMS/security/advisories/GHSA-3xpq-q494-8qq4
- https://nvd.nist.gov/vuln/detail/CVE-2026-40329
