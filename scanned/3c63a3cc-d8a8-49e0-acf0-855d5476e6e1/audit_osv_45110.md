# [H] SiYuan: Graph endpoints omit the publish-password tier: anonymous readers receive block-level content of password-protected documents

## Summary
Severity: High
Advisory: GHSA-vpjw-wf5h-cgpq
Aliases: CVE-2026-72804, GO-2026-6407
Ecosystem: Go
Published: 2026-09-03
Source: https://osv.dev/vulnerability/GHSA-vpjw-wf5h-cgpq
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260724091654-82e9ded423e4

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72804](https://nvd.nist.gov/vuln/detail/CVE-2026-72804).

### Summary

`getGraph` and `getLocalGraph` filter reader sessions against the *visibility* tier only and never check the publish password. Password-protected documents are `Visible = true`, so their graph nodes survive the filter and graph nodes are block-level and carry the block's actual content. An anonymous reader who has never supplied a document's password can therefore retrieve that document's per-block content and its reference/backlink topology. Both endpoints are `CheckAuth`-only, so they are reachable by the publish `RoleReader` token and by the anonymous account when `Publish.Auth.Enable` is `false`.

### Details

Both handlers filter with the invisible-tier set only:

```go
publishIgnore := model.GetInvisiblePublishAccess(publishAccess)   // Visible tier ONLY
nodes, links = model.FilterGraphByPublishIgnore(publishIgnore, nodes, links)
```

`FilterGraphByPublishIgnore` (`kernel/model/publish_access.go:849`) drops a node only when `!CheckPathAccessableByPublishIgnore(node.Box, node.Path, publishIgnore)`. There is no password evaluation anywhere in the graph code grepping `graph.go` for `CheckPublishAuthCookie` or `password` returns nothing.

Because password-protected documents are `Visible = true`, their nodes pass the filter unchanged.

**The nodes carry content, not just titles.** `genTreeNodes` emits one node per block, and `nodeTitleLabel` sets `node.Title = node.Label = block.Content` (`kernel/model/graph.go:673-678`). So each surviving node exposes the block's text.

This is materially broader than the by-design listing behaviour: `listDocsByPath` intentionally exposes protected document *titles* (protected means "publicly visible, password required to access"), but the graph endpoints expose per-block *content* and the full link/reference topology, which listing never does.

Verified at `origin/master`: `FilterGraphByPublishIgnore` contains only the `CheckPathAccessableByPublishIgnore` call; `graph.go` contains no password check; both routes are registered `CheckAuth` without `CheckAdminRole`.

### Proof of Concept

Precondition: publish mode enabled (default port 6808); anonymous when `Publish.Auth.Enable` is `false`, otherwise any publish reader account. A document is marked **protected** (visible, password set) and contains blocks with distinctive content. No password is supplied in any request below.

**Targeted: one protected document's content and reference structure:**
```
POST http://127.0.0.1:6808/api/graph/getLocalGraph
{"id":"<PROTECTED_DOC_ID>"}
```
Returns nodes whose `Title`/`Label` contain the protected document's per-block content, plus its links/backlinks.

**Workspace-wide: every protected document:**
```
POST http://127.0.0.1:6808/api/graph/getGraph
{}
```
Returns block-level nodes for every protected document in the workspace, together with the complete link graph.

**Control:** requesting the same document through the normal content path returns the password placeholder confirming the password gate is enforced elsewhere and omitted here.

### Impact

An anonymous reader (publish mode with auth disabled) or any publish `RoleReader` can read the block-level content of every password-protected document in the workspace, plus the full reference/backlink topology, without ever supplying a password. This defeats the publish-password control for the graph subsystem. Confidentiality-only, no modification.

### Suggested fix

Extend the graph filter to evaluate the password tier in addition to visibility: in `FilterGraphByPublishIgnore`, drop a node unless the document's publish password is unset or the caller presents a valid publish-auth cookie for it (`password == "" || CheckPublishAuthCookie(...)`), matching the sibling filters that enforce both tiers. Consider also excluding block content from node `Title`/`Label` for reader sessions, so the graph conveys structure without document text.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-vpjw-wf5h-cgpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-72804
- https://github.com/siyuan-note/siyuan/commit/82e9ded423e45eabcc96010abd30c0f96bfe0323
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-authentication-bypass-via-graph-endpoints
