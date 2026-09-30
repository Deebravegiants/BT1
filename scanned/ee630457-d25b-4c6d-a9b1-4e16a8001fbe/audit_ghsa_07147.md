# [M] SurrealDB has an Authorization Bypass via Composite Record-id Paths

## Summary
Severity: Medium
Advisory: GHSA-6vg3-hgrw-p5gf
CWE: CWE-639, CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-6vg3-hgrw-p5gf
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
An authenticated user could bypass permission rules that gated access on parts of a record's id — most commonly tenant-isolation rules of the form `PERMISSIONS FOR select WHERE id.tenant = $auth.id.tenant`. The same defect also let UNIQUE constraints defined on parts of an id admit duplicate entries.

When a query referenced part of a composite record id (`id.tenant`, `id.uid`, …), SurrealDB read the value from the record's editable body fields instead of from the immutable id key. Because the body is editable but the id is fixed at creation, an attacker with write access could set the body field to any value and have permission checks read that spoofed value.

### Impact

What an attacker **can** do:

- Read records hidden by permission rules of the form `id.<field> = $auth.<...>` (typically tenant- or scope-isolation boundaries) by writing the same-named field on a record they control to the spoofed value.
- Cause UNIQUE constraints defined on `id.<field>` to silently admit duplicate entries, leaving the database with rows that violate the constraint.

What it **can't** do:

- Cross namespace or database isolation boundaries.
-Bypass field-level `PERMISSIONS FOR` update clauses that don't reference `id.<field>` paths.
- Affect availability or crash the server.

### Patches

The value-path resolver now special-cases `Part::Field` and `Part::Value` against `RecordIdKey::Object`, reading the named component directly from the id key without ever entering `select_document`. The Array-keyed special case (`id[0]`, `id[1]`, …) is unchanged.

- Versions 3.1.0 and later are not affected.

### Workarounds

Users unable to patch are advised to consider the following workarounds:
- Avoid permission expressions that read `id.<field>` on Object-keyed record ids; gate on the full record id (`id = $auth.id`) or on a server-derived session value instead.
- Avoid UNIQUE indexes on `id.<field>` until 3.1.0; use `DEFINE INDEX ... ON FIELDS id UNIQUE` (the full id) where possible.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-6vg3-hgrw-p5gf
- https://github.com/surrealdb/surrealdb/commit/1fcb19040bfffba92b3f69edb9b707d469e0027b
- https://github.com/surrealdb/surrealdb
