# [H] ArcadeDB has cross-database IDOR: /ts/*, /batch/*, Prometheus and Grafana handlers bypass authorization

## Summary
Severity: High
Advisory: GHSA-x8mg-6r4p-87pf
CWE: CWE-200, CWE-285
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-x8mg-6r4p-87pf
Type: github-advisory

## Affected
- Maven: `com.arcadedb:arcadedb-server` — affected >=0 <26.7.2

## Details
About 14 HTTP handlers resolve the {database} path param and call getDatabase(...) WITHOUT user.canAccessToDatabase(...) and without setting the engine principal, because they extend AbstractServerHttpHandler directly instead of DatabaseAbstractHandler (which holds the only per-database gate at DatabaseAbstractHandler.java:69,88-90). Affected: PostBatchHandler:129, PostTimeSeriesWriteHandler:115, PostPrometheusWriteHandler:83, PostTimeSeriesQueryHandler:69, GetTimeSeriesLatestHandler:58, PostGrafanaQueryHandler:69, GetGrafanaHealthHandler:49, GetGrafanaMetadataHandler:52, GetPromQLQueryHandler:63, GetPromQLQueryRangeHandler:71, GetPromQLLabelsHandler:56, GetPromQLLabelValuesHandler:62, GetPromQLSeriesHandler:72, PostPrometheusReadHandler:85. The engine fallback is also void: LocalDatabase.checkPermissionsOnDatabase:711 early-returns when getCurrentUser()==null.

Exploit: a user authorized only for DB 'a' calls POST /api/v1/batch/b, POST /api/v1/ts/b/write, GET /api/v1/ts/b/prom/api/v1/query, POST /api/v1/ts/b/query -> full read AND write of DB 'b' (200 OK). The equivalent /api/v1/command/b correctly returns 403.

Fix: re-parent these handlers to DatabaseAbstractHandler, or add a shared resolveAuthorizedDatabase() choke point that enforces canAccessToDatabase and sets the engine principal before getDatabase(...). Fail closed when the security context is absent.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-x8mg-6r4p-87pf
- https://github.com/ArcadeData/arcadedb
- https://github.com/ArcadeData/arcadedb/releases/tag/26.7.2
