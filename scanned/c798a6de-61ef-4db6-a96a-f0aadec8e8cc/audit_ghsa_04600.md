# [M] SurrealDB: Indexed ORDER BY leaks the value ordering of a SELECT-restricted field

## Summary
Severity: Medium
Advisory: GHSA-h4h3-3rfj-x6fq
CWE: CWE-200
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-h4h3-3rfj-x6fq
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=3.0.0 <3.1.5

## Details
A field can be hidden from a user with a field-level SELECT permission (`DEFINE FIELD code ON secret PERMISSIONS FOR select WHERE owner = $auth.id`). When that field is indexed, a record user who cannot read it could still recover the relative ordering of its values across every record by issuing `ORDER BY <field>`: the field came back `null` as intended, but the rows were returned in the hidden values' true sorted order.

To satisfy the sort, the planner selects the field's index and walks it in value order; the field-level permission is applied later, when the row is projected, so the value is nulled but the row order already encodes it. The guard that withholds restricted fields from the `WHERE` path was never applied to `ORDER BY`.

## Impact

What an attacker **can** do:

- As a record (scope) user with table SELECT, learn the relative ordering of a field hidden by a field-level SELECT permission, across other users' records, by ordering on it when an index covers the field — the value returns `null`, but the rows come back in the hidden values' order.
- With rows they control in the same table, use that ordering to narrow the hidden values toward exact ones.

What it **can't** do:

- Read the field value directly — only its relative ordering leaks; the projected value is correctly redacted.
- Cross table, record, or namespace/database boundaries — the table's SELECT permission and any row-level `WHERE` are still enforced, so only records the caller may already read are ordered.
- Leak anything when the restricted field is not indexed, affect root or record-owner sessions, or modify data (confidentiality only).

## Patches

The query planner now applies the field-permission guard to the `ORDER BY` clause as well as the `WHERE` clause. When an ordered field is hidden from the caller by a field-level SELECT permission, the index sort pushdown is withheld and the rows are sorted after redaction instead, so the row order no longer reflects the hidden values. The dynamic-scan fallback is closed the same way, and a regression test was added.

The fix is included in SurrealDB 3.1.5.

## Workarounds

Users unable to upgrade are advised to consider the following:

- Force the legacy executor with `SURREAL_PLANNER_STRATEGY=compute-only`; the sort then runs after redaction, so no ordering leaks.
- Do not place an index on a field whose values are hidden by a field-level SELECT permission — without the index the leak does not occur.
- Do not rely on field-level SELECT permissions to hide values on indexed fields from record users; restrict at the table level instead.
- Use namespace / database isolation as the primary trust boundary where feasible.

## References

- [SurrealQL Documentation — DEFINE FIELD](https://surrealdb.com/docs/surrealql/statements/define/field)
- [SurrealQL Documentation — DEFINE INDEX](https://surrealdb.com/docs/surrealql/statements/define/indexes)
- [SurrealQL Documentation — DEFINE TABLE … PERMISSIONS](https://surrealdb.com/docs/surrealql/statements/define/table)
- Related advisory (same class, indexed COUNT variant): [GHSA-c8jx-96c9-8xrp](https://github.com/surrealdb/surrealdb/security/advisories/GHSA-c8jx-96c9-8xrp)
- `fix(planner): prevent ORDER BY value-ordering oracle on restricted SELECT fields`
- `fix(planner): close ORDER BY value-ordering oracle on the DynamicScan fallback`

## Acknowledgements

Thanks to George Chen ([@geo-chen](https://github.com/geo-chen)) for finding and reporting this issue.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-h4h3-3rfj-x6fq
- https://github.com/surrealdb/surrealdb
