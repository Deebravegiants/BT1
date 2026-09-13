# [H] SiYuan: Second-order SSTI to arbitrary SQL via attribute-view template column (queryBlocks): malicious imported package executes SQL on victim kernel

## Summary
Severity: High
Advisory: GHSA-x67c-8pwr-m8g3
Aliases: CVE-2026-72807, GO-2026-6410
Ecosystem: Go
Published: 2026-09-03
Source: https://osv.dev/vulnerability/GHSA-x67c-8pwr-m8g3
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260723035036-0a176345e02a

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72807](https://nvd.nist.gov/vuln/detail/CVE-2026-72807).

### Summary

Attribute-view (AV) template columns are live-evaluated on every render and expose the `queryBlocks` template function, which runs raw SQL on the read-write database handle (`SelectBlocksRawStmt`, using `?`→argument string substitution rather than parameter binding). AV mutations are admin-gated, so this is not directly reader-injectable but it is a second-order vector: an attacker distributes a SiYuan document or AV package whose template column contains `.action{queryBlocks "<arbitrary SQL>"}` when a victim imports the package and renders the AV, the attacker's SQL executes on the victim's kernel (read and, via statement stacking, write).

### Details

Doc-level `{{…}}` templates are rendered at insert-time and become static, so they are not re-evaluated on reader view. The residual is AV template columns, which are live-evaluated at render. `queryBlocks` passes its argument to `SelectBlocksRawStmt` with `?`→arg string substitution, not a bound parameter, on the main read-write handle (`88250/go-sqlite3` fork, statement-stacking capable) so an attacker-controlled template argument becomes arbitrary SQL.

The SSTI surface is otherwise hardened: `BuiltInTemplateFuncs` deletes `env`, `expandenv`, and `getHostByName` so there is no environment/host/file/exec SSTI. `queryBlocks`-to-SQL is the remaining live-evaluated sink.

### Proof of Concept

An AV template column set to `.action{queryBlocks "<sql>"}` executes `<sql>` against the read-write handle when the AV is rendered. Delivered second-order: a shared/imported document or AV package carrying such a column runs the embedded SQL on any kernel that imports and renders it.

### Proof of Concept

Reproduced on a live instance.

**1. Host doc + AV (admin, 6806):**
```
POST /api/filetree/createDocWithMd {notebook, path:"/ssti-poc", markdown:"host"}  → DOC
POST /api/av/renderAttributeView   {id:"<AV>"}   # materializes the AV
```

**2. Plant the malicious template column (one performTransactions call):**
```json
{"reqId":1,"session":"poc","transactions":[{"doOperations":[
  {"action":"addAttrViewCol","avID":"<AV>","id":"<COL>","name":"tpl","type":"template"},
  {"action":"updateAttrViewColTemplate","avID":"<AV>","id":"<COL>","type":"template",
   "data":".action{range queryBlocks \"SELECT * FROM blocks WHERE root_id='<PROTECTED_DOC_ID>'\"}.action{.Markdown} .action{end}"},
  {"action":"insertAttrViewBlock","avID":"<AV>","isDetached":true}
]}]}
```

**3. Trigger (render evaluates the template):**
```
POST /api/av/renderAttributeView {id:"<AV>"}
```
Result: the template cell renders `## LockedSection TOP_SECRET…` the `queryBlocks` SQL executed and returned the password-protected document's content, arbitrary SQL via template reading across the publish/password boundary. `queryBlocks` uses `?`→arg string substitution (not parameterized), so UNION and stacked writes are also possible. Delivered second-order, the same column executes on any kernel that imports and renders the AV.

### Impact

An attacker who gets a victim to import a crafted document/AV package and render it achieves arbitrary SQL execution on the victim's kernel cross-notebook read and via stacking, write. Precondition is content delivery plus render (import of an attacker-supplied package), which bounds severity to Medium. Not directly reachable by an anonymous reader (AV creation is admin-gated); the injection travels in stored/imported template content.

### Suggested fix

Parameterize `queryBlocks` bind the argument rather than substituting it into the SQL string or restrict the template function set available in AV columns as was done for the doc-template functions. Treat imported template content as untrusted at render time.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-x67c-8pwr-m8g3
- https://nvd.nist.gov/vuln/detail/CVE-2026-72807
- https://github.com/siyuan-note/siyuan/commit/0a176345e02a0d19bdc7762e50e0b92002087d20
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-sql-injection-via-queryblocks-template
