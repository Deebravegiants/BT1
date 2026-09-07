# [M] Gitea: Incomplete CVE-2025-68941 fix: /user/orgs missing checkTokenPublicOnly + switch-case logic flaw

## Summary
Severity: Medium
Advisory: GHSA-8629-vc8r-5p58
CVE: CVE-2026-25714
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-8629-vc8r-5p58
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.2

## Details
## Summary

Two related issues in the token public-only scope enforcement introduced by PR #32204 (CVE-2025-68941 fix). A public-only scoped API token can access private organization data.

## Issue 1: /user/orgs missing checkTokenPublicOnly()

`routers/api/v1/api.go` line 1599:
```go
m.Get("/user/orgs", reqToken(), tokenRequiresScopes(
    auth_model.AccessTokenScopeCategoryUser,
    auth_model.AccessTokenScopeCategoryOrganization,
), org.ListMyOrgs)
// Missing checkTokenPublicOnly()
```

Adjacent route at line 1603 has it:
```go
m.Group("/users/{username}/orgs", func() { ... },
    ..., checkTokenPublicOnly())
```

## Issue 2: checkTokenPublicOnly switch-case evaluates only first matching category

`routers/api/v1/api.go` lines 253-295. Go switch executes only the first matching case. For routes with categories [User, Organization]:

1. Organization case matches first (line 263)
2. ctx.Org.Organization is nil on user routes, passes
3. ctx.ContextUser.IsOrganization() is false, passes
4. User case (line 273) is never reached
5. User visibility check skipped entirely

## Steps to Reproduce

1. Create a token with public-only scope (Settings > Applications > check "public only")
2. Call: `curl -H "Authorization: token <PUBLIC_ONLY_TOKEN>" https://gitea.example.com/api/v1/user/orgs`
3. Response includes private and limited-visibility organizations

Expected: only public organizations returned.

## Impact

Public-only scoped tokens can enumerate private organizations the token owner belongs to. Violates the token's declared scope constraints.

## Suggested Fix

1. Add `checkTokenPublicOnly()` to `/user/orgs` route at line 1599
2. Replace switch with loop over all categories so User visibility check is not skipped

## Version

Current main branch, commit 2c2d7e6 (April 3, 2026).

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-8629-vc8r-5p58
- https://github.com/go-gitea/gitea
