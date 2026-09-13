# [H] OneUptime ClickHouse vulnerable to SQL Injection via unvalidated column identifiers in sort, select, and groupBy parameters

## Summary
Severity: High
Advisory: GHSA-gcg3-c5p2-cqgg
CVE: CVE-2026-33142
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-gcg3-c5p2-cqgg
Type: github-advisory

## Affected
- npm: `oneuptime` — affected >=0 <10.0.34

## Details
The fix for GHSA-p5g2-jm85-8g35 (ClickHouse SQL injection via aggregate query parameters) added column name validation to the `_aggregateBy` method but did not apply the same validation to three other query construction paths in `StatementGenerator`. The `toSortStatement`, `toSelectStatement`, and `toGroupByStatement` methods accept user-controlled object keys from API request bodies and interpolate them as ClickHouse `Identifier` parameters without verifying they correspond to actual model columns.

ClickHouse Identifier parameters are substituted directly into queries without escaping, so an attacker who can reach any analytics list or aggregate endpoint can inject arbitrary SQL through crafted `sort`, `select`, or `groupBy` keys.

## Details

### Root cause

`StatementGenerator.ts` has four methods that iterate over user-provided object keys to build SQL:

| Method | Validates keys? |
|--------|----------------|
| `toWhereStatement` (line 292) | Yes - calls `this.model.getTableColumn(key)` |
| `toSortStatement` (line 467) | **No** |
| `toSelectStatement` (line 483) | **No** |
| `toGroupByStatement` (line 451) | **No** |

In `Statement.ts`, when a value passed to the `SQL` tagged template is a string, it receives the `Identifier` data type (line 40). Per [ClickHouse documentation](https://clickhouse.com/docs/en/sql-reference/syntax#defining-and-using-query-parameters), Identifier parameters are substituted directly into the query without quoting or escaping. This is correct for trusted column names but unsafe for user input.

### Input flow

`BaseAnalyticsAPI.ts` deserializes `sort`, `select`, and `groupBy` directly from `req.body` (lines 239-253) and passes them to the service layer without column validation:

```typescript
sort = JSONFunctions.deserialize(req.body["sort"]) as Sort<AnalyticsDataModel>;
select = JSONFunctions.deserialize(req.body["select"]) as Select<AnalyticsDataModel>;
groupBy = JSONFunctions.deserialize(req.body["groupBy"]) as GroupBy<AnalyticsDataModel>;
```

### Affected endpoints

Any endpoint backed by `BaseAnalyticsAPI.getList()` or `BaseAnalyticsAPI.getAggregate()` - this includes analytics queries for logs, metrics, spans, and exceptions.

## Impact

An authenticated user can inject arbitrary ClickHouse SQL through crafted column names in sort, select, or groupBy request parameters. This allows reading, modifying, or deleting analytics data (logs, metrics, traces) stored in ClickHouse. PostgreSQL data is not affected (separate query path).

## Suggested Fix

Add the same `getTableColumn()` validation already present in `toWhereStatement` to the three unvalidated methods:

```typescript
// toSortStatement, toSelectStatement, toGroupByStatement
for (const key in sort) {
  if (!this.model.getTableColumn(key)) {
    throw new BadDataException(`Unknown column: ${key}`);
  }
  // existing logic
}
```

This matches the pattern used in the GHSA-p5g2 fix for `_aggregateBy` and the existing `toWhereStatement` validation.

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-gcg3-c5p2-cqgg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33142
- https://github.com/OneUptime/oneuptime
