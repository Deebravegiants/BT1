# [M] MariaDB Server Audit Plugin Comment Handling Bypass

## Summary
Severity: Medium
Advisory: BIT-mariadb-2026-3494
Aliases: BIT-mariadb-min-2026-3494, BIT-mysql-client-2026-3494, CVE-2026-3494
Ecosystem: Bitnami
Published: 2026-03-10
Source: https://osv.dev/vulnerability/BIT-mariadb-2026-3494
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=11.5.0 <11.8.6

## Details
In MariaDB server version through 11.8.5, when server audit plugin is enabled with server_audit_events variable configured with QUERY_DCL, QUERY_DDL, or QUERY_DML filtering, if an authenticated database user invokes a SQL statement prefixed with double-hyphen (—) or hash (#) style comments, the statement is not logged.

## References
- https://aws.amazon.com/security/security-bulletins/2026-006-AWS/
- https://nvd.nist.gov/vuln/detail/CVE-2026-3494
- https://github.com/MariaDB/server/commit/635559a2ad68a5a6d1a354e8209c58323dba0261
- https://github.com/aws/audit-plugin-for-mysql/commit/01e25a5cb1073f131eea774c06c8a056b1e4b2ff
