# [H] Centreon Command Injection

## Summary
Severity: High
Advisory: GHSA-c4fj-3wqq-g9c9
CVE: CVE-2015-1561
CWE: CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-c4fj-3wqq-g9c9
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=0 <2.8.28

## Details
The `escape_command` function in `include/Administration/corePerformance/getStats.php` in Centreon (formerly Merethis Centreon) 2.5.4 and earlier (offending file deleted in Centreon 19.10.0) uses an incorrect regular expression, which allows remote authenticated users to execute arbitrary commands via shell metacharacters in the `ns_id` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1561
- https://github.com/centreon/centreon-archived/pull/7083
- https://github.com/centreon/centreon-archived/pull/7271
- https://github.com/centreon/centreon-archived/commit/387dffdd051dbc7a234e1138a9d06f3089bb55bb
- https://github.com/centreon/centreon-archived/commit/a78c60aad6fd5af9b51a6d5de5d65560ea37a98a
- https://forge.centreon.com/projects/centreon/repository/revisions/387dffdd051dbc7a234e1138a9d06f3089bb55bb
- https://github.com/centreon/centreon-archived
- https://web.archive.org/web/20201125112637/http://www.securityfocus.com/archive/1/535961/100/0/threaded
- http://packetstormsecurity.com/files/132607/Merethis-Centreon-2.5.4-SQL-Injection-Remote-Command-Execution.html
