# [M] Gitea: API access token scope enforcement bypass on repository RSS/Atom feed endpoints leaks private repository commit data

## Summary
Severity: Medium
Advisory: GHSA-3pww-vcvm-3gmj
CVE: CVE-2026-27761
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-3pww-vcvm-3gmj
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.3

## Details
### Summary
A Gitea personal access token (PAT) restricted to a non-repository scope (e.g. `read:issue`) can read the commit history of any private repository the token owner can access, via the repository RSS/Atom feed endpoints. The same token is correctly denied (403) on `/raw`, `/media`, `/archive`, and the contents API. It leaks commit SHAs, full commit messages (which frequently contain secrets and internal context), and committer name + email.

### Details
Gitea enforces PAT scope on repository-content endpoints via `checkDownloadTokenScope()` (added in PR #37698, extended to the archive endpoint by the CVE-2026-20706 fix in 1.26.2). The RSS/Atom feed handlers were never included: they (a) opt into PAT auth via `webAuth.AllowBasic`, (b) serve private-repo content, but (c) never call `checkDownloadTokenScope()`.

Affected handlers (all carry `AllowBasic`, none call the scope check):
- `RenderBranchFeedRSS/Atom` - `routers/web/feed/render.go` (last 10 commits: SHA, title, full message, committer name + email)
- `ShowFileFeed` - `routers/web/feed/file.go` (per-file commit history)
- repo activity feed `/{owner}/{repo}.rss` / `.atom`
- `TagsListFeedRSS/Atom`, `ReleasesFeedRSS/Atom` - `routers/web/repo/release.go`

Root cause: `routers/web/web.go` registers the feed routes with `webAuth.AllowBasic` so a PAT authenticates, but the unit-permission middleware only checks the user's access, not the token's scope. `checkDownloadTokenScope` (`routers/web/repo/download.go` and the archive `Download` in `repo.go`) exists to close exactly that gap and is absent from the feed handlers. Same class as the recently fixed download/archive bypasses (GHSA-cr4g-f395-h25h / CVE-2026-20706); the feeds are the surface those fixes missed.

### PoC
Tested on `gitea/gitea:1.26.2-rootless`, confirmed present at `main` HEAD (9608cc2, 2026-06-13).
1. User `carol` owns private repo `carol/priv` with a commit (message: "add confidential secret").
2. Create a PAT scoped to issues only, no repository scope:
   `curl -u carol:PASS -X POST $HOST/api/v1/users/carol/tokens -d '{"name":"t","scopes":["read:issue"]}'`
3. Scope-enforcing sibling correctly denies it:
   `curl -u carol:$TOK $HOST/carol/priv/raw/branch/main/secret.txt`  ->  403
4. The feed leaks private data with the same token:
   `curl -u carol:$TOK $HOST/carol/priv/rss/branch/main`  ->  200, returns
   `<description>add confidential secret ... this commit message itself is sensitive</description>`

| Auth (same read:issue token) | /raw/branch/main/secret.txt | /rss/branch/main |
|---|---|---|
| anonymous | - | 404 (private repo hidden) |
| invalid token | - | 401 |
| read:issue token (no repo scope) | 403 (scope enforced) | 200 + private commit data |
| full-scope token | 200 | 200 (legitimate) |

### Impact
PATs are routinely issued narrowly and handed to third-party bots, CI jobs, or chat integrations that are meant to have no code access. This bypass lets such a token exfiltrate private-repository commit history (messages often hold secrets, ticket refs, internal context) and committer emails for every repository the owner can read. Confidentiality only; no integrity or availability impact. Preconditions: a valid PAT of any non-repository scope owned by a user with read access to the target private repo, and feeds enabled (`Other.EnableFeed`, default ON).

Suggested fix: call `checkDownloadTokenScope(ctx)` at the start of each feed handler (mirroring `download.go`). Longer-term, enforce repository token scope in a single route-group middleware wherever `AllowBasic` / `AllowOAuth2` is set on a repo-content route, so the next added endpoint cannot miss it.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-3pww-vcvm-3gmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-27761
- https://github.com/go-gitea/gitea/pull/38147
- https://github.com/go-gitea/gitea/commit/9e84deb969aff5c1115c2984e41250f28c78451f
- https://blog.gitea.com/release-of-1.26.3-and-1.26.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.3
