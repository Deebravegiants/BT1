# [M] GitHub MCP Server: Lockdown mode singleton in HTTP server causes cross-user GraphQL client confusion

## Summary
Severity: Medium
Advisory: GHSA-pjp5-fpmr-3349
CVE: CVE-2026-48529
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-pjp5-fpmr-3349
Type: github-advisory

## Affected
- Go: `github.com/github/github-mcp-server` — affected >=0.22.0 <1.1.2

## Details
### Summary

When running in HTTP mode with --lockdown-mode enabled, the RepoAccessCache is implemented as a process-global singleton initialized with the first authenticated user's GraphQL client. All subsequent requests from different users share this singleton and their lockdown-related GraphQL queries are executed using the first user's credentials. The singleton is never updated to reflect later users' tokens.

### Details

The singleton is defined in pkg/lockdown/lockdown.go:

```go
var (
    instance   *RepoAccessCache
    instanceMu sync.Mutex
)

func GetInstance(client *githubv4.Client, opts ...RepoAccessOption) *RepoAccessCache {
    instanceMu.Lock()
    defer instanceMu.Unlock()
    if instance == nil {
        instance = &RepoAccessCache{
            client: client,  // only stored on first call
        }
    }
    return instance  // subsequent callers receive the same object regardless of their client
}
```

In HTTP mode, pkg/github/dependencies.go calls this per request:

```go
func (d *RequestDeps) GetRepoAccessCache(ctx context.Context) (*lockdown.RepoAccessCache, error) {
    gqlClient, err := d.GetGQLClient(ctx)  // creates client with request's token
    ...
    instance := lockdown.GetInstance(gqlClient, d.RepoAccessOpts...)
    // gqlClient is silently dropped if singleton already exists
    return instance, nil
}
```

The singleton's internal client field is never updated after the first initialization. All lockdown GraphQL queries that check repository access and visibility (queryRepoAccessInfo, called by IsSafeContent) run under the first authenticated user's token for the lifetime of the process.

IsSafeContent is called in at least six places across pkg/github/issues.go and pkg/github/pullrequests.go to decide whether to trust or sanitize content from external contributors.

### PoC

The following program demonstrates that two distinct GraphQL clients produce the same singleton pointer, confirming that the second client is discarded:

```go
package main

import (
    "fmt"
    "net/http"
    "github.com/github/github-mcp-server/pkg/lockdown"
    "github.com/shurcooL/githubv4"
)

func main() {
    httpClientA := &http.Client{}
    httpClientB := &http.Client{}
    gqlClientA := githubv4.NewEnterpriseClient("https://api.github.com/graphql", httpClientA)
    gqlClientB := githubv4.NewEnterpriseClient("https://api.github.com/graphql", httpClientB)

    fmt.Printf("gqlClientA (user A token): %p\n", gqlClientA)
    fmt.Printf("gqlClientB (user B token): %p\n", gqlClientB)
    fmt.Printf("clients are different objects: %v\n\n", gqlClientA != gqlClientB)

    instanceForA := lockdown.GetInstance(gqlClientA)
    instanceForB := lockdown.GetInstance(gqlClientB)

    fmt.Printf("lockdown instance returned for user A: %p\n", instanceForA)
    fmt.Printf("lockdown instance returned for user B: %p\n", instanceForB)
    fmt.Printf("same singleton returned for both users: %v\n", instanceForA == instanceForB)
}
```

Output:

```
gqlClientA (user A token): 0x400044070
gqlClientB (user B token): 0x400044078
clients are different objects: true

lockdown instance returned for user A: 0x400002ecc0
lockdown instance returned for user B: 0x400002ecc0
same singleton returned for both users: true
```

<img width="1642" height="450" alt="image" src="https://github.com/user-attachments/assets/bec46420-9ba7-458e-8710-62f951cb836a" />


### Impact

This affects deployments running the HTTP server with --lockdown-mode, which is the intended configuration for multi-user scenarios such as GitHub Copilot's managed MCP endpoint.

Three concrete consequences:

First, the ViewerLogin field in cache entries always reflects the first authenticated user's identity. The IsSafeContent check `repoInfo.ViewerLogin == strings.ToLower(username)` compares this stale value against each subsequent user's login, producing incorrect results for all users except the first.

Second, repository visibility and collaborator access data stored in the cache is evaluated through the first user's token. If user A cannot see a private repository but user B can (or vice versa), the cached isPrivate and hasPushAccess values will reflect user A's view of that repository, causing IsSafeContent to return wrong decisions for user B. In lockdown mode, a wrong true result means potentially injected content from untrusted external contributors is passed to the model without sanitization.

Third, if the first user's token is revoked or expires, all subsequent lockdown GraphQL queries fail with authentication errors. Since getRepoAccessInfo propagates these errors, IsSafeContent returns an error for every request, breaking lockdown protection for all users until the process is restarted.

## References
- https://github.com/github/github-mcp-server/security/advisories/GHSA-pjp5-fpmr-3349
- https://github.com/github/github-mcp-server
