# [H] Piwigo: SQL Injection in pwg.users.getList API Method via filter Parameter

## Summary
Severity: High
Advisory: CVE-2026-27834
Aliases: GHSA-5jwg-cr5q-vjq2
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-27834
Type: osv

## Details
Piwigo is an open source photo gallery application for the web. Prior to version 16.3.0, a SQL Injection vulnerability exists in the pwg.users.getList Web Service API method. The filter parameter is directly concatenated into a SQL query without proper sanitization, allowing authenticated administrators to execute arbitrary SQL commands. This issue has been patched in version 16.3.0.

## References
- https://piwigo.org/release-16.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27834.json
- https://github.com/Piwigo/Piwigo/security/advisories/GHSA-5jwg-cr5q-vjq2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27834
- https://github.com/Piwigo/Piwigo/commit/9df471f16243371dc3725c5262e1632d23c8218a
