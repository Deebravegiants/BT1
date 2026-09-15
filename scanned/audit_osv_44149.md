# [M] StarRocks through 4.0.13 Missing Authorization on DROP MATERIALIZED VIEW for Legacy Synchronous Materialized Views

## Summary
Severity: Medium
Advisory: CVE-2026-80346
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80346
Type: osv

## Details
StarRocks performs no privilege check when a legacy synchronous materialized view is dropped. Every other statement type routed through AuthorizerStmtVisitor calls into Authorizer before execution, but visitDropMaterializedViewStatement returns immediately with a comment stating the check happens in execution logic. That holds only for asynchronous materialized views: LocalMetastore.dropMaterializedView calls Authorizer.checkMaterializedViewAction inside a branch taken when the resolved table is a MaterializedView. A legacy synchronous materialized view is stored as a rollup index on an OlapTable rather than a MaterializedView, so the other branch runs, reaching AlterJobMgr.processDropMaterializedView and MaterializedViewHandler, neither of which contains any Authorizer call. The former locates the target by scanning every OlapTable in the named database for a matching rollup index, and the latter validates only table state and name conflicts. Any authenticated account can therefore drop a legacy synchronous materialized view belonging to any database, holding no grant on the view, the base table or the database, and the drop is indistinguishable from an authorized one.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80346.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80346
- https://www.vulncheck.com/advisories/starrocks-through-4.0.13-missing-authorization-on-drop-materialized-view-for-legacy-synchronous-materialized-views
- https://github.com/StarRocks/starrocks/issues/76566
- https://github.com/StarRocks/starrocks
- https://github.com/StarRocks/starrocks/blob/3.5.19/fe/fe-core/src/main/java/com/starrocks/alter/AlterJobMgr.java
- https://github.com/StarRocks/starrocks/blob/3.5.19/fe/fe-core/src/main/java/com/starrocks/sql/analyzer/AuthorizerStmtVisitor.java
