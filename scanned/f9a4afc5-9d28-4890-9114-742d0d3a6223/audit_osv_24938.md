# [M] Sensitive information disclosure possible on misconfigured failed backups of non-H2 databases in gocd

## Summary
Severity: Medium
Advisory: CVE-2023-28630
Aliases: GHSA-p95w-gh78-qjmv
CVSS: 4.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-28630
Type: osv

## Details
GoCD is an open source continuous delivery server. In GoCD versions from 20.5.0 and below 23.1.0, if the server environment is not correctly configured by administrators to provide access to the relevant PostgreSQL or MySQL backup tools, the credentials for database access may be unintentionally leaked to admin alerts on the GoCD user interface. The vulnerability is triggered only if the GoCD server host is misconfigured to have backups enabled, but does not have access to the `pg_dump` or `mysqldump` utility tools to backup the configured database type (PostgreSQL or MySQL respectively). In such cases, failure to launch the expected backup utility reports the shell environment used to attempt to launch in the server admin alert, which includes the plaintext database password supplied to the configured tool. This vulnerability does not affect backups of the default on-disk H2 database that GoCD is configured to use. This issue has been addressed and fixed in GoCD 23.1.0. Users are advised to upgrade. Users unable to upgrade may disable backups, or administrators should ensure that the required `pg_dump` (PostgreSQL) or `mysqldump` (MySQL) binaries are available on the GoCD server when backups are triggered.

## References
- https://github.com/gocd/gocd/releases/tag/23.1.0
- https://www.gocd.org/releases/#23-1-0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28630.json
- https://github.com/gocd/gocd/security/advisories/GHSA-p95w-gh78-qjmv
- https://nvd.nist.gov/vuln/detail/CVE-2023-28630
- https://github.com/gocd/gocd/commit/6545481e7b36817dd6033bf614585a8db242070d
