# [H] Dgraph Vulnerable to DQL Injection via checkUserPassword GraphQL Query

## Summary
Severity: High
Advisory: GHSA-q2m9-6jp9-c6mc
CVE: CVE-2026-44840
CWE: CWE-943
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-29
Source: https://github.com/advisories/GHSA-q2m9-6jp9-c6mc
Type: github-advisory

## Affected
- Go: `github.com/dgraph-io/dgraph/v25` — affected >=0 <25.3.4

## Details
## Summary

The `checkUserPassword` GraphQL query in Dgraph is vulnerable to DQL (Dgraph Query Language) injection. User-supplied password values are interpolated directly into a DQL `checkpwd()` query via `fmt.Sprintf` without any escaping or parameterization. An attacker can inject a password containing a double-quote character to break out of the DQL string literal and append arbitrary DQL query blocks.

## Details

### Vulnerable Code Path

The vulnerability exists in the GraphQL-to-DQL query rewriting layer:

1. **`query_rewriter.go` (~line 364)** — The `checkpwd()` DQL function is constructed using `fmt.Sprintf`:

   ```go
   fmt.Sprintf(`checkpwd(User.password, "%s")`, password)
   ```

   The raw password string from the GraphQL query input is embedded directly into the DQL query without escaping double quotes or other special characters.

2. **`graphquery.go`** — The constructed query attribute is serialized into the final DQL string via `b.WriteString(query.Attr)`, passing the unsanitized content directly to the Dgraph query engine.

### Attack Mechanism

A password value containing a double-quote (`"`) terminates the string literal in the `checkpwd()` function. Any content after the escaped quote is parsed as additional DQL, allowing the attacker to inject arbitrary query blocks.

### Distinction from CVE-2026-41328 and CVE-2026-41327

CVE-2026-41328 and CVE-2026-41327 address DQL injection in **`edgraph/server.go`**, where GraphQL mutation inputs (upsert/delete) are embedded unsafely into DQL mutations. Those fixes sanitize the mutation path.

This vulnerability is in a **completely different code path** — the **GraphQL query rewriter** (`query_rewriter.go` → `graphquery.go`). The `checkUserPassword` GraphQL query triggers a DQL *query* via `checkpwd()`, and this query construction was not covered by the patches for CVE-2026-41328/CVE-2026-41327.

## PoC

```bash
curl -s -X POST http://TARGET:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{ "query": "query { checkUserPassword(name: \"admin\", password: \"x\\\") { uid } injected(func: has(User.name)) { User.name User.email } dummy(func: eq(x, \\\"x\") { msg } }") { msg } }" }'
```

**What to observe:**

- The `touched_uids` field in the `extensions` section of the response will be elevated (indicating the injected blocks executed)
- Dgraph server logs (`dgraph alpha` output) will show the injected query blocks being parsed and executed
- The response itself may be filtered by the GraphQL layer, but server-side execution is confirmed

## Impact

- **Data enumeration**: Injected query blocks execute server-side and can probe for the existence of predicates, types, and nodes via `touched_uids` metrics and server logs.
- **Schema discovery**: An attacker can enumerate all predicates and types in the database by injecting `schema {}` blocks or `has()` queries.
- **Resource exhaustion**: Expensive injected queries (recursive traversals, large aggregations) execute at the DQL layer, consuming server resources regardless of whether results are returned to the attacker.
- **Potential data disclosure**: Depending on Dgraph configuration (e.g., debug mode, custom extensions), injected query results may leak into the response.

**CVSS 3.1: 7.5 High** — `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`

- Network-accessible via any GraphQL endpoint
- No authentication required (`checkUserPassword` is an unauthenticated query)
- Low attack complexity (single crafted HTTP request)
- High confidentiality impact (server-side query execution confirmed, data enumeration possible)

## Affected Versions

All versions of Dgraph that include GraphQL support with the `@secret` directive are affected:

- <= v25.3.3
- Any version where `query_rewriter.go` constructs `checkpwd()` via string interpolation

## Suggested Fix

Escape or parameterize the password value before embedding it in the DQL query. At minimum, double-quote characters in the password must be escaped:

```go
// Before (vulnerable):
fmt.Sprintf(`checkpwd(User.password, "%s")`, password)

// After (escaped):
escaped := strings.ReplaceAll(password, `\`, `\\`)
escaped = strings.ReplaceAll(escaped, `"`, `\"`)
fmt.Sprintf(`checkpwd(User.password, "%s")`, escaped)
```

Ideally, Dgraph should implement parameterized query support for the `checkpwd()` function to avoid string interpolation entirely, consistent with best practices for injection prevention.

## Credit

Kai Aizen (kai.aizen.dev@gmail.com)

## References
- https://github.com/dgraph-io/dgraph/security/advisories/GHSA-q2m9-6jp9-c6mc
- https://github.com/dgraph-io/dgraph/commit/cee702c93f141eeb0c96a81f70830ec9e459efac
- https://github.com/dgraph-io/dgraph
- https://github.com/dgraph-io/dgraph/releases/tag/v25.3.4
