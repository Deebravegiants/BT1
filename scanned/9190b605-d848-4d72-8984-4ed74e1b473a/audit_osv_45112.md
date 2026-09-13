# [M] SiYuan: Missing authorization on refreshBacklink allows anonymous readers to trigger persistent server-side writes and unauthenticated resource amplification (publish mode)

## Summary
Severity: Medium
Advisory: GHSA-wgwx-479j-23vq
Aliases: CVE-2026-72812, GO-2026-6408
Ecosystem: Go
Published: 2026-09-03
Source: https://osv.dev/vulnerability/GHSA-wgwx-479j-23vq
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260723002528-7d273c271ce1

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72812](https://nvd.nist.gov/vuln/detail/CVE-2026-72812).

### Summary

The `/api/ref/refreshBacklink` endpoint is gated by `CheckAuth` only. Unlike its mutating siblings, it carries no `CheckAdminRole`, no `CheckReadonly`, and no inline reader-role guard so it falls through all three authorization mechanisms the codebase uses to protect write operations. A publish `RoleReader` or the anonymous account when `Publish.Auth.Enable` is `false` can invoke it, forcing the server to flush its pending write-transaction queue, scan all references globally, load and parse referencing trees from disk, and enqueue database writes. This violates the read-only invariant (it writes even in a globally read-only workspace), provides an unauthenticated resource-amplification/DoS primitive, and applies no per-object access check to the caller-supplied ID.

### Details

**Route / auth tier.** `router.go`: `Handle("POST", "/api/ref/refreshBacklink", model.CheckAuth, refreshBacklink)`, `CheckAuth` only. `CheckAuth` admits `RoleReader`; the publish proxy forwards port-6808 traffic with a Reader JWT (anonymous account when publish auth is disabled). Anonymous/reader reachable.

**Guard fall-through.** SiYuan protects write handlers with one of three mechanisms: route-level `CheckAdminRole` (AV/riff/repo/sync/setting/snippet/notebook mutations), route-level `CheckReadonly` (filetree/block/attr/tag mutations), or an inline `IsReadOnlyRoleContext` check (e.g. `updateEmbedBlock`, `updateRecentDoc*Time`). `refreshBacklink` has none of the three.

**Write path reached.** `refreshBacklink` calls `model.RefreshBacklink(id)`:
- `FlushTxQueue()` — forces the pending write-transaction queue to disk.
- `refreshRefsByDefID(defID)` → `QueryRefsByDefID(defID)` (global scan with encrypted-box fallback loop) → `filesys.LoadTrees(rootIDs)` (disk read and Lute parse of every referencing tree) → `sql.UpdateRefsTreeQueue(tree)` (enqueues DB writes) → ref-count task update.

The handler also does not consult `util.ReadOnly`, so it executes its writes even when the workspace is configured globally read-only.

**No per-object authorization.** `defID` is attacker-controlled and receives no publish-access or ownership check, so a reader can force a reference reindex of any document, including publish-forbidden/unpublished ones (cross-scope).

### Proof of Concept

Reproduced on a local instance (SiYuan running locally, publish mode enabled on port 6808, publish Basic Auth disabled), as an anonymous reader (no token):

**Target endpoint executes the full write path:**
```
POST http://127.0.0.1:6808/api/ref/refreshBacklink
{"id":"<any block id>"}
```
Returns `{"code":0,"msg":"","data":null}` HTTP 200 the handler ran to completion, flushing the transaction queue and enqueuing ref writes.

**Controls: the guarded mutating siblings correctly reject the same anonymous session:**
```
POST http://127.0.0.1:6808/api/tag/renameTag      → 403 (CheckAdminRole and CheckReadonly)
POST http://127.0.0.1:6808/api/block/foldBlock    → 403
POST http://127.0.0.1:6808/api/block/updateEmbedBlock → code 0 no-op (inline IsReadOnlyRoleContext blocks the write)
```
The 200-vs-403 contrast confirms `refreshBacklink` is reachable and executes where its siblings are blocked.

### Impact

An anonymous reader (publish mode with auth disabled) or any publish `RoleReader` can:

- **Bypass the read-only invariant:** trigger persistent server-side writes (transaction-queue flush and reference reindex), including in a workspace configured globally read-only.
- **Amplify resource use without authentication:** each call forces a transaction flush, a global reference scan, and disk read and parse of every referencing tree, with an attacker-controlled `id` and no rate limiting, a DoS primitive.
- **Act cross-scope:** `defID` receives no publish-access check, so a reader can force reindexing of documents outside their publish scope. This is an integrity-invariant violation and a resource-amplification vector, not data corruption or injection, the caller cannot control the content of the writes, only trigger them. Impact is integrity-low and availability-low; no confidentiality impact and no attacker-controlled data reaches storage.

### Suggested fix

Apply the same guard its mutating siblings use, add `CheckReadonly` (and `CheckAdminRole` if reference refresh is intended to be an authenticated operation) to the route, or an inline `IsReadOnlyRoleContext` check consistent with `updateEmbedBlock`. The endpoint should also honor `util.ReadOnly` and apply a publish-access check to `defID` so a reader cannot force cross-scope reindexing. More broadly, the three-way guard strategy (route middleware vs. inline check vs. none) is what allowed this handler to receive no gate at all; a structural backstop, a role-scoped route group for the mutation surface would prevent recurrence.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-wgwx-479j-23vq
- https://nvd.nist.gov/vuln/detail/CVE-2026-72812
- https://github.com/siyuan-note/siyuan/commit/7d273c271ce193b9d3ee5751b596b8093ba84ada
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-missing-authorization-via-refreshbacklink
