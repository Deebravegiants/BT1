# [M] Cloudreve: Information Exposure in `GET /api/v4/user/search`: `SearchActive` omits the active-status predicate, leaking inactive/banned account emails

## Summary
Severity: Medium
Advisory: GHSA-8r7f-r8hj-r3rv
CVE: CVE-2026-55496
CWE: CWE-200, CWE-359
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-8r7f-r8hj-r3rv
Type: github-advisory

## Affected
- Go: `github.com/cloudreve/Cloudreve/v4` — affected >=0 <4.0.0-20260613023921-7e1289d55279
- Go: `github.com/cloudreve/Cloudreve/v3` — affected >=0

## Details
## Summary
 
`GET /api/v4/user/search` is available to any logged-in user. The service calls `userClient.SearchActive`, but despite its name that method filters only by email/nickname keyword and **never adds a `StatusActive` predicate** — while the sibling lookups `GetActiveByID` and `GetActiveByDavAccount`, defined a few lines above it, do. Search hits are serialized at `RedactLevelUser`, which includes the email address.
 
A normal logged-in user can therefore enumerate and retrieve the email (plus nickname, avatar, creation time, redacted group, profile share-visibility) of **inactive and banned** accounts that an active-user directory is supposed to suppress. No global status interceptor compensates — the only User query interceptor is soft-delete, and inactive/banned rows are not soft-deleted.

### Details
## Root cause (verified at `26b6b10`)
 
**1. Route — logged-in + `UserInfo.Read` scope** (`routers/router.go`):
```go
user := v4.Group("user")            // protected user group (login required)
user.GET("search",
    middleware.RequiredScopes(types.ScopeUserInfoRead),
    controllers.FromQuery[usersvc.SearchUserService](...), controllers.UserSearch)
```
The `RequiredScopes` check applies to scoped OAuth tokens; plain session requests are not gated by it — so any logged-in user reaches the search.
 
**2. Service — 2-char keyword to `SearchActive`** (`service/user/info.go`):
```go
type SearchUserService struct { Keyword string `form:"keyword" binding:"required,min=2"` }
const resultLimit = 10
func (s *SearchUserService) Search(c *gin.Context) ([]*ent.User, error) {
    return dep.UserClient().SearchActive(c, resultLimit, s.Keyword)
}
```
 
**3. The bug — `SearchActive` has no status predicate** (`inventory/user.go`):
```go
func (c *userClient) SearchActive(ctx context.Context, limit int, keyword string) ([]*ent.User, error) {
    ctx = context.WithValue(ctx, LoadUserGroup{}, true)
    return withUserEagerLoading(ctx,
        c.client.User.Query().
            Where(user.Or(user.EmailContainsFold(keyword), user.NickContainsFold(keyword))).
            Limit(limit),                       // <-- no user.StatusEQ(user.StatusActive)
    ).All(ctx)
}
```
Contrast the siblings immediately above:
```go
func (c *userClient) GetActiveByID(...)        { ... Where(user.ID(id)).Where(user.StatusEQ(user.StatusActive)) ... }
func (c *userClient) GetActiveByDavAccount(...) { ... Where(user.EmailEqualFold(email)).Where(user.StatusEQ(user.StatusActive)) ... }
```
`withUserEagerLoading` only eager-loads the group/passkey edges; it adds no status filter. Status values are `active`/`inactive`/`manual_banned`/`sys_banned` (`ent/user/user.go`).
 
**4. No global status interceptor** — `User.Mixin()` is `CommonMixin{}` (`ent/schema/user.go`), whose `Interceptors()` returns only `softDeleteInterceptors` (`ent/schema/common.go`). Inactive/banned users are not soft-deleted, so nothing filters them out at query time.
 
**5. Results serialized with email** (`routers/controllers/user.go` → `service/user/response.go`):
```go
// UserSearch:
return user.BuildUserRedacted(item, user.RedactLevelUser, hasher)
// BuildUserRedacted:
if level == RedactLevelUser { user.Email = userRaw.Email }   // email included
```
 
**Secondary path:** `GET /api/v4/user/info/:id` → `GetUser` uses `GetByID` (no status filter), and the controller picks `RedactLevelUser` for any non-anonymous caller (`RedactLevelAnonymous` only for anonymous). So a logged-in caller with an inactive/banned user's hashed ID also receives the email-bearing profile. (Less practical than search, since it needs the hashed ID rather than a 2-char keyword.)

## Steps to reproduce (requires a live instance)
 
1. Ensure a target account exists in `inactive` or `manual_banned`/`sys_banned` status (e.g., an unconfirmed registration or a banned user).
2. As any logged-in user:
   ```
   GET /api/v4/user/search?keyword=<>=2 chars of the target email/nick>
   Cookie: cloudreve-session=<attacker-session>
   ```
3. Observe the inactive/banned account in the results, including its `email`.
**Expected:** only active accounts appear (matching the method name and the sibling `GetActive*` behavior).
**Actual:** inactive/banned accounts are returned with their email addresses.
 
## Impact
 
Any logged-in user can enumerate and harvest the email addresses (and basic profile metadata) of inactive and banned accounts that active-user lookups intentionally hide. No account access, passwords, or 2FA secrets are exposed; the impact is PII leakage and user enumeration.
 
## Remediation
 
- Add `Where(user.StatusEQ(user.StatusActive))` to `SearchActive` (matching `GetActiveByID`).
- Apply the same active-status requirement to `GET /api/v4/user/info/:id`, or fall back to anonymous-level redaction unless the target account is active.
- Consider not returning email from directory search at all — display name + hashed ID is usually sufficient.
- Regression tests: searching a keyword that matches an inactive/banned account must return no result (or no email).

## References
- https://github.com/cloudreve/cloudreve/security/advisories/GHSA-8r7f-r8hj-r3rv
- https://github.com/cloudreve/cloudreve/commit/7e1289d552794bdbeb551be78456115c87dcb3da
- https://github.com/cloudreve/cloudreve
- https://github.com/cloudreve/cloudreve/releases/tag/4.17.0
