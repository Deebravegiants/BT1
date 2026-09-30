# [C] Twenty: SQL Injection via the timeZone field

## Summary
Severity: Critical
Advisory: CVE-2026-46624
Aliases: GHSA-jgx4-6mr9-9573
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-46624
Type: osv

## Details
Twenty is an open source CRM. From 1.7.7 through 1.16.7, a critical Remote Code Execution (RCE) vulnerability exists in Twenty CRM via a chained SQL Injection and PostgreSQL COPY TO PROGRAM attack. If Postgres user is a super user then any authenticated user can execute arbitrary OS commands on the database server by injecting SQL through the unsanitized timeZone parameter in the REST API groupBy endpoint. The timeZone field within the group_by query parameter is directly interpolated into a raw SQL expression using JavaScript template literals without any parameterization, validation, or escaping. This affects engine/api/graphql/graphql-query-runner/group-by/resolvers/utils/get-group-by-expression.util.ts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46624.json
- https://github.com/twentyhq/twenty/security/advisories/GHSA-jgx4-6mr9-9573
- https://nvd.nist.gov/vuln/detail/CVE-2026-46624
