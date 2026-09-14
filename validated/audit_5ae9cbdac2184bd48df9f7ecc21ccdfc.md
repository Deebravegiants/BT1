### Title
Non-constant-time comparison of the Prometheus metrics bearer token enables a timing side-channel - (File: core/web/router.go)

### Summary
The `/metrics` endpoint's bearer-token check in `prometheusHandler` compares the caller-supplied `Authorization` header against the configured secret using Go's native `!=` string comparison instead of a constant-time comparison, unlike other secret/token comparisons in the same codebase (e.g. `subtle.ConstantTimeCompare` used in `bridges.AuthenticateExternalInitiator` and `constantTimeEmailCompare` in the LDAP/OIDC authenticators). This is analogous to the report's class of "inaccurate/weaker protections than the rest of the system provides," where one code path silently uses a weaker guarantee than the pattern established elsewhere.

### Finding Description
`prometheusHandler` builds the expected value as `"Bearer " + token` and checks it against the client-supplied header with a plain `!=` comparison: [1](#0-0) 

This is a byte-by-byte, short-circuiting comparison, so response latency leaks information about how many leading bytes of the guessed token match the real secret. Elsewhere in the same repository, this exact class of secret comparison is deliberately hardened with `subtle.ConstantTimeCompare`: [2](#0-1) 

and with a dedicated constant-time helper for authentication in the LDAP/OIDC providers: [3](#0-2) 

The Prometheus metrics route registration wires this weaker comparison directly into an HTTP handler reachable by any unauthenticated network client that can reach the metrics port: [4](#0-3) 

### Impact Explanation
A successful timing attack would let an unauthenticated network client recover the Prometheus metrics bearer token byte-by-byte and then access `/metrics`, which chainlink/ginprom based instrumentation could expose internal counters/labels. The impact is limited: it doesn't grant admin/session/API-key access to the node's job/wallet functionality, only to the metrics scrape endpoint, and only when a non-empty `Token` is configured (`token == ""` skips auth entirely, which is a separate, intentional "no-auth" mode). Practical exploitability of pure network timing side-channels is also generally noisy and requires many samples, which lowers real-world severity.

### Likelihood Explanation
Likelihood is low-to-moderate: it requires (1) the operator to have configured a Prometheus auth token (a nonstandard/optional setting) and (2) the endpoint to be reachable over a network path with a sufficiently low-noise timing signal (e.g., LAN or same-host adversary). It is not exploitable purely from the "internet-facing gateway" surfaces described in the report, but it is a genuine unprivileged-client-reachable authentication weakness in a node-facing HTTP handler.

### Recommendation
Replace the `header != bearer` check with a constant-time comparison, consistent with the pattern already used elsewhere in the codebase:
```go
if subtle.ConstantTimeCompare([]byte(header), []byte(bearer)) != 1 {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
```

### Proof of Concept
1. Configure the node with `WebServer.Prometheus.AuthToken` (mapped to `p.Token` in `prometheusUse`) set to a secret value, exposing `/metrics` on the configured `MetricsPath`.
2. From a network position with low jitter to the target (e.g., same host or same LAN segment), send repeated `GET /metrics` requests with `Authorization: Bearer <guess>` headers, incrementally brute-forcing one byte at a time and measuring response latency for the `header != bearer` comparison in `prometheusHandler`.
3. Because the comparison short-circuits on the first mismatched byte, correct-prefix guesses take measurably (if slightly) longer to reach the mismatch point than incorrect ones, allowing incremental byte recovery of the token.
4. Once the full token is recovered, use it to authenticate to `/metrics` as if authorized.

### Citations

**File:** core/web/router.go (L660-674)
```go
// prometheusUse is adapted from ginprom.Prometheus.Use
// until merged upstream: https://github.com/Depado/ginprom/pull/48
func prometheusUse(p *ginprom.Prometheus, e *gin.Engine, handlerOpts promhttp.HandlerOpts) {
	var (
		r prometheus.Registerer = p.Registry
		g prometheus.Gatherer   = p.Registry
	)
	if p.Registry == nil {
		r = prometheus.DefaultRegisterer
		g = prometheus.DefaultGatherer
	}
	h := promhttp.InstrumentMetricHandler(r, promhttp.HandlerFor(g, handlerOpts))
	e.GET(p.MetricsPath, prometheusHandler(p.Token, h))
	p.Engine = e
}
```

**File:** core/web/router.go (L676-700)
```go
// use is adapted from ginprom.prometheusHandler to add support for custom http.Handler
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

		h.ServeHTTP(c.Writer, c.Request)
	}
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

**File:** core/sessions/ldapauth/ldap.go (L814-823)
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
