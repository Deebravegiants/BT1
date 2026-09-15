Found the analog. Let me check where `p.Token` is set/configured to confirm this handler is reachable from an unprivileged client and how the token is set up.### Title
Prometheus metrics endpoint bearer-token check uses non-constant-time `!=` comparison, enabling timing-attack brute force of `Prometheus.AuthToken` - ([File: core/web/router.go])

### Summary
The Prometheus `/metrics` endpoint is protected by a single shared bearer token (`Prometheus.AuthToken`), but the token comparison in `prometheusHandler` is a plain Go string inequality (`header != bearer`) rather than a constant-time comparison. This is the exact bug class described in CVE-2024-0436: a single, statically-configured secret compared via a short-circuiting `!=`/`!==` operator, which leaks timing information proportional to the number of matching prefix bytes and could in theory allow an unprivileged network client to brute-force the token faster than a naive full-keyspace guess.

### Finding Description
`prometheusUse` wires the `/metrics` route to `prometheusHandler(p.Token, h)`, where `p.Token` is populated from the operator-configured `Prometheus.AuthToken` secret [1](#0-0) . Inside `prometheusHandler`, if a token is configured, the incoming `Authorization` header is compared to the expected `"Bearer " + token` value using Go's built-in `!=` string operator:

```go
bearer := "Bearer " + token
if header != bearer {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
``` [2](#0-1) 

Go's `!=` on strings performs a byte-by-byte comparison that returns as soon as a mismatch is found (and also short-circuits on length differences), so the time taken to reject a request leaks information about how many leading bytes of the guessed token are correct. This mirrors the reported anything-llm bug where a single-user password was compared with `!==`, which is non-constant-time and enables brute-forcing via a timing side channel.

This is directly analogous to the codebase's other secret-verification code paths, which are careful to use `crypto/subtle.ConstantTimeCompare` specifically to avoid this class of bug — e.g. `AuthenticateUserByToken` [3](#0-2) , `AuthenticateBridgeType` [4](#0-3) , and `AuthenticateExternalInitiator` [5](#0-4) , plus the dedicated `constantTimeEmailCompare` helpers duplicated across `ldapauth`, `oidcauth`, and `localauth` [6](#0-5) . The Prometheus handler is the one place where a bearer-secret check was implemented with a plain `!=` instead of following this established constant-time pattern.

### Impact Explanation
If `Prometheus.AuthToken` is configured (documented in `docs/SECRETS.md` as "the authorization key for the Prometheus metrics endpoint" [7](#0-6) ), an unauthenticated network attacker who can reach the node's web server could theoretically exploit response-time differences to accelerate guessing of the token, ultimately gaining unauthorized read access to the `/metrics` endpoint (which can expose internal operational/telemetry data). Similar to the referenced CVE, real-world exploitability is limited by network jitter and the overhead of full HTTP request/response cycles, which make a reliable timing side channel hard to execute over a network, especially since Go string comparison differences here are on the order of nanoseconds per byte.

### Likelihood Explanation
Low-to-moderate. It requires: (1) `Prometheus.AuthToken` to be configured (it's optional — if empty, auth is skipped entirely per `if token == ""`) [8](#0-7) ; (2) network-level access to the metrics port; and (3) the ability to perform statistically significant timing measurements against the endpoint despite realistic network noise. This matches the low-confidence characterization in the original report.

### Recommendation
Replace the plain string comparison with a constant-time comparison, consistent with the rest of the codebase's secret-handling conventions:

```go
if subtle.ConstantTimeCompare([]byte(header), []byte(bearer)) != 1 {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
```

This aligns the Prometheus token check with the existing `subtle.ConstantTimeCompare` usage already present in `core/sessions/session.go`, `core/bridges/bridge_type.go`, and `core/bridges/external_initiator.go`.

### Proof of Concept
1. Configure `Prometheus.AuthToken = "supersecrettoken"` in the node's secrets TOML.
2. Send repeated `GET /metrics` requests with `Authorization: Bearer <guess>` headers where `<guess>` shares an increasing number of correct leading bytes with the real token.
3. Measure response latency for each guess over many trials; requests whose header comparison fails later (more matching prefix bytes) will, on average, take marginally longer due to the extra byte comparisons performed by `!=` before it short-circuits, versus a guess that mismatches at byte 0.

Note: I could not find any rate-limiting or additional constant-time protections wrapping this specific handler within the indexed code, and I was unable to fully trace how `ginprom.Prometheus.Token` field is populated from `cfg.Prometheus().AuthToken()` due to index coverage limits on `core/web/router.go`'s full initialization path — a Devin session with full repo access could confirm this wiring in more detail if needed.

### Citations

**File:** core/web/router.go (L671-673)
```go
	h := promhttp.InstrumentMetricHandler(r, promhttp.HandlerFor(g, handlerOpts))
	e.GET(p.MetricsPath, prometheusHandler(p.Token, h))
	p.Engine = e
```

**File:** core/web/router.go (L677-696)
```go
func prometheusHandler(token string, h http.Handler) gin.HandlerFunc {
	return func(c *gin.Context) {
		if token == "" {
			h.ServeHTTP(c.Writer, c.Request)
			return
		}

		header := c.Request.Header.Get("Authorization")

		if header == "" {
			c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
			return
		}

		bearer := "Bearer " + token

		if header != bearer {
			c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
			return
		}
```

**File:** core/sessions/session.go (L66-74)
```go
// AuthenticateUserByToken returns true on successful authentication of the
// user against the given Authentication Token.
func AuthenticateUserByToken(token *auth.Token, user *User) (bool, error) {
	hashedSecret, err := auth.HashedSecret(token, user.TokenSalt.ValueOrZero())
	if err != nil {
		return false, err
	}
	return subtle.ConstantTimeCompare([]byte(hashedSecret), []byte(user.TokenHashedSecret.ValueOrZero())) == 1, nil
}
```

**File:** core/bridges/bridge_type.go (L104-112)
```go
// AuthenticateBridgeType returns true if the passed token matches its
// IncomingToken, or returns false with an error.
func AuthenticateBridgeType(bt *BridgeType, token string) (bool, error) {
	hash, err := incomingTokenHash(token, bt.Salt)
	if err != nil {
		return false, err
	}
	return subtle.ConstantTimeCompare([]byte(hash), []byte(bt.IncomingTokenHash)) == 1, nil
}
```

**File:** core/bridges/external_initiator.go (L59-67)
```go
// AuthenticateExternalInitiator compares an auth against an initiator and
// returns true if the password hashes match
func AuthenticateExternalInitiator(eia *auth.Token, ea *ExternalInitiator) (bool, error) {
	hashedSecret, err := auth.HashedSecret(eia, ea.Salt)
	if err != nil {
		return false, err
	}
	return subtle.ConstantTimeCompare([]byte(hashedSecret), []byte(ea.HashedSecret)) == 1, nil
}
```

**File:** core/sessions/localauth/orm.go (L232-241)
```go
const constantTimeEmailLength = 256

func constantTimeEmailCompare(left, right string) bool {
	length := mathutil.Max(constantTimeEmailLength, len(left), len(right))
	leftBytes := make([]byte, length)
	rightBytes := make([]byte, length)
	copy(leftBytes, left)
	copy(rightBytes, right)
	return subtle.ConstantTimeCompare(leftBytes, rightBytes) == 1
}
```

**File:** docs/SECRETS.md (L133-146)
```markdown
## Prometheus
```toml
[Prometheus]
AuthToken = "prometheus-token" # Example
```


### AuthToken
```toml
AuthToken = "prometheus-token" # Example
```
AuthToken is the authorization key for the Prometheus metrics endpoint.

Environment variable: `CL_PROMETHEUS_AUTH_TOKEN`
```
