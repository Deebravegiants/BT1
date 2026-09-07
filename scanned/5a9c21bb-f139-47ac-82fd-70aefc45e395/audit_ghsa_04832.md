# [M] NocoDB: Postgres SQL Injection in Formula `ARRAYSORT`

## Summary
Severity: Medium
Advisory: GHSA-cxv7-gmmp-228p
CVE: CVE-2026-47375
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-cxv7-gmmp-228p
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.04.1

## Details
### Summary

An authenticated user with `columnAdd` permission on a Postgres-backed base can inject arbitrary SQL into the formula engine via the optional `direction` argument of `ARRAYSORT(...)`. The value is unrestricted by formula validation and embedded into a `knex.raw` `ORDER BY` clause, executing during column creation and on every subsequent record read of the formula column.

### Details

The vulnerability is specific to the Postgres mapping for `ARRAYSORT` in `packages/nocodb/src/db/functionMappings/pg.ts`. Two factors combine:

1. `ARRAYSORT` declares only argument count, not `validation.args.type`, so `validate-extract-tree.ts` does not enforce an allowlist on the second argument.
2. The Postgres mapping then passes the attacker-controlled value through `sanitize(knex.raw(...))` into a raw SQL fragment:

```ts
const direction = pt.arguments[1]
  ? sanitize(
      knex.raw(pt.arguments[1]?.value ?? (await fn(pt.arguments[1])).builder),
    )
  : knex.raw('asc');

return {
  builder: knex.raw(`ARRAY(SELECT UNNEST(??) ORDER BY 1 ??)`, [source, direction]),
};
```

`sanitize()` in `sqlSanitize.ts` only escapes `?` placeholder characters; it does not validate SQL syntax. A payload such as `"desc, (SELECT COUNT(*) FROM generate_series(1,30000000))"` is accepted, persisted, and re-executed on every read of the formula column.

### Impact

- Authenticated SQL injection against Postgres-backed bases.
- Requires `columnAdd` permission (creator/owner-level).
- Proven impact: attacker-controlled heavy SQL causing multi-second query stalls (DoS).
- Potentially extendable to broader SQL injection outcomes depending on database permissions and deployment hardening.
- Limited to Postgres backends.

### Credit

This issue was reported by [@leduckhuong](https://github.com/leduckhuong).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-cxv7-gmmp-228p
- https://nvd.nist.gov/vuln/detail/CVE-2026-47375
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.04.1
