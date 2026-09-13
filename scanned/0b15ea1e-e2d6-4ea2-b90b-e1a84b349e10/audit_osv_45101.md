# [C] SiYuan: SQL injection in backlink/mention search via unescaped stored and client input (publish mode): first-order (client keyword) and second-order (stored document title) breakout on read-write handle

## Summary
Severity: Critical
Advisory: GHSA-q2vg-7qgx-x5fc
Aliases: CVE-2026-72811, GO-2026-6402
Ecosystem: Go
Published: 2026-09-03
Source: https://osv.dev/vulnerability/GHSA-q2vg-7qgx-x5fc
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260723004839-1a5b3431d5ab

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72811](https://nvd.nist.gov/vuln/detail/CVE-2026-72811).

### Summary

The backlink/mention search query (`kernel/model/backlink.go`) concatenates stored block metadata (title, name, alias, anchor text) and the client-supplied keyword into a SQL `MATCH`/search statement, escaping only the double-quote character (`"`) and not the single quote (`'`). A single quote in either the client keyword or in stored document metadata breaks out of the string literal. The query runs on the main read-write `siyuan.db` handle through a statement-stacking-capable driver.

This yields two vectors:
- **First-order:** a client-supplied keyword containing `'` injects directly. This path is reachable by an anonymous reader on the publish surface.
- **Second-order:** a document whose title/name/alias contains `'` is stored safely (indexing uses parameterized inserts) but detonates when that stored value is later concatenated into the backlink query including on another user's kernel that has ingested the malicious document.

### Details

**Storage is safe; reuse is not.** Indexing INSERTs (`kernel/sql/upsert.go`) are parameterized (`(?,?,…)` with bound arguments for `Name`/`Content`/`Markdown`/`IAL`), so malicious `.sy` content is stored intact and safely. The injection is in the *reuse* path: the backlink/mention MATCH query (`kernel/model/backlink.go`, around line 980) builds its condition by concatenating the stored title/name/alias/anchor and the client keyword, applying only `"`→escaping and not `'`. A `'` in either source terminates the literal and lands in SQL context.

**Sink / handle.** The concatenated statement reaches `SelectBlocksRawStmtNoParse` → `query()` on the global read-write `siyuan.db` handle (DSN has no `mode=ro`/`_query_only`), driven by the vendored `88250/go-sqlite3` fork whose connection `query` loops over `;`-separated statements (stacking possible). Ceiling is arbitrary SQL cross-notebook read and write.

**Route / auth tier.** The backlink/mention family (`getBacklink`, `getBacklink2`, `getBacklinkDoc`, `getBackmentionDoc`) is `CheckAuth`-only, so the first-order client-keyword vector is reachable by the publish `RoleReader` token and by the anonymous account when `Publish.Auth.Enable` is `false`.

**Scope of the injection surface (confirmed the only second-order sink).** A sweep of the query paths that reuse stored content confirmed this is the sole injectable reuse sink: indexing INSERTs are parameterized, tag search uses `content LIKE ?` with pattern escaping, virtual refs use in-memory matching (no SQL), `IN(...)` joins use node-IDs/hex-hashes/ROWIDs (no quote surface), and the graph name/content filter escapes `'`. Only the backlink/mention MATCH path concatenates with `'` unescaped.

### Proof of Concept

Reproduced on a local instance (SiYuan running locally, publish mode enabled on port 6808, publish Basic Auth disabled). Strictly non-destructive verification, a syntax-error probe and a stored-value observation; no UNION exfiltration, no write, no DDL.

**First-order (client keyword), anonymous reader on port 6808:**
```
POST http://127.0.0.1:6808/api/ref/getBacklink2
{"id":"<block id>","k":"a'b","mk":""}
```
The keyword `a'b` reaches the concatenated `MATCH` condition and produces a SQL parse error, confirming the single quote breaks out of the literal and the client keyword lands in SQL context.

**Second-order (stored title), setup via admin then observed anonymously:**
A document whose title contains a single quote e.g. `("locked-doc")` style metadata is stored safely by the parameterized indexer, then appears at the exact unescaped position in the backlink query when that document participates in a backlink/mention lookup, breaking the query the same way. This demonstrates that stored document metadata detonates on reuse, independent of the client keyword.

Verification was limited to the syntax-error probe and the stored-value position observation; no exfiltration or write statement was executed. Full reproduction detail available privately on request.

### Impact

**First-order:** an anonymous reader (publish mode with auth disabled) or any publish `RoleReader` injects arbitrary SQL into the backlink/mention query via the keyword parameter, on the read-write main handle: cross-notebook read disclosure and, via statement stacking, write and `ATTACH`. This is the same anonymous-arbitrary-SQL severity as the search/embed injection findings, on a different sink.

**Second-order:** a document whose title/name/alias contains injection content is stored safely but executes when that stored value is concatenated into the backlink query. This fires on any kernel that has ingested the malicious document for example via a shared or imported `.sy` file, sync, or an opened `.sy.zip`. The precondition here is content delivery into the victim workspace (not a direct anonymous request), so it is a distinct, delivery-dependent threat model from the first-order vector.

Encrypted notebooks are out of scope; code execution is not reachable in the default build (no `load_extension`).

**Distinctness from the other SQL findings:** this is a different sink (`backlink.go` MATCH query) from the `searchDocs` (`LIKE` keyword), `searchEmbedBlock` (verbatim stmt), and `getEmbedBlock` (`IN`-clause ID array) findings, and it is the only one with a second-order (stored-content) vector. A fix to any of those does not remediate this path.

### Suggested fix

Parameterize the backlink/mention query bind the keyword and any stored metadata as placeholders rather than concatenating or escape `'` (and use `LIKE`-pattern escaping) consistently, matching the tag-search and graph-filter paths that already do so. The second-order vector specifically requires that stored metadata be bound rather than concatenated, since escaping at storage time is not the defense (storage is already safe); the fix must be at the query-construction site.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-q2vg-7qgx-x5fc
- https://nvd.nist.gov/vuln/detail/CVE-2026-72811
- https://github.com/siyuan-note/siyuan/commit/1a5b3431d5ab3036b19c1cc79486fedd6906fb57
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-sql-injection-via-backlink-search
