# [M] SiYuan: Missing publish-access check on getBlockBreadcrumb, getRefText, and getBlockTreeInfos discloses content and metadata of protected/forbidden documents

## Summary
Severity: Medium
Advisory: GHSA-67x2-mq63-v9vm
Aliases: CVE-2026-72805, GO-2026-6387
Ecosystem: Go
Published: 2026-09-03
Source: https://osv.dev/vulnerability/GHSA-67x2-mq63-v9vm
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260723163028-931ba693375e

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72805](https://nvd.nist.gov/vuln/detail/CVE-2026-72805).

### Summary

Three block endpoints return document content snippets and metadata without any publish-access check, while their sibling `getBlockInfo` which returns comparable data does enforce one. All three are `CheckAuth`-only, so they are reachable by the publish `RoleReader` token and by the anonymous account when `Publish.Auth.Enable` is `false`. An anonymous reader supplying a block ID receives content and metadata belonging to publish-forbidden and password-protected documents.

### Details

`getBlockInfo` (`kernel/api/block.go`) gates on the publish boundary:
```go
if !checkBlockPublishAccess(c, id, ret) {
    return
}
```

The following siblings in the same file perform no equivalent check:

| Endpoint | Returns | Publish check |
|---|---|---|
| `getBlockInfo` | root/title/path metadata | `checkBlockPublishAccess`: present |
| `getBlockBreadcrumb` | `BlockPath.Name` : root document title plus every ancestor block's content snippet | none |
| `getRefText` | the block's reference/anchor text (document content) | none |
| `getBlockTreeInfos` | root/title/path metadata for arbitrary block IDs | none |

`getBlockBreadcrumb` returns the full ancestor chain including each ancestor block's content snippet, and `getRefText` returns block anchor text both are document content, not just metadata. `getBlockTreeInfos` returns root/title/path for any caller-supplied ID set via `model.GetBlockTreeInfosInBox(...)` with no gate.

`getBlockBreadcrumb` and `getRefText` additionally accept a client-supplied notebook argument that routes to the `*InBox` variants, so the same unguarded path applies to encrypted-notebook reads while the notebook is unlocked.

The correct primitive already exists in the codebase and is used by `getBlockInfo`; these three handlers simply do not call it.

### Proof of Concept

Precondition: publish mode enabled (default port 6808); anonymous when `Publish.Auth.Enable` is `false`, otherwise any publish reader account. A document `D` is marked publish-forbidden (or password-protected) and contains a block `BLOCK_ID` under a heading with distinctive content.

**Control: the gated sibling correctly refuses:**
```
POST http://127.0.0.1:6808/api/block/getBlockInfo
{"id":"BLOCK_ID"}
```
Blocked by `checkBlockPublishAccess`.

**Disclosure: the ungated siblings return the data anyway:**
```
POST http://127.0.0.1:6808/api/block/getBlockBreadcrumb
{"id":"BLOCK_ID"}
→ ancestor chain including the forbidden document's title and ancestor block content snippets

POST http://127.0.0.1:6808/api/block/getRefText
{"id":"BLOCK_ID"}
→ the block's reference/anchor text (content of the forbidden document)

POST http://127.0.0.1:6808/api/block/getBlockTreeInfos
{"ids":["BLOCK_ID"]}
→ root ID, title, and path for the forbidden document
```

Verified by code inspection at `origin/master` (`eef10568`): `getBlockInfo` contains the `checkBlockPublishAccess` call; `getBlockBreadcrumb`, `getRefText`, and `getBlockTreeInfos` contain no publish-access, publish-ignore, or readonly-role check in their bodies.

### Impact

An anonymous reader (publish mode with auth disabled) or any publish `RoleReader` can read, for documents explicitly excluded from publishing or protected by a publish password:
- the document title and full ancestor chain, including ancestor block content snippets (`getBlockBreadcrumb`);
- block reference/anchor text, i.e. document content (`getRefText`);
- root ID, title, and path metadata for arbitrary block IDs (`getBlockTreeInfos`).

Because `getBlockBreadcrumb` and `getRefText` accept a notebook argument routing to the `*InBox` variants, the same disclosure applies to encrypted notebooks while unlocked. Confidentiality-only; the precondition is a block ID, obtainable from other reader-reachable endpoints.

### Suggested fix

Call `checkBlockPublishAccess` (as `getBlockInfo` does) in `getBlockBreadcrumb`, `getRefText`, and `getBlockTreeInfos` before returning data for `getBlockTreeInfos`, apply it per ID and drop unauthorized entries. Confirm the `*InBox` variants (`GetBlockRefTextInBox`, `BuildBlockBreadcrumbInBox`) enforce the same boundary so the notebook-argument path is covered.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-67x2-mq63-v9vm
- https://nvd.nist.gov/vuln/detail/CVE-2026-72805
- https://github.com/siyuan-note/siyuan/commit/931ba693375ea9877b2ef74f9bfb632fad5bab3f
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-information-disclosure-via-block-endpoints
