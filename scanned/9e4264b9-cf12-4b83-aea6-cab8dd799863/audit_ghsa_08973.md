# [M] SiYuan has broken access control in `/api/search/{searchAsset,searchTag,searchWidget,searchTemplate}` publish-mode

## Summary
Severity: Medium
Advisory: GHSA-fmh9-gpqh-g53g
CVE: CVE-2026-45148
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-fmh9-gpqh-g53g
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260512140701-d7b77d945e0d

## Details
### Summary

The advisory `GHSA-c77m-r996-jr3q` patched `getBookmark` so that, when invoked by a publish-mode `RoleReader`, results are filtered through `FilterBlocksByPublishAccess` to remove entries from password-protected / publish-ignored notebooks. Four sibling search handlers in the same file did not receive the equivalent treatment and continue to expose metadata across the publish-access boundary.

### Details

**Affected files / lines (v3.6.5):**

`kernel/api/router.go:181-190` — all four endpoints registered with `CheckAuth` only, which the publish-service `RoleReader` JWT passes:

```go
ginServer.Handle("POST", "/api/search/searchTag",      model.CheckAuth, searchTag)
ginServer.Handle("POST", "/api/search/searchTemplate", model.CheckAuth, searchTemplate)
ginServer.Handle("POST", "/api/search/searchWidget",   model.CheckAuth, searchWidget)
ginServer.Handle("POST", "/api/search/searchAsset",    model.CheckAuth, searchAsset)
```

`kernel/api/search.go` — none of the four handlers branches on `model.IsReadOnlyRoleContext(c)` to filter the response, while their *peers* in the same file do. Compare:

```go
// :29-65  listInvalidBlockRefs — DOES filter:
if model.IsReadOnlyRoleContext(c) {
    publishAccess := model.GetPublishAccess()
    blocks = model.FilterBlocksByPublishAccess(c, publishAccess, blocks)
}

// :67-93  getAssetContent — DOES filter (FilterAssetContentByPublishAccess)
// :95-115 fullTextSearchAssetContent — DOES filter
// :250-285 getEmbedBlock — DOES filter (FilterEmbedBlocksByPublishAccess)

// :156-176 searchAsset — does NOT filter
ret.Data = model.SearchAssetsByName(k, exts)

// :178-196 searchTag — does NOT filter
tags := model.SearchTags(k)
ret.Data = map[string]any{"tags": tags, "k": k}

// :198-213 searchWidget — does NOT filter
widgets := model.SearchWidget(keyword)

// :233-248 searchTemplate — does NOT filter
templates := model.SearchTemplate(keyword)
```

`model.SearchAssetsByName`, `model.SearchTags`, `model.SearchWidget`, `model.SearchTemplate` operate over the entire workspace database / filesystem, not just the publish-visible subset. A `FilterTagsByPublishIgnore` helper *already exists* in `kernel/model/` and is used by `getTag` itself (`kernel/api/tag.go:58-62`), confirming the maintainers' intent.

### PoC

End-to-end reproduction requires enabling the SiYuan publish service, marking one notebook as private to publish access, and obtaining a `RoleReader` JWT from the publish reverse-proxy (per `kernel/server/proxy/publish.go`). Once authenticated as the Reader against the publish port:

```bash
# Returns ALL tags across the workspace, including ones drawn only from the publish-private notebook.
curl -X POST https://<publish-host>/api/search/searchTag \
     -H 'Authorization: Bearer <reader-jwt>' \
     -H 'Content-Type: application/json' \
     -d '{"k":""}'

# Returns ALL asset filenames (e.g., CV.pdf, contract.docx, salary-2026.xlsx) regardless of source notebook.
curl -X POST https://<publish-host>/api/search/searchAsset \
     -H 'Authorization: Bearer <reader-jwt>' \
     -H 'Content-Type: application/json' \
     -d '{"k":""}'

curl -X POST https://<publish-host>/api/search/searchWidget   -H '...' -d '{"k":""}'
curl -X POST https://<publish-host>/api/search/searchTemplate -H '...' -d '{"k":""}'
```

Each call returns the global result set without applying `FilterTagsByPublishIgnore` / `FilterAssetContentByPublishAccess` / equivalent.

In this audit I source-confirmed the missing branch in v3.6.5 but did not stand up the full publish-service flow. The fix is straightforward enough that the source-level evidence should be sufficient for triage.

### Impact

A publish-service Reader (the role assigned to anonymous publish visitors by default) can enumerate:

- All tag strings used anywhere in the workspace — frequently contains person names, project codenames, internal identifiers.
- All asset filenames uploaded to the workspace — frequently contains the contents of `CV.pdf`, `contract.docx`, `salary-2026.xlsx`, etc.
- All widget names and template names installed in the workspace.

This violates the publish-service trust boundary. Users intentionally mark notebooks as "invisible to publish" specifically to keep this metadata out of public reach.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-fmh9-gpqh-g53g
- https://nvd.nist.gov/vuln/detail/CVE-2026-45148
- https://github.com/siyuan-note/siyuan
