### Title
Timing attack on Prometheus metrics endpoint bearer token due to non-constant-time comparison - (File: core/web/router.go)

### Summary
The `prometheusHandler` function that protects the `/metrics` Prometheus endpoint compares the client-supplied `Authorization` header against the expected bearer token using a plain Go string inequality (`!=`) rather than a constant-time comparison, mirroring the CWE-367 timing-attack root cause described in the Gradio advisory (GHSA-hmx6-r76c-85g9), where early-exit string comparison in Python leaked information about how many leading characters matched.

### Finding Description
`prometheusHandler` builds the expected value as `"Bearer " + token` and compares it to the request's `Authorization` header with the native `!=` operator: [1](#0-0) 

Go's `!=` on strings, like Python's `==`, short-circuits at the first byte mismatch, so the time taken to reject a request is proportional to the number of correctly guessed leading characters of the bearer token. This is architecturally the same bug class as the reported Gradio vulnerability: an unrated, publicly reachable endpoint performs a non-constant-time secret comparison, enabling a byte-by-byte timing-based brute force of the token.

By contrast, every other authentication path in this codebase (session/API-token auth, external-initiator auth, bridge auth) explicitly uses `crypto/subtle.ConstantTimeCompare` or bcrypt hash comparison to avoid exactly this issue, e.g.: [2](#0-1) [3](#0-2) [4](#0-3) 

The Prometheus metrics handler is the outlier that never received this hardening, and it is wired directly into the gin `Engine` as a `GET` route with no rate limiting: [5](#0-4) 

### Impact Explanation
If `PrometheusAuthToken` is configured, an unauthenticated network client can send repeated `GET` requests to the metrics path with different guessed `Authorization: Bearer <guess>` values and use response timing differences to recover the token byte-by-byte, eventually bypassing authentication and gaining unauthorized read access to the node's internal Prometheus metrics (which can reveal operational/internal state). This matches the "unauthorized access via authentication bypass" impact class validated for this analog.

### Likelihood Explanation
Exploitation requires network access to the node's metrics port and depends on measurable timing differences over the network, which is noisy but has been shown practical for such issues (this is precisely the underlying condition the referenced advisory patched). There is no rate-limiting or lockout on this endpoint, and no evidence of any wrapper making the comparison constant-time, so likelihood is moderate — consistent with the CVSS "AC:H" (high attack complexity) rating of the original advisory.

### Recommendation
Replace the `header != bearer` check in `prometheusHandler` with a constant-time comparison, consistent with the rest of the codebase's convention, e.g. `subtle.ConstantTimeCompare([]byte(header), []byte(bearer)) != 1`, and consider adding basic rate limiting on the metrics endpoint.

### Proof of Concept
1. Configure a node with `PrometheusAuthToken` set (protecting `/metrics`).
2. As an unauthenticated network client, send repeated requests to `GET /metrics` with `Authorization: Bearer <guess>` headers, varying guessed prefixes.
3. Measure response latency for each guess; because `header != bearer` in `core/web/router.go` short-circuits at the first mismatching byte, correct-prefix guesses take measurably longer to reject than incorrect ones.
4. Iteratively refine the guess byte-by-byte using the timing signal to reconstruct the full token, ultimately bypassing the `Authorization` check to access `/metrics` without a valid token.

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

**File:** core/web/router.go (L677-699)
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

		h.ServeHTTP(c.Writer, c.Request)
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
