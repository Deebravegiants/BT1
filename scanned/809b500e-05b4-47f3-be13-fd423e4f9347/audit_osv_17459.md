# [M] CVE-2020-15226

## Summary
Severity: Medium
Advisory: CVE-2020-15226
Aliases: GHSA-jwpv-7m4h-5gvc
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-10-07
Source: https://osv.dev/vulnerability/CVE-2020-15226
Type: osv

## Details
In GLPI before version 9.5.2, there is a SQL Injection in the API's search function. Not only is it possible to break the SQL syntax, but it is also possible to utilise a UNION SELECT query to reflect sensitive information such as the current database version, or database user. The most likely scenario for this vulnerability is with someone who has an API account to the system. The issue is patched in version 9.5.2. A proof-of-concept with technical details is available in the linked advisory.

## References
- https://github.com/glpi-project/glpi/commit/3dc4475c56b241ad659cc5c7cb5fb65727409cf0
- https://github.com/glpi-project/glpi/security/advisories/GHSA-jwpv-7m4h-5gvc
