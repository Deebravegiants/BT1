# [H] Budibase: Snowflake private key returned unmasked from datasource API to BASIC users

## Summary
Severity: High
Advisory: CVE-2026-46427
Aliases: GHSA-qv26-4hvj-m7fv
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46427
Type: osv

## Details
Budibase is an open-source low-code platform. Prior to 3.38.3, removeSecrets at packages/server/src/sdk/workspace/datasources/datasources.ts masks only datasource config fields whose schema type is DatasourceFieldType.PASSWORD. The Snowflake integration types its privateKey field as SENSITIVE_LONGFORM, which the filter skips. GET /api/datasources/:datasourceId lives on authorizedRoutes guarded by PermissionType.TABLE + PermissionLevel.READ. An authenticated BASIC user with any app role and call the endpoint and receive the full Snowflake PEM in plaintext. This vulnerability is fixed in 3.38.3.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-qv26-4hvj-m7fv
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46427.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46427
