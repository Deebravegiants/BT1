# [M] Gitea: API Fork Endpoint Authorization Bypass Allows Organization Members to Bypass Repository Creation Restrictions

## Summary
Severity: Medium
Advisory: GHSA-rjvx-x5h2-6px5
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-rjvx-x5h2-6px5
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.0

## Details
### Summary

The API endpoint used to fork repositories into organizations performs a weaker authorization check than the corresponding web UI and other repository creation endpoints.

When a repository is forked into an organization through the API, the endpoint only verifies that the user is an organization member (`IsOrgMember()`), but does not verify whether the user is allowed to create repositories in that organization (`CanCreateOrgRepo()`).

As a result, organization members belonging to teams with `can_create_org_repo=false` can still create repositories inside the organization by using the fork API.

### Details

Affected endpoint:

```
POST /api/v1/repos/{owner}/{repo}/forks
```

In `routers/api/v1/repo/fork.go`, the endpoint performs the following authorization check:

```go
if !ctx.Doer.IsAdmin {
    isMember, err := org.IsOrgMember(ctx, ctx.Doer.ID)
    if !isMember {
        ctx.APIError(http.StatusForbidden, ...)
        return
    }
}
```

The equivalent web UI implementation uses the stronger permission check:

```go
isAllowedToFork, err := organization.OrgFromUser(ctxUser).
    CanCreateOrgRepo(ctx, ctx.Doer.ID)
```

The same `CanCreateOrgRepo()` authorization check is also used by:

* CreateOrgRepo API endpoint
* GenerateRepository API endpoint

The fork endpoint appears to be the only repository creation path that relies solely on organization membership.

### Proof of Concept

Tested on Gitea 1.23.7.

1. Create an organization.
2. Create a team with `can_create_org_repo=false`.
3. Add a test user to that team.
4. Verify that normal repository creation is denied:

```http
POST /api/v1/orgs/target-org/repos
```

Result:

```http
403 Forbidden
```

5. Fork a repository into the organization:

```http
POST /api/v1/repos/admin/public-repo/forks
Content-Type: application/json

{
  "organization": "target-org"
}
```

Result:

```http
202 Accepted
```

The repository is successfully created despite repository creation permissions being disabled.

### Impact

Users who are organization members but are intentionally prevented from creating repositories can bypass that restriction through the API.

This allows unauthorized repository creation inside the organization and may expose additional attack surface depending on the organization's Actions, runner, and workflow configuration.

The vulnerability represents an authorization bypass because API behavior is less restrictive than both the web UI and other repository creation endpoints.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-rjvx-x5h2-6px5
- https://github.com/go-gitea/gitea/pull/36950
- https://github.com/go-gitea/gitea/commit/686d10b7f0c26baf91171124b382cbcdfa7bf025
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.0
