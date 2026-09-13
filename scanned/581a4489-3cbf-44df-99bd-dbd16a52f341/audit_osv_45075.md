# [M] SiYuan: Database view structure (all view names, layout types and per-field visibility) is returned to anonymous readers by /api/av/getAttributeViewFieldViews

## Summary
Severity: Medium
Advisory: GHSA-57v5-wqx3-cgj4
Aliases: GO-2026-6430
Ecosystem: Go
Published: 2026-09-08
Source: https://osv.dev/vulnerability/GHSA-57v5-wqx3-cgj4
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260726004013-64c26e74bb82

## Details
### Scope note (please read first)

This endpoint does not exist in v3.7.3 or on master. It was introduced on the development branch by commit `acfc02ee8` ("Improve database field visibility across views", #11020) and is live on `v3.7.4-alpha.1`, so it will ship in v3.7.4 unless gated first. No released stable version is affected.

### Summary

`/api/av/getAttributeViewFieldViews` is registered with `CheckAuth` only and applies no publish-access filtering. Given a database `avID`, it returns the complete view structure of that database: every view's name, icon, layout type and the per-field `Hidden` flag, regardless of whether the caller is authorized to see that database or those views.

The route registered immediately before it, `getAttributeViewKeys`, does gate reader roles.

### Details

| Item | Detail |
|---|---|
| Route | `kernel/api/router.go:530` `POST /api/av/getAttributeViewFieldViews` → `model.CheckAuth` → `getAttributeViewFieldViews` |
| Middleware | `CheckAuth` only, no `CheckReadonly`, no `CheckAdminRole` |
| Guard in handler | None. Greps for `IsReadOnlyRoleContext`, `publishAccess` and `Filter*` all return zero matches |
| Exposed | For each entry in `attrView.Views`: `ID`, `Icon`, `Name`, `Type`, and the `Hidden` flag for the requested field |
| Introduced by | `acfc02ee8` (feature), dev branch only |

**The leak path.** The handler binds `avID` and `keyID`, validating them against the ID pattern only, then calls `GetAttributeViewFieldViews(avID, keyID)`. That function calls `av.ParseAttributeView(avID)`, which reads the database's storage file directly by identifier. There is no ownership check and no publish-access check anywhere on the path. The result is a per-view record for every view the database defines.

What a reader learns is author-written: view names are typed by the user, and layout type distinguishes a table from a gallery or kanban. The `Hidden` flag additionally reveals, per view, which fields the author chose to conceal.

**Guarded sibling, one route earlier.** `getAttributeViewKeys` (`kernel/api/router.go:529`) is also reader-reachable and does gate:

```go
if model.IsReadOnlyRoleContext(c) {
    blockAttributeViewKeys = model.FilterBlockAttributeViewKeysByPublishAccess(c, publishAccess, ...)
}
```

The new route at 530 applies nothing equivalent.

This is worth flagging as more than an isolated omission. `acfc02ee8` added a new reader-reachable attribute-view endpoint during the same development cycle in which the surrounding attribute-view endpoints were being hardened. The same pattern produced an earlier exposure: `f2d966659`, which added encrypted-notebook unlock status for plugin consumption, created a reader-reachable disclosure on a surface that was otherwise being tightened. A check on new reader-reachable routes against the gating applied to their registered neighbours would catch this class before release.

**Reachability, stated honestly.** The endpoint requires a valid `avID` and `keyID`. `renderAttributeView` supplies both to a reader for any database embedded in a document the reader can access. The realistic target is therefore a partially-published database: the document publishes one view, and this endpoint enumerates the existence, name, layout type and hidden-field configuration of the database's other views, including views the author did not publish. Against a database with no reader-accessible surface at all, obtaining the identifiers is harder, particularly since the `getAttributeViewKeysByID` enumeration path was closed on the development branch. The severity below reflects that constraint rather than a worst case.

### Proof of Concept

Precondition: `v3.7.4-alpha.1` build, publish mode enabled (default port 6808), anonymous when `Publish.Auth.Enable` is `false`, otherwise any publish reader account. A database embedded in a reader-accessible document, with at least one additional view that is not published.

Step 1, obtain the identifiers through the reader-accessible path:

```
POST http://127.0.0.1:6808/api/av/renderAttributeView
{"id":"<block id of the embedded database in a published doc>"}

→ 200, returns the published view together with its key identifiers
```

Step 2, enumerate the rest of the database's views:

```
POST http://127.0.0.1:6808/api/av/getAttributeViewFieldViews
{"avID":"<avID from step 1>","keyID":"<keyID from step 1>"}

→ 200, returns a record per view: ID, Icon, Name, Type, Hidden
```

The response includes views that were never published, disclosing their author-written names, their layout types, and which field is hidden in each.

### Impact

An anonymous reader in publish mode, or any publish `RoleReader`, can enumerate the full view structure of a database when only part of that database is published. View names are author-written free text and frequently describe the data they filter, so this discloses the existence and subject matter of unpublished views. The per-field `Hidden` flags additionally reveal the author's concealment choices across those views. Confidentiality only, with no integrity or availability impact, and bounded by the reader needing identifiers obtainable from a reader-accessible database.

### Suggested fix

Gate the handler for read-only roles, mirroring `getAttributeViewKeys`: when `IsReadOnlyRoleContext(c)` holds, resolve the block that owns the `avID` and apply the publish-access check before returning any view record, or filter the returned set through the same `FilterBlockAttributeViewKeysByPublishAccess` path its neighbour uses.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-57v5-wqx3-cgj4
- https://github.com/siyuan-note/siyuan/commit/64c26e74bb82c24a73513107684b91cc01335fab
- https://github.com/siyuan-note/siyuan
