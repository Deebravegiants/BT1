# [H] Lychee is vulnerable to an SQL Injection in explain DB queries.

## Summary
Severity: High
Advisory: CVE-2023-52082
Aliases: GHSA-rjwv-5j3m-p5x4
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-12-28
Source: https://osv.dev/vulnerability/CVE-2023-52082
Type: osv

## Details
Lychee is a free photo-management tool.  Prior to 5.0.2, Lychee is vulnerable to an SQL injection on any binding when using mysql/mariadb. This injection is only active for users with the `.env` settings set to DB_LOG_SQL=true and DB_LOG_SQL_EXPLAIN=true. The defaults settings of Lychee are safe.  The patch is provided on version 5.0.2.  To work around this issue, disable SQL EXPLAIN logging.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52082.json
- https://github.com/LycheeOrg/Lychee/security/advisories/GHSA-rjwv-5j3m-p5x4
- https://nvd.nist.gov/vuln/detail/CVE-2023-52082
- https://github.com/LycheeOrg/Lychee/commit/33354a2ce7cf700cc4ee537b7b8b94dfc1e84ad4
