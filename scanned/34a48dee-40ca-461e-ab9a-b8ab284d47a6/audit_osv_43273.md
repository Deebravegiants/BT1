# [C] Twenty: SQL Injection in the `searchVector` Field Settings Allows Arbitrary PostgreSQL Execution

## Summary
Severity: Critical
Advisory: CVE-2026-73069
Aliases: GHSA-mm7j-q9q3-qqwj
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73069
Type: osv

## Details
Twenty is an open-source CRM (customer relationship management) platform. Prior to 2.15.0, Twenty allowed a workspace administrator with the DATA_MODEL permission to supply settings.asExpression for the system TS_VECTOR field searchVector through PATCH /rest/metadata/fields/:id or the updateOneField GraphQL mutation, causing buildSqlColumnDefinition in packages/twenty-server/src/engine/twenty-orm/workspace-schema-manager/utils/build-sql-column-definition.util.ts to concatenate unescaped input into GENERATED ALWAYS AS (...) and execute arbitrary PostgreSQL statements as the application database user. This issue is fixed in version 2.15.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73069.json
- https://github.com/twentyhq/twenty/security/advisories/GHSA-mm7j-q9q3-qqwj
- https://nvd.nist.gov/vuln/detail/CVE-2026-73069
- https://github.com/twentyhq/twenty/commit/0b8368cd6c1a47711bf52972800f162bde0bbab9
- https://github.com/twentyhq/twenty/pull/21947
