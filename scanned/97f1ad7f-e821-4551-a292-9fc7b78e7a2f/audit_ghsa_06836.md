# [M] Gitea: Public-only API token restriction is not enforced on team API routes

## Summary
Severity: Medium
Advisory: GHSA-h56g-4qw7-2mxg
CVE: CVE-2026-58431
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-h56g-4qw7-2mxg
Type: github-advisory

## Affected
- Go: `gitea.dev` — affected >=0 <1.27.0

## Details
### Summary

Gitea's `/api/v1/teams/{id}` API routes do not correctly enforce the `public-only` access token restriction.

A `public-only` token is intended to limit API access to public repositories and public organizations. However, several team API routes continue to return private team repository metadata and private team activity feed entries when called with a `public-only` token.

### Details

The `/api/v1/teams/{teamid}` route group uses:

```go
orgAssignment(false, true)
```

This loads `ctx.Org.Team`, but does not load `ctx.Org.Organization`.

The `checkTokenPublicOnly` middleware checks organization visibility through `ctx.Org.Organization`. When `ctx.Org.Organization` is nil, the organization visibility check silently passes.

In addition, the team repository handlers return repositories without applying repository-level `public-only` filtering:

```go
repo_model.GetTeamRepositories(...)
convert.ToRepo(...)
```

They do not call:

```go
ctx.TokenCanAccessRepo(repo)
```

The team activity feed handler also sets:

```go
IncludePrivate: true
```

but does not apply:

```go
opts.ApplyPublicOnly(ctx.PublicOnly)
```

### PoC

Vulnerability is verified on latest gitea release (1.26.2) and nightly build.
Frist, create a `public-only` organization-scoped token for a user who is a member of a team in a private org with private repositories:

<img width="1075" height="577" alt="image" src="https://github.com/user-attachments/assets/4a01d0ab-f67c-47c9-94b1-e74ddd77d7bc" />

<img width="649" height="375" alt="image" src="https://github.com/user-attachments/assets/b5d91962-088e-40f4-bc51-88a17946e6d8" />

Use the returned token to request team repositories:

<img width="1728" height="190" alt="image" src="https://github.com/user-attachments/assets/0f15878f-5806-431d-958c-ffb39bf7c1e9" />

Expected result: Private repositories should be hidden or rejected for a public-only token.
Actual result: Private team repository metadata is returned.

The team activity feed endpoint can be tested similarly:

<img width="1728" height="237" alt="image" src="https://github.com/user-attachments/assets/280a5ddf-ad14-4769-86a8-1fdad858287c" />

### Impact

A `public-only` token can access private team resources that should be hidden from that token.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-h56g-4qw7-2mxg
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
