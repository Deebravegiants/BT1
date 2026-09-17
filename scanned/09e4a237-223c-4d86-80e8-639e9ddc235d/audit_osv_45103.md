# [M] SiYuan: Missing publish-access filter on getBlockAttrs and batchGetBlockAttrs discloses block attributes (name, alias, memo, custom fields) of protected documents

## Summary
Severity: Medium
Advisory: GHSA-qvq9-hq6p-v378
Aliases: CVE-2026-72803, GO-2026-6404
Ecosystem: Go
Published: 2026-09-03
Source: https://osv.dev/vulnerability/GHSA-qvq9-hq6p-v378
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260724093256-229fdffd7e4a

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72803](https://nvd.nist.gov/vuln/detail/CVE-2026-72803).

### Summary

`POST /api/attr/getBlockAttrs` and `POST /api/attr/batchGetBlockAttrs` return a block's full attribute set (IAL) with no publish-access check. Both are `CheckAuth`-only, so they are reachable by the publish `RoleReader` token and by the anonymous account when `Publish.Auth.Enable` is `false`. An anonymous reader supplying a block ID receives the block's name, alias, memo, bookmark, tags, and every `custom-*` attribute including for blocks in publish-forbidden and password-protected documents. The batch variant accepts an ID list, making it a bulk extraction primitive.

### Details

Neither handler applies a filter:

```go
// /api/attr/getBlockAttrs      (router line 301)
ret.Data = sql.GetBlockAttrs(id)

// /api/attr/batchGetBlockAttrs (router line 302)
ret.Data = sql.BatchGetBlockAttrs(idList)
```

`sql.GetBlockAttrs` is a direct database read returning the block's entire IAL: `name`, `alias`, `memo`, `bookmark`, `tags`, and any `custom-*` key/value the user has set. Several of these are user-authored free text memos in particular are freeform notes attached to a block so this is document content, not merely structural metadata.

`batchGetBlockAttrs` takes an arbitrary list of block IDs in a single request, so an attacker holding a set of block IDs can sweep attributes across the entire workspace in one call.

**Guarded-sibling asymmetry.** The sibling metadata endpoint `getBlockInfo` calls `checkBlockPublishAccess(c, id, ret)` before returning; `getBlockAttrs` and `batchGetBlockAttrs` call nothing.

Verified at `origin/master`: both handler bodies contain no publish-access, publish-ignore, or readonly-role check, and both routes are registered `CheckAuth` without `CheckAdminRole`.

### Proof of Concept

Precondition: publish mode enabled (default port 6808); anonymous when `Publish.Auth.Enable` is `false`, otherwise any publish reader account. A document is marked publish-forbidden (or password-protected) and contains a block with a memo and a custom attribute set.

**Single-block disclosure:**
```
POST http://127.0.0.1:6808/api/attr/getBlockAttrs
{"id":"<BLOCK_ID_IN_PROTECTED_DOC>"}
```
Returns the block's IAL: `name`, `alias`, `memo`, `bookmark`, `tags`, and all `custom-*` values.

**Bulk disclosure:**
```
POST http://127.0.0.1:6808/api/attr/batchGetBlockAttrs
{"ids":["<ID1>","<ID2>","<ID3>"]}
```
Returns the attribute sets for every supplied ID in one response, with no per-ID authorization.

**Control:** the sibling `getBlockInfo` with the same block ID is refused by `checkBlockPublishAccess`, confirming the boundary is enforced elsewhere and omitted here.

### Impact

An anonymous reader (publish mode with auth disabled) or any publish `RoleReader` can read block attributes belonging to publish-forbidden and password-protected documents, including user-authored memos and arbitrary `custom-*` values. The batch endpoint turns this into a bulk primitive: given a set of block IDs, an attacker retrieves attributes across the whole workspace in a single request. Confidentiality-only.

### Suggested fix

Call `checkBlockPublishAccess` in `getBlockAttrs` before returning, matching `getBlockInfo`. For `batchGetBlockAttrs`, apply the check per ID and drop unauthorized entries from the response rather than failing the whole batch.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-qvq9-hq6p-v378
- https://nvd.nist.gov/vuln/detail/CVE-2026-72803
- https://github.com/siyuan-note/siyuan/commit/229fdffd7e4afdef543d4d8495657fda8a369400
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-information-disclosure-via-getblockattrs
