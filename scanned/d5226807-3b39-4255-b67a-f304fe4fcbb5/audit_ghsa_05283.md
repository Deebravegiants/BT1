# [M] TypeORM: SQL Injection in UpdateQueryBuilder/SoftDeleteQueryBuilder orderBy (MySQL/MariaDB)

## Summary
Severity: Medium
Advisory: GHSA-9ggv-8w38-r7pm
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-9ggv-8w38-r7pm
Type: github-advisory

## Affected
- npm: `typeorm` — affected >=0.1.12 <0.3.29

## Details
### Impact

Blind SQL injection vulnerability in `UpdateQueryBuilder` and `SoftDeleteQueryBuilder` affecting MySQL and MariaDB users.

`UpdateQueryBuilder` and `SoftDeleteQueryBuilder` (including their `addOrderBy` variants) do not validate the `order` parameter against an allowlist of permitted values (`ASC`/`DESC`). The caller-supplied value is stored verbatim and concatenated directly into the generated SQL string without quoting or parameterization. `SelectQueryBuilder.orderBy` performs this validation correctly; the affected builders do not.

If any code path passes user-controlled input to `orderBy`/`addOrderBy` on an update or soft-delete query, an attacker can inject arbitrary SQL via the sort direction — even when the column name itself is hardcoded.

Demonstrated impact includes:
- **Data exfiltration** via time-based blind extraction (e.g. using `SLEEP()` to infer secret values bit by bit)
- **Row targeting manipulation** in queries using `LIMIT` patterns
- **Denial of service** via `SLEEP()`-based query exhaustion

CVSS 3.1: **8.6 (High)** — `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L`

Affected files (relative to commit `73fda419`):
- `src/query-builder/UpdateQueryBuilder.ts`: lines 383–419 and 718–744
- `src/query-builder/SoftDeleteQueryBuilder.ts`: lines 352–388 and 520–546

The vulnerability was introduced in commit `03799bd2` (v0.1.12) and is present through the latest release (v0.3.28).

### Patches

A fix has been released in 0.3.29 (1b66c44) and 1.0.0 (93eec63).

### Workarounds

Applications can manually validate the `order` argument before passing it to `orderBy` or `addOrderBy` on update or soft-delete query builders:

```ts
const direction = userInput.toUpperCase();
if (direction !== 'ASC' && direction !== 'DESC') {
  throw new Error('Invalid sort direction');
}
qb.orderBy(column, direction as 'ASC' | 'DESC');
```

Do not pass user-controlled values to `orderBy`/`addOrderBy` on `UpdateQueryBuilder` or `SoftDeleteQueryBuilder` without this validation.

### References

- Introduced in commit 03799bd2 (v0.1.12)
- Confirmed present in v0.3.28 (commit 73fda419)
- See `SelectQueryBuilder.orderBy` for the correct validation pattern this fix should mirror

## References
- https://github.com/typeorm/typeorm/security/advisories/GHSA-9ggv-8w38-r7pm
- https://github.com/typeorm/typeorm/commit/1b66c44d0410bdc56a0dcefb46be41867ec0fffc
- https://github.com/typeorm/typeorm/commit/93eec630630b219b162ba4e0c072afa851697cff
- https://github.com/typeorm/typeorm
