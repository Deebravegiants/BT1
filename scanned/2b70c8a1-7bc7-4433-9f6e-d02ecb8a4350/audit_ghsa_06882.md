# [M] Gitea: Token public-only scope bypassed on Limited-visibility owners (Repository + Package categories) — residual after CVE-2026-25714 / PR #37118

## Summary
Severity: Medium
Advisory: GHSA-7p4h-3gxq-x3h3
CVE: CVE-2026-56443
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-7p4h-3gxq-x3h3
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
## Summary

After [PR #37118](https://github.com/go-gitea/gitea/pull/37118) / **CVE-2026-25714**
(`fix: Unify public-only token filtering in API queries and repo access checks`,
merged 2026-05-18, backport `#37773` to 1.26.2 — the May 2026 unification pass
for public-only token filtering, reporter Medoedus per the 1.26.2 release notes),
the `public-only` PAT scope is still bypassable on **Repository** and **Package**
scope categories when the owner's `Visibility = Limited` (instance-internal).

The sibling `Org` / `User` / `ActivityPub` cases in the same `checkTokenPublicOnly`
switch correctly reject Limited owners via `!Visibility.IsPublic()`. The
Repository / Package cases use `repo.IsPrivate` or `Owner.Visibility.IsPrivate()`,
both of which return `false` for `VisibleTypeLimited` — so a `public-only` PAT
strictly exceeds anonymous reach on a Limited owner.

Tested on `gitea/gitea:1.26.2`. The decisive marker is that PR #37118's
unification IS applied in the version under test (User-category PROBE returns
`403 "token scope is limited to public users"`). Despite that, the
Repository-category PROBE on the same Limited owner with the same PAT returns
`200` and serves content.

## Affected entry points (4 spots)

| File:Line | Function | Affected surface |
|---|---|---|
| `routers/api/v1/api.go:292` | `checkTokenPublicOnly` Package case | API v1 packages |
| `routers/api/packages/api.go:76` | `reqPackageAccess` middleware | All 24 native package registries (`/api/packages/<type>/...`) |
| `services/context/api.go` | `TokenCanAccessRepo` helper | All API v1 Repository-category endpoints — content, issues, PRs, releases, labels, milestones, etc. |
| `services/context/permission.go:32` | `CheckTokenScopes` (called via `CheckRepoScopedToken`) | Web download endpoints `/raw`, `/media`, `/attachments`. LFS routes (`services/lfs/server.go:470/472`, `services/lfs/locks.go:62/151/216/284`) also chain through this helper. |

All four sinks check `repo.IsPrivate` or `Owner.Visibility.IsPrivate()` only.
`VisibleTypeLimited` falls through.

```go
// modules/structs/visible_type.go
func (vt VisibleType) IsPrivate() bool { return vt == VisibleTypePrivate }   // line 39-40
func (vt VisibleType) IsLimited() bool { return vt == VisibleTypeLimited }   // line 33-34
```

## Same-file evidence (`routers/api/v1/api.go:246-299` after PR #37118)

```go
case auth_model.AccessTokenScopeCategoryOrganization:
    orgPrivate := ... && !ctx.Org.Organization.Visibility.IsPublic()        // !IsPublic ✓
case auth_model.AccessTokenScopeCategoryUser:
    if ... && !ctx.ContextUser.Visibility.IsPublic() { ... }                // !IsPublic ✓
case auth_model.AccessTokenScopeCategoryActivityPub:
    if ... && !ctx.ContextUser.Visibility.IsPublic() { ... }                // !IsPublic ✓

case auth_model.AccessTokenScopeCategoryPackage:
    if ctx.Package != nil && ctx.Package.Owner.Visibility.IsPrivate() {     // IsPrivate ONLY ✗
        ctx.APIError(http.StatusForbidden, "token scope is limited to public packages")
        return
    }
```

`TokenCanAccessRepo` (`services/context/api.go`) reduces to `!repo.IsPrivate`:

```go
// A public-only token cannot reach a private repo; any other token is unrestricted by this check.
func (ctx *APIContext) TokenCanAccessRepo(repo *repo_model.Repository) bool {
    return repo == nil || !ctx.PublicOnly || !repo.IsPrivate
}
```

`CheckTokenScopes` (`services/context/permission.go:32`):

```go
if publicOnly && repo != nil && repo.IsPrivate {
    ctx.HTTPError(http.StatusForbidden)
    return
}
```

## PoC (Docker e2e VERIFIED on `gitea/gitea:1.26.2`, 2026-06-05)

Full script in the report (`run-poc.sh`). Setup:

1. Create user `limuser`. `PATCH /api/v1/admin/users/limuser` with body
   `{"visibility":"limited", ...}` — response confirms `"visibility":"limited"`.
2. Upload a generic package as `limuser`:
   `PUT /api/packages/limuser/generic/secretpkg/1.0.0/secret.txt` with body
   `secret-content-internal-only` → `201`.
3. Create user `attacker`.
4. Mint PAT for `attacker` with `scopes=["read:package","read:user","read:repository","public-only"]`.

Result on `gitea/gitea:1.26.2` — nine PROBEs:

```
PROBE A  (download package via attacker PAT)
    HTTP=200  Body: secret-content-internal-only

PROBE C  (read README of limuser's PUBLIC repo)
    HTTP=200  Body: {"name":"README.md", ...}

PROBE F  (sanity — User category, same PAT, same owner)
    HTTP=403  Body: {"message":"token scope is limited to public users"}

PROBE G  (Repository category, same PAT, same owner)
    HTTP=200  Body: {"name":"README.md", ...}                    ← bypass

PROBE H  (list limuser's repos, User category)
    HTTP=403  Body: {"message":"token scope is limited to public users"}

PROBE M  (git HTTPS smart protocol — info/refs)
    HTTP=200  Body: 001e# service=git-upload-pack ... HEAD ...   ← full clone enabled

PROBE N  (write attempt: POST contents/hacked.txt)
    HTTP=403  Body: {"message":"user should have a permission to write to the target branch"}
                                                                    Integrity:N confirmed

PROBE O  (Limited ORG — same bypass class)
    Org category    : HTTP=403  {"message":"token scope is limited to public orgs"}
    Repo category   : HTTP=200  README content                  ← bypass

Anonymous baseline (no auth) on every above endpoint: HTTP=401/404
```

Gitea's own server error string in PROBE F / H / O — *"token scope is limited
to public users"* / *"public orgs"* — is the explicit declaration of intent.
Repository / Package category violates that intent on the same Limited owner.

## Why this is not a duplicate of CVE-2026-25714

CVE-2026-25714 / PR #37118 (the May 2026 unification pass for public-only token
filtering, merged 2026-05-18, backported to 1.26.2 via PR #37773) realigned
`checkTokenPublicOnly`'s Org / User / ActivityPub cases on `!Visibility.IsPublic()`
and introduced the `TokenCanAccessRepo` helper for the Repository / Issue /
Notification cases.

PROBE F on `1.26.2` returns `403 "token scope is limited to public users"` for
the User category — i.e. PR #37118's unification IS in effect on the version
under test. The Repository / Package leak occurs *after* that fix; the Limited
gap is the next residual issue on the same hygiene effort (the Package case was
not touched, and `TokenCanAccessRepo` reduces to `!repo.IsPrivate` without
consulting owner visibility), not the same bug.

## Suggested fix (4 spots, 1-line shape each)

```go
// routers/api/v1/api.go:292  (checkTokenPublicOnly Package case)
- if ctx.Package != nil && ctx.Package.Owner.Visibility.IsPrivate() {
+ if ctx.Package != nil && !ctx.Package.Owner.Visibility.IsPublic() {

// routers/api/packages/api.go:76  (reqPackageAccess middleware)
- if ctx.Package != nil && ctx.Package.Owner.Visibility.IsPrivate() {
+ if ctx.Package != nil && !ctx.Package.Owner.Visibility.IsPublic() {

// services/context/api.go  (TokenCanAccessRepo helper)
- return repo == nil || !ctx.PublicOnly || !repo.IsPrivate
+ return repo == nil || !ctx.PublicOnly ||
+     (!repo.IsPrivate && repo.Owner != nil && repo.Owner.Visibility.IsPublic())

// services/context/permission.go:32  (CheckTokenScopes)
- if publicOnly && repo != nil && repo.IsPrivate {
+ if publicOnly && repo != nil &&
+     (repo.IsPrivate || (repo.Owner != nil && !repo.Owner.Visibility.IsPublic())) {
```

This aligns the Repository / Package categories with the User / Org / ActivityPub
siblings already shipped in PR #37118.
## Reporter

JebeenLee

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-7p4h-3gxq-x3h3
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
