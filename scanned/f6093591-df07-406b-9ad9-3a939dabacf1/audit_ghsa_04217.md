# [M] NocoDB: Hidden Column Exposure in Public Shared View Endpoints

## Summary
Severity: Medium
Advisory: GHSA-4w6r-5c2j-qf5f
CVE: CVE-2026-47378
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-4w6r-5c2j-qf5f
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.04.1

## Details
### Summary
Public shared-view endpoints exposed values from columns that the view owner had
hidden, via three independent paths: groupBy returned raw values for any column
named in the request, filter and sort arrays operated on hidden columns enabling
boolean-blind extraction, and the related-data list accepted arbitrary link-column
IDs from other tables in the same base.

### Details
A new `sanitizeListArgsForPublicView` helper now strips request keys that should
never be caller-controlled (e.g. `getHiddenColumn`, `nested`), parses `where`
clauses against a restricted alias map that only contains visible columns, and
recursively removes filter/sort entries whose `fk_column_id` is not in the visible
set. `validateGroupByColumnNames` and `validateGroupColumnId` reject groupBy
requests whose `column_name` (CSV-style) or `groupColumnId` is not in the visible
or group-by column set. `relDataList` now checks `column.fk_model_id ===
currentModel.id` before resolving the linked table, matching the pre-existing
check on `publicMmList` and `publicHmList`.

### Impact
Anyone with a shared-view UUID could enumerate hidden-column values directly (via
groupBy), confirm hidden-column values by observing row counts (via filter), or
read records from unrelated tables in the same base (via the related-data list).
No authentication was required.

### Credit
This issue was reported by [@0xBassia](https://github.com/0xBassia).
It was independently reported by [@b-hermes](https://github.com/b-hermes).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-4w6r-5c2j-qf5f
- https://nvd.nist.gov/vuln/detail/CVE-2026-47378
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.04.1
