# [H] Piwigo: SQL Injection in Activity.getList

## Summary
Severity: High
Advisory: CVE-2026-27885
Aliases: GHSA-wfmr-9hg8-jh3m
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-27885
Type: osv

## Details
Piwigo is an open source photo gallery application for the web. Prior to version 16.3.0, a SQL Injection vulnerability was discovered in Piwigo affecting the Activity List API endpoint. This vulnerability allows an authenticated administrator to extract sensitive data from the database, including user credentials, email addresses, and all stored content. This issue has been patched in version 16.3.0.

## References
- https://piwigo.org/release-16.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27885.json
- https://github.com/Piwigo/Piwigo/security/advisories/GHSA-wfmr-9hg8-jh3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-27885
- https://github.com/Piwigo/Piwigo/commit/c172d284e11eab4a5dbadd2844d26f734d5c8c72
