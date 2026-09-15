# [C] @hypequery/clickhouse has SQL Injection in parameter escaping that allows arbitrary SQL execution

## Summary
Severity: Critical
Advisory: GHSA-6wcc-39rp-hh9p
CVE: CVE-2026-54658
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-6wcc-39rp-hh9p
Type: github-advisory

## Affected
- npm: `@hypequery/clickhouse` — affected >=0 <2.5.1

## Details
A SQL injection vulnerability exists in the `escapeValue()` function used for parameter substitution. `escapeValue()` dispatches on the type of the parameter value, and two of its branches failed to escape safely. An attacker who can control a parameter value can terminate the enclosing string literal and have the rest of the value parsed as SQL.

**Vector 1 - string parameters. Fixed in 2.0.2.** The string branch escaped `'` as `''` but left `\\` untouched. ClickHouse honours C-style backslash escapes as well as SQL-standard quote doubling, so a value ending in an odd number of backslashes escapes the closing quote and the next parameter lands outside the literal:

```
where('a', 'eq', 'x\\')          ->   WHERE a = 'x\\' AND b = ' OR 1=1 --'
```

**Vector 2 - object and array parameters. Fixed in 2.5.1, NOT in 2.0.2.** The final branch of the same function rendered non-scalar values as `` `'${JSON.stringify(value)}'` `` with no escaping at all. JSON has no reason to escape the apostrophe, so any nested string containing `'` terminates the literal:

```
where('meta', 'eq', { k: \"x' OR 1=1 -- \" })
                                ->   WHERE meta = '{\"k\":\"x' OR 1=1 -- \"}'
```

The 2.0.2 patch changed only the string branch and did not address this. Vector 2 remained exploitable in **2.0.2, 2.1.0, 2.1.1, 2.1.2, 2.1.3, 2.2.0, 2.3.0, 2.4.0 and 2.5.0** - every release this advisory previously reported as patched.

**Who is impacted.** Any application on a version below 2.5.1 that passes user-controlled input as a query parameter. Both vectors are reachable through the documented public API: `.where(column, operator, value)`, the `in` operator, and `adapter.render()` / `rawQuery()`.

**Schema type declarations do not mitigate vector 2.** `createQueryBuilder().table()` builds its state with an empty column map, so the filter validator has no declared type to check against and returns without validating. Even where a schema is supplied, only `String`, `Int32`, `Int64`, `Float64` and `Date` columns are type-checked - `Map`, `Array`, `Bool`, `UUID`, `DateTime`, `UInt*`, `Enum` and `Nullable` columns are not - and any column name containing a `.` skips validation entirely.

## Patches

Upgrade to **2.5.1 or later**. Both vectors are closed there.

- **Vector 1** - fixed in **2.0.2** by `2dc1df7bae` (the referenced `4dfa9d77` is the same change
  on the pull-request branch). Escapes backslashes before escaping single quotes.
- **Vector 2** - fixed in **2.5.1** by `2879161a81`, which routes the serialised JSON back through  `escapeValue()` so nested quotes are doubled. The same commit also rejects non-finite numbers and  invalid `Date` values instead of emitting them into the query.

For anyone auditing the history: the vector-2 fix is bundled inside `2879161a81`, whose commit message is *\"parenthesize logical groups in WHERE to preserve AND/OR precedence (#349)\"*. Commit `4a1d4e38aa` (#350), whose message *does* describe the escaping fix, changes only a `bigint` branch - the escaping fix is already present in its parent.

## Workarounds

Upgrading is the only complete fix.

For **vector 2** only, applications on 2.0.2–2.5.0 that cannot upgrade can serialise non-scalar parameters themselves and pass the resulting string. That routes the value through the string branch, which is correctly escaped from 2.0.2 onward:

```js
.where('meta', 'eq', JSON.stringify(value))   // safe on >= 2.0.2
```

There is no workaround for **vector 1** other than upgrading to 2.0.2 or later.

Do not substitute application-level input validation or sanitisation for either fix. Correct escaping depends on the literal context the library constructs, so the library has to own it.

## References
- https://github.com/hypequery/hypequery/security/advisories/GHSA-6wcc-39rp-hh9p
- https://nvd.nist.gov/vuln/detail/CVE-2026-54658
- https://github.com/hypequery/hypequery/pull/349
- https://github.com/hypequery/hypequery/commit/2879161a810fed2c2222f785816ff05510976960
- https://github.com/hypequery/hypequery/commit/2dc1df7bae
- https://github.com/hypequery/hypequery/commit/4dfa9d77d70a08b970e722268b75ca7d13db0bdf
- https://github.com/hypequery/hypequery
- https://github.com/hypequery/hypequery/blob/main/packages/clickhouse/CHANGELOG.md#202
- https://github.com/hypequery/hypequery/releases/tag/@hypequery/clickhouse@2.0.2
- https://github.com/hypequery/hypequery/releases/tag/@hypequery/clickhouse@2.5.1
