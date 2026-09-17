# [H] SiYuan: Publish Reader Can Arbitrarily Delete Attribute View Files via `/api/av/removeUnusedAttributeView`

## Summary
Severity: High
Advisory: GHSA-7m5h-w69j-qggg
CVE: CVE-2026-40259
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-7m5h-w69j-qggg
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260407035653-2f416e5253f1

## Details
## Summary

An authenticated publish-service reader can invoke `/api/av/removeUnusedAttributeView` and cause persistent deletion of arbitrary attribute view (`AV`) definition files from the workspace.

The route is protected only by generic `CheckAuth`, which accepts publish `RoleReader` requests. The handler forwards a caller-controlled `id` directly into a model function that deletes `data/storage/av/<id>.json` without verifying either:

- that the caller is allowed to perform write/destructive actions; or
- that the target AV is actually unused.

This is a persistent integrity and availability issue reachable from the publish surface.

## Root Cause

### 1. Publish users are issued a `RoleReader` JWT

- [kernel/model/auth.go](/root/audit/siyuan/kernel/model/auth.go#L105)

```go
ClaimsKeyRole: RoleReader,
```

### 2. The publish reverse proxy forwards that token upstream

- [kernel/server/proxy/publish.go](/root/audit/siyuan/kernel/server/proxy/publish.go#L131)
- [kernel/server/proxy/publish.go](/root/audit/siyuan/kernel/server/proxy/publish.go#L186)

### 3. `CheckAuth` accepts `RoleReader`

- [kernel/model/session.go](/root/audit/siyuan/kernel/model/session.go#L201)

```go
if role := GetGinContextRole(c); IsValidRole(role, []Role{
    RoleAdministrator,
    RoleEditor,
    RoleReader,
}) {
    c.Next()
    return
}
```

### 4. The route is exposed with `CheckAuth` only

- [kernel/api/router.go](/root/audit/siyuan/kernel/api/router.go#L507)

```go
ginServer.Handle("POST", "/api/av/removeUnusedAttributeView", model.CheckAuth, removeUnusedAttributeView)
```

There is no `CheckAdminRole` and no `CheckReadonly`.

### 5. The handler forwards attacker-controlled `id` directly to the delete sink

- [kernel/api/av.go](/root/audit/siyuan/kernel/api/av.go#L32)

```go
avID := arg["id"].(string)
model.RemoveUnusedAttributeView(avID)
```

### 6. The model deletes the AV file unconditionally

- [kernel/model/attribute_view.go](/root/audit/siyuan/kernel/model/attribute_view.go#L49)

```go
func RemoveUnusedAttributeView(id string) {
    absPath := filepath.Join(util.DataDir, "storage", "av", id+".json")
    if !filelock.IsExist(absPath) {
        return
    }
    ...
    if err = filelock.RemoveWithoutFatal(absPath); err != nil {
        ...
        return
    }
    IncSync()
}
```

Crucially, this function does **not** verify that the supplied AV is actually unused. The name of the function suggests a cleanup helper, but the implementation is really "delete AV file by id if it exists".

## Attack Prerequisites

- Publish service enabled
- Attacker can access the publish service
- If publish auth is enabled, attacker has valid publish-reader credentials
- Attacker knows an `avID`

## Obtaining `avID`

`avID` is not secret. It is exposed extensively in frontend markup as `data-av-id`.

Examples:

- [app/src/protyle/render/av/render.ts](/root/audit/siyuan/app/src/protyle/render/av/render.ts#L117)
- [app/src/protyle/render/av/layout.ts](/root/audit/siyuan/app/src/protyle/render/av/layout.ts#L120)
- [app/src/protyle/render/av/groups.ts](/root/audit/siyuan/app/src/protyle/render/av/groups.ts#L52)

Any publish-visible database/attribute view can therefore disclose a valid `avID` to the attacker.

## Exploit Path

1. Attacker browses published content containing an attribute view.
2. Attacker extracts the `data-av-id` value from the page/DOM.
3. Attacker sends a POST request to `/api/av/removeUnusedAttributeView` through the publish service.
4. Publish proxy injects a valid `RoleReader` token.
5. `CheckAuth` accepts the request.
6. The handler passes the attacker-controlled `avID` to `model.RemoveUnusedAttributeView`.
7. The backend deletes `data/storage/av/<avID>.json`.

## Proof of Concept

Request:

```http
POST /api/av/removeUnusedAttributeView HTTP/1.1
Host: <publish-host>:<publish-port>
Content-Type: application/json
Authorization: Basic <publish-account-creds-if-enabled>

{
  "id": "<exposed-data-av-id>"
}
```

Expected result:

- HTTP 200
- backend increments sync state
- the target attribute view file is removed from `data/storage/av/`
- published and local workspace behavior for that AV becomes broken until restored from history or recreated

## Impact

This gives a low-privileged publish reader a destructive persistent write primitive against workspace data.

Practical consequences include:

- deletion of live attribute view definitions
- corruption/breakage of published database views
- breakage of local workspace rendering and AV-backed relationships
- operational disruption until restore or manual repair

The bug affects integrity and availability, not merely UI state.

## Recommended Fix

At minimum:

1. Block publish/read-only users from this route.
2. Require admin/write authorization.
3. Re-validate that the target AV is actually unused before deletion.

Safe router fix:

```go
ginServer.Handle("POST", "/api/av/removeUnusedAttributeView",
    model.CheckAuth,
    model.CheckAdminRole,
    model.CheckReadonly,
    removeUnusedAttributeView,
)
```

And inside the model or handler, reject deletion unless the target `id` is present in `UnusedAttributeViews(...)`.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-7m5h-w69j-qggg
- https://nvd.nist.gov/vuln/detail/CVE-2026-40259
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.6.4
