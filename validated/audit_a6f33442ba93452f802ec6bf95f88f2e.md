### Title
Non-constant-time bearer token comparison in Prometheus metrics endpoint enables timing attack against the auth token - ([File: core/web/router.go])

### Summary
The `/metrics` endpoint authentication in `prometheusHandler` compares the client-supplied `Authorization` header directly against the expected `"Bearer " + token` string using Go's built-in `!=` operator, which performs a byte-by-byte, early-exit string comparison rather than a constant-time comparison.

### Finding Description
`prometheusHandler` is wired up via `prometheusUse`, which registers it as the handler for the Prometheus metrics path (`e.GET(p.MetricsPath, prometheusHandler(p.Token, h))`) [1](#0-0) . The handler reads the `Authorization` header from the unauthenticated, internet-reachable HTTP request and does a direct string comparison against the expected bearer token:

```go
bearer := "Bearer " + token
if header != bearer {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
``` [2](#0-1) 

Go's `!=` on strings short-circuits at the first mismatching byte, so the time taken to reject an incorrect token leaks how many leading characters were guessed correctly — exactly the bug class described in the vLLM advisory (CVE-2025-59425), where `==`/direct string comparison on a bearer/API token allowed statistical recovery of the secret one character at a time.

This is notably inconsistent with the rest of the codebase's authentication paths, which correctly use `subtle.ConstantTimeCompare` for token/secret validation:
- `AuthenticateUserByToken` (session/API token auth) [3](#0-2) 
- `AuthenticateBridgeType` (bridge incoming token) [4](#0-3) 
- `AuthenticateExternalInitiator` (external initiator secret) [5](#0-4) 
- email comparisons in LDAP/OIDC/local auth (`constantTimeEmailCompare`) [6](#0-5) 

The Prometheus metrics handler is the one bearer-token check in the codebase that was not updated to use `subtle.ConstantTimeCompare`.

### Impact Explanation
An unprivileged, unauthenticated network client sending requests to the metrics endpoint can, in principle, use response-timing measurements to incrementally recover the configured Prometheus auth token, one prefix-byte at a time, without needing to brute-force the entire token space. Once recovered, the token grants access to the `/metrics` endpoint, which typically exposes internal operational and possibly sensitive runtime metrics about the node.

### Likelihood Explanation
Exploitation requires the operator to have configured a non-empty Prometheus auth token (`token == ""` skips the check entirely) and requires the endpoint to be reachable over a network path where timing signal is measurable (statistical timing attacks over real networks require many requests and are noisier than local ones, but are a well-documented class of exploitable weakness, as demonstrated by the referenced vLLM CVE). This is a lower-severity/harder-to-execute variant relative to a local-network or same-host attacker, but the root cause (non-constant-time comparison of a secret token supplied by the caller) is a direct structural match to the reported bug class.

### Recommendation
Replace the direct string comparison in `prometheusHandler` with a constant-time comparison, consistent with the rest of the codebase, e.g.:
```go
if subtle.ConstantTimeCompare([]byte(header), []byte(bearer)) != 1 {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
```

### Proof of Concept
1. Configure a Prometheus auth token (`Prometheus.AuthToken` per `core/services/chainlink/config.go`), enabling the check path in `prometheusHandler`.
2. Send repeated GET requests to the metrics path with `Authorization: Bearer <guess>` headers, incrementally varying guessed prefix characters and measuring response latency via statistical averaging over many requests, analogous to the technique described in GHSA-wr9h-g72x-mwhm for vLLM's API key check.
3. Because `header != bearer` short-circuits at the first differing byte, correct-prefix guesses will exhibit a statistically detectable, larger elapsed time than incorrect-prefix guesses, allowing incremental token recovery character-by-character rather than requiring full brute force.

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

**File:** core/web/router.go (L676-699)
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
