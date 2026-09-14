## Finding: Non-constant-time comparison of the Prometheus metrics bearer token allows timing-based token disclosure

The reported CVE (Nova's instance-metadata signature check) is a textbook case of a security-sensitive secret comparison performed without constant-time semantics, letting a remote unauthenticated actor use response-timing differences to incrementally guess the correct value. The chainlink codebase has a direct analog in the internet-facing metrics endpoint authentication.

### Title
Non-constant-time comparison of the Prometheus metrics bearer token enables timing side-channel token disclosure - (File: core/web/router.go)

### Summary
The `/metrics` endpoint is protected by a bearer token check in `prometheusHandler`, but the comparison uses Go's native `!=` string operator instead of a constant-time comparison function.

### Finding Description
`prometheusHandler` is wired up via `prometheusUse`, which is invoked from `NewRouter` whenever a `*ginprom.Prometheus` is configured, exposing `p.MetricsPath` (typically `/metrics`) on the node's HTTP API surface [1](#0-0) . The handler extracts the `Authorization` header and compares it against the expected `"Bearer " + token` value using plain string inequality:

```go
bearer := "Bearer " + token
if header != bearer {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
``` [2](#0-1) 

Go's `!=` operator on strings performs a byte-by-byte comparison and returns as soon as a mismatch is found (length check first, then a linear scan), so a value that matches more leading bytes of the true token will, in expectation, take a small but measurable amount of extra time to reject compared to one that mismatches earlier. This is exactly the class of bug described in the report: a secret/signature comparison whose implementation leaks timing information, enabling a byte-by-byte brute-force attack against the shared secret.

This contrasts with how the rest of the authentication surface in this codebase is implemented — every other secret/token comparison in the API auth paths explicitly uses `crypto/subtle.ConstantTimeCompare` to avoid exactly this class of leak, e.g. `AuthenticateUserByToken` [3](#0-2) , `AuthenticateExternalInitiator` [4](#0-3) , `AuthenticateBridgeType` [5](#0-4) , and the LDAP/OIDC email comparisons [6](#0-5) . The Prometheus metrics bearer-token check at `core/web/router.go:693` is the one place in the HTTP-facing authentication surface that deviates from this pattern.

### Impact Explanation
If an attacker can measure response timing with enough precision (feasible even over a network with sufficient statistical sampling, and trivially over localhost/same-host access), they could incrementally recover the metrics bearer token byte-by-byte far faster than brute-forcing the full token space. Possessing the token grants unauthenticated read access to the node's `/metrics` endpoint, which can expose internal operational and possibly sensitive information about the node (CWE-200 information exposure), matching the "Exposure of Sensitive Information to an Unauthorized Actor" classification of the reference CVE.

### Likelihood Explanation
Exploitability is Medium: it requires the operator to have configured a Prometheus token (`prometheusUse` is only invoked when a `*ginprom.Prometheus` is passed in) and requires an attacker capable of performing high-precision timing measurements against the endpoint, which is harder over noisy public networks but realistic for attackers on the same host/network segment or via statistical averaging.

### Recommendation
Replace the direct string comparison in `prometheusHandler` with `subtle.ConstantTimeCompare([]byte(header), []byte(bearer)) == 1` (after a constant-time length check, since `ConstantTimeCompare` returns 0 immediately for differing lengths without leaking timing beyond that), consistent with the constant-time comparison pattern already used throughout `core/auth`, `core/bridges`, and `core/sessions`.

### Proof of Concept
1. Configure a chainlink node with Prometheus metrics enabled and a bearer token set.
2. Send repeated requests to `/metrics` with `Authorization: Bearer <guess>` where `<guess>` varies by one trailing character at a time.
3. Measure response latency for early-mismatch guesses vs. late-mismatch guesses (i.e., guesses that share a longer correct prefix). Statistically average out noise over many requests.
4. Because `header != bearer` at `core/web/router.go:693` short-circuits on the first mismatched byte, correctly-prefixed guesses will show a measurable timing bias, allowing incremental recovery of the token.

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
