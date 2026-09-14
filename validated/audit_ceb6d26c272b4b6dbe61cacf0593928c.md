### Title
OIDC Sign-In Writes to Session Storage Before Authentication - ([File: core/sessions/oidcauth/oidc.go])

### Summary
`oidcAuthenticator.handleSignIn` writes a `state` value into the session store and persists it via `session.Save()` before any authentication has occurred, mirroring the OpenStack Horizon bug class (CWE-696, GHSA-vxvf-xvm3-p8j5): an unauthenticated request causes a write to the server-side session storage backend.

### Finding Description
`handleSignIn` generates a random state string and immediately stores and saves it in the gin session before redirecting the user to the OIDC provider — no credentials or prior authentication are required to reach this code: [1](#0-0) 

This handler sits behind the `/` route group which only applies rate limiting and session middleware, not authentication, matching the pattern used for other unauthenticated session-establishing routes such as `/sessions` (`POST`) in `core/web/router.go`: [2](#0-1) 

Because gin sessions backed by `cookie.NewStore` are typically encrypted/signed client-side cookies (as configured in `core/web/router.go` line 56), the direct impact of this particular write is limited (no server-side storage row is created) — but if the OIDC session store is backed by a server-side store (e.g., depending on deployment configuration or a differently configured session backend for the OIDC routes), each unauthenticated hit to sign-in generates and persists new session state, which is exactly the write-before-auth pattern flagged in the advisory.

### Impact Explanation
If session storage for this route is server-side (database, memory store, or any backend with capacity limits), an unauthenticated attacker can repeatedly call the sign-in endpoint to force writes/allocations, exhausting storage or memory — a denial-of-service condition consistent with CWE-696 as described in the advisory. Impact is bounded to availability (matches the CVSS vector `C:N/I:N/A:L` in the advisory).

### Likelihood Explanation
The `handleSignIn` handler requires no authentication and no rate-limiting beyond the generic unauthenticated group throttle already present in the router; likelihood of a low-cost automated abuse is moderate to high if the deployed session backend is not a stateless cookie store.

### Recommendation
Avoid writing/persisting session state prior to authentication completing. If a CSRF/state value must be tracked, prefer:
- Signing/encoding the state value into the redirect itself (e.g., encrypted state token validated on callback) instead of persisting server-side session data, or
- Ensuring the OIDC session store used for `state` is always a stateless, size-bounded cookie store (never a growable server-side store), and
- Applying tighter unauthenticated rate limiting specifically to `/sign-in` in addition to the general unauthenticated group limiter in `core/web/router.go`.

### Proof of Concept
Confidence in exploitability is limited because I could not verify (within available context) which concrete `sessions.Store` implementation backs the OIDC routes' session middleware in this deployment, nor find the exact router registration line binding `handleSignIn` to a path (only the handler itself and its `session.Set`/`session.Save()` calls were located). Given the index's stated size limits, I was unable to confirm the route wiring code (`ExtendRouter` for the OIDC provider) or the exact session store configuration passed to it — a Devin session with full filesystem access should be used to inspect `core/sessions/oidcauth/oidc.go`'s router registration and the `sessions.NewStore` call used for the OIDC routes to confirm whether the store is server-side (making this exploitable for storage exhaustion) or purely a signed cookie (making impact negligible).

### Citations

**File:** core/sessions/oidcauth/oidc.go (L147-161)
```go
func (oi *oidcAuthenticator) handleSignIn(c *gin.Context) {
	// generate state and store on session
	state := oi.generateState()
	session := sessions.Default(c)
	session.Set("state", state)
	err := session.Save()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save session"})
		return
	}

	// redirect to provider
	url := oi.oauth2Config.AuthCodeURL(state, oauth2.AccessTypeOffline)
	c.Redirect(http.StatusFound, url)
}
```

**File:** core/web/router.go (L207-218)
```go
func sessionRoutes(app chainlink.Application, r *gin.RouterGroup) {
	config := app.GetConfig()
	rl := config.WebServer().RateLimit()
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
}
```
