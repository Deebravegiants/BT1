# [H] Database bypassing any permissions in Metabase via SQlite attach

## Summary
Severity: High
Advisory: CVE-2022-24854
Aliases: GHSA-vm79-xvmp-7329
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-04-14
Source: https://osv.dev/vulnerability/CVE-2022-24854
Type: osv

## Details
Metabase is an open source business intelligence and analytics application. SQLite has an FDW-like feature called `ATTACH DATABASE`, which allows connecting multiple SQLite databases via the initial connection. If the attacker has SQL permissions to at least one SQLite database, then it can attach this database to a second database, and then it can query across all the tables. To be able to do that the attacker also needs to know the file path to the second database. Users are advised to upgrade as soon as possible. If you're unable to upgrade, you can modify your SQLIte connection strings to contain the url argument `?limit_attached=0`, which will disallow making connections to other SQLite databases. Only users making use of SQLite are affected.

## References
- https://www.sqlite.org/lang_attach.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24854.json
- https://github.com/metabase/metabase/security/advisories/GHSA-vm79-xvmp-7329
- https://nvd.nist.gov/vuln/detail/CVE-2022-24854
