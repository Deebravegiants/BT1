# [H] Piwigo SQL Injection vulnerability in "User-Agent"

## Summary
Severity: High
Advisory: CVE-2023-37270
Aliases: GHSA-934w-qj9p-3qcx
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2023-07-07
Source: https://osv.dev/vulnerability/CVE-2023-37270
Type: osv

## Details
Piwigo is open source photo gallery software. Prior to version 13.8.0, there is a SQL Injection vulnerability in the login of the administrator screen. The SQL statement that acquires the HTTP Header `User-Agent` is vulnerable at the endpoint that records user information when logging in to the administrator screen. It is possible to execute arbitrary SQL statements. Someone who wants to exploit the vulnerability must be log in to the administrator screen, even with low privileges. Any SQL statement can be executed. Doing so may leak information from the database. Version 13.8.0 contains a fix for this issue. As another mitigation, those who want to execute a SQL statement verbatim with user-enterable parameters should be sure to escape the parameter contents appropriately.

## References
- https://github.com/Piwigo/Piwigo/blob/c01ec38bc43f09424a8d404719c35f963d63cf00/include/dblayer/functions_mysqli.inc.php#L491
- https://github.com/Piwigo/Piwigo/blob/c01ec38bc43f09424a8d404719c35f963d63cf00/include/functions.inc.php#L621
- https://piwigo.org/release-13.8.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37270.json
- https://github.com/Piwigo/Piwigo/security/advisories/GHSA-934w-qj9p-3qcx
- https://nvd.nist.gov/vuln/detail/CVE-2023-37270
- https://github.com/Piwigo/Piwigo/commit/978425527d6c113887f845d75cf982bbb62d761a
