# [H] Metabase vulnerable to Remote Code Execution via H2

## Summary
Severity: High
Advisory: CVE-2022-39361
Aliases: GHSA-gqpj-wcr3-p88v
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CVE-2022-39361
Type: osv

## Details
Metabase is data visualization software. Prior to versions 0.44.5, 1.44.5, 0.43.7, 1.43.7, 0.42.6, 1.42.6, 0.41.9, and 1.41.9, H2 (Sample Database) could allow Remote Code Execution (RCE), which can be abused by users able to write SQL queries on H2 databases. This issue is patched in versions 0.44.5, 1.44.5, 0.43.7, 1.43.7, 0.42.6, 1.42.6, 0.41.9, and 1.41.9. Metabase no longer allows DDL statements in H2 native queries.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39361.json
- https://github.com/metabase/metabase/security/advisories/GHSA-gqpj-wcr3-p88v
- https://nvd.nist.gov/vuln/detail/CVE-2022-39361
