# [H] CVE-2016-9282

## Summary
Severity: High
Advisory: CVE-2016-9282
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-11-11
Source: https://osv.dev/vulnerability/CVE-2016-9282
Type: osv

## Details
SQL Injection in framework/modules/search/controllers/searchController.php in Exponent CMS v2.4.0 allows remote attackers to read database information via action=search&module=search with the search_string parameter.

## References
- http://www.securitytracker.com/id/1037281
- http://www.securityfocus.com/bid/94296
- https://github.com/exponentcms/exponent-cms/commit/e83721a5b9fcc88e1141a8fb29c3d1bd522257c1
