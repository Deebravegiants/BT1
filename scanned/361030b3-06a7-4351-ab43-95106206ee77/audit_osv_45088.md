# [H] SiYuan: Embedded (transclusion) block content is returned without publish-access filtering, leaking private and password-protected document content to anonymous readers

## Summary
Severity: High
Advisory: GHSA-h6w7-xxcf-w2mq
Aliases: CVE-2026-72795, GO-2026-6425
Ecosystem: Go
Published: 2026-09-04
Source: https://osv.dev/vulnerability/GHSA-h6w7-xxcf-w2mq
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260725125659-1ca1c3c9d94b

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72795](https://nvd.nist.gov/vuln/detail/CVE-2026-72795).

### Summary

`/api/block/getBlockDOMWithEmbed` and `/api/block/getBlockDOMsWithEmbed` gate only the *requested* block against publish access. The blocks pulled in by that block's embed (transclusion) query are inlined into the returned DOM with no publish-access check at all, so a reader who requests a legitimately-published block containing an embed query receives the content of every block that query matched including blocks in hidden, forbidden and password-protected documents.

The dedicated embed endpoint `getEmbedBlock` filters these same results for reader roles. The DOM-with-embed path does not.

### Details

| Item | Detail |
|---|---|
| Routes | `kernel/api/router.go:226` `POST /api/block/getBlockDOMWithEmbed` → `model.CheckAuth` → `getBlockDOMWithEmbed`; `:227` `POST /api/block/getBlockDOMsWithEmbed` → `model.CheckAuth` → `getBlockDOMsWithEmbed` |
| Middleware | `CheckAuth` only — no `CheckReadonly`, no `CheckAdminRole` → reachable by the publish `RoleReader` token, and anonymously when `Publish.Auth.Enable` is `false` |
| Guard present | Top-level requested block only. Singular: password + disable checks on the requested id. Plural: `filterBlockDOMsByPublishAccess` over the requested ids. |
| Guard absent | The embedded blocks resolved from the query |
| Exposed | Content HTML of every block matched by the embed query, regardless of that block's publish visibility or password tier |

**The leak path.** `getBlockDOMWithEmbed` → `GetBlockDOMsWithEmbedInBox` → `resolveEmbedContentInBox` (`kernel/model/block.go:976`). That function walks the tree for `NodeBlockQueryEmbed`, extracts the embed SQL, executes `sql.SelectBlocksRawStmtInBox(stmt, ...)`, builds `embedContents` from each matched block's content HTML, and inlines the result via `SetIALAttr("embed-content", ...)`.

`resolveEmbedContentInBox` takes no `publishAccess` parameter and contains no filtering: `FilterEmbedBlocks`, `CheckBlockIdAccessableByPublishAccess`, `CheckPathAccessable`, `publishAccess` and `IsReadOnlyRoleContext` all return zero matches in that function and its call path. The top-level gate therefore passes on the requested block, and the response body carries content the reader has no access to.

Embed queries in published documents routinely span the entire workspace by design, dashboard documents, "all my TODOs" aggregations, tag or attribute rollups. The reader does not need to construct anything: requesting an already-published document that contains such an embed is sufficient. If the publish frontend renders embedded blocks through this endpoint, the disclosure occurs passively during normal viewing of any published document containing an embed block.

**Guarded sibling.** `getEmbedBlock` (`kernel/api/router.go:212`), which is also reader-reachable and returns embed query results, applies `model.FilterEmbedBlocksByPublishAccess(c, publishAccess, blocks)` for reader roles (`kernel/model/search.go:38`). The same class of data is filtered there and unfiltered here.

**Scope note.** A prior review of `getBlockDOMsWithEmbed` confirmed that the per-id publish gate is correctly applied to the *requested* ids. That observation is accurate and is not in dispute, this report concerns the *embedded* blocks resolved downstream in `resolveEmbedContentInBox`, which are not covered by that gate.

### Proof of Concept

Precondition: publish mode enabled (default port 6808); anonymous when `Publish.Auth.Enable` is `false`, otherwise any publish reader account. A published document containing an embed query whose results include at least one block in a non-published or password-protected document.

```
POST http://127.0.0.1:6808/api/block/getBlockDOMWithEmbed
{"id":"<id of a published block containing an embed query>"}

→ 200
   The returned DOM contains embed-content attributes carrying the
   content HTML of blocks in documents the reader has no publish
   access to.
```

Differential check against the filtered sibling, using the same reader session and the same underlying query:

```
POST http://127.0.0.1:6808/api/search/getEmbedBlock
{"stmt":"<the same embed query>"}

→ 200, results filtered by FilterEmbedBlocksByPublishAccess
```

The filtered endpoint withholds the private blocks; the DOM endpoint returns their content.

The plural route behaves identically for each requested id:

```
POST http://127.0.0.1:6808/api/block/getBlockDOMsWithEmbed
{"ids":["<published block containing an embed query>"]}
```

### Impact

An anonymous reader in publish mode or any publish `RoleReader` can read the content of blocks in documents that are not published, are marked hidden or forbidden, or are protected by a publish password, by requesting a published block that transcludes them. Because embed queries in aggregation-style published documents commonly match across the whole workspace, the volume of exposed content is bounded only by what the author's embed queries happen to match, not by anything under the reader's control being unusual. Confidentiality-only; no integrity or availability impact.

### Suggested fix

Thread the request's `publishAccess` context into `resolveEmbedContentInBox` and, when `IsReadOnlyRoleContext` holds, drop any matched block failing `CheckBlockIdAccessableByPublishAccess` and the password-tier check before its content is written into `embed-content` mirroring the treatment `getEmbedBlock` already gives the same data via `FilterEmbedBlocksByPublishAccess`.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-h6w7-xxcf-w2mq
- https://nvd.nist.gov/vuln/detail/CVE-2026-72795
- https://github.com/siyuan-note/siyuan/commit/1ca1c3c9d94bea14fc9728ff2fb8392bb0f29732
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-information-disclosure-via-embed-block
