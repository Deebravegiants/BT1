### Title
Non-constant-time bearer token comparison in Prometheus metrics endpoint enables timing side-channel token recovery - ([File: core/web/router.go])

### Summary
The Prometheus metrics HTTP endpoint compares the caller-supplied `Authorization` header against the configured secret token using Go's native string inequality operator (`!=`), which performs a byte-by-byte, short-circuiting comparison. This is the same bug class described in the referenced CVE (timing-channel disclosure of a secret via non-constant-time comparison), applied here to a live, internet-facing, unauthenticated HTTP handler.

### Finding Description
`prometheusHandler` builds the expected value as `"Bearer " + token` and then checks it against the caller's header using plain string comparison: [1](#0-0) 

```
header := c.Request.Header.Get("Authorization")
...
bearer := "Bearer " + token
if header != bearer {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
```

Go's `string != string` comparison returns as soon as it finds the first differing byte, so the time taken to reject a request is proportional to the number of correct leading bytes in the guess. This is architecturally the same class of vulnerability as the reported PostgreSQL MD5-password timing channel — a secret comparison that is not constant-time.

This is notable because the rest of this codebase explicitly recognizes non-constant-time comparison as a real threat and consistently uses `crypto/subtle.ConstantTimeCompare` for secret/token verification everywhere else:
- User API token verification: [2](#0-1) 
- Bridge incoming token verification: [3](#0-2) 
- LDAP/OIDC email comparisons: [4](#0-3) , [5](#0-4) 

The Prometheus metrics handler is the one place where a static, long-lived credential (`PrometheusAuthToken`, configured via `core/services/chainlink/config.go`) is checked with a naive `!=` comparison instead of `subtle.ConstantTimeCompare`, breaking that otherwise-consistent pattern. It is wired into the router via `prometheusUse`, which registers it on `p.MetricsPath` (default `/metrics`) as an unauthenticated GET route reachable from any client that can reach the node's HTTP listener: [6](#0-5) 

### Impact Explanation
An attacker who can send repeated HTTP requests to the `/metrics` endpoint and measure response timing can incrementally recover the `PrometheusAuthToken` byte-by-byte, since a match on more leading bytes causes the comparison (and therefore the branch/response) to take measurably longer to fail than a mismatch on an early byte. Once recovered, the attacker gains authenticated access to the Prometheus metrics endpoint, which can expose internal operational/telemetry data about the node. This is a genuine unprivileged-actor credential-disclosure vector reachable over the node's exposed HTTP API, analogous to the reported CVE class (secret comparison timing side-channel leading to credential recovery).

### Likelihood Explanation
Exploitation requires the operator to have configured a non-empty `PrometheusAuthToken` (if empty, the check is skipped entirely per line 679 `if token == "" { ... }`), and requires the attacker to perform a timing attack over the network, which is noisier than a local side-channel and needs statistical averaging over many requests. This raises the difficulty of exploitation but doesn't eliminate it — timing attacks against short, fixed-prefix HTTP comparisons over LAN/low-jitter networks are practical and have been demonstrated in real-world settings (this is the exact bug class of the reported CVE). Likelihood is moderate: it depends on network jitter and whether the token is enabled, but the vulnerable code path itself is unconditionally present and reachable pre-authentication.

### Recommendation
Replace the direct string comparison in `prometheusHandler` with a constant-time comparison, consistent with the rest of the codebase's pattern:
```go
if subtle.ConstantTimeCompare([]byte(header), []byte(bearer)) != 1 {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
```
Additionally, consider hashing the token server-side (as is done for user API tokens and bridge tokens) rather than storing/comparing it in plaintext, to further reduce risk if the comparison logic is ever regressed.

### Proof of Concept
1. Configure a node with `PrometheusAuthToken` set to a secret value, exposing `/metrics` per the wiring in [7](#0-6) .
2. From an unauthenticated network position, send repeated `GET /metrics` requests with `Authorization: Bearer <guess>` headers, incrementing correctly-guessed prefix bytes while measuring response latency for the branch taken at [8](#0-7) .
3. Statistically distinguish "more leading bytes correct" (marginally slower rejection, since `!=` scans further before diverging) from "leading byte wrong" (faster rejection) to recover the token byte-by-byte over repeated samples.
4. Use the recovered token to authenticate directly to `/metrics` with `Authorization: Bearer <token>`.

**Note on uncertainty:** I was unable to fully confirm from the index how latency-observable the comparison is in practice (e.g., whether TLS termination, proxying, or Go's compiler optimizations on short string comparisons meaningfully affect exploitability), since I don't have access to run the code or a network-level PoC. The root cause (non-constant-time comparison of a secret token in an unauthenticated handler) is confirmed directly from the source, but real-world exploitability would depend on network conditions not visible from static analysis alone.

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

**File:** core/web/router.go (L684-696)
```go
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

**File:** core/sessions/oidcauth/oidc.go (L648-656)
```go
func constantTimeEmailCompare(left, right string) bool {
	const constantTimeEmailLength = 256
	length := mathutil.Max(constantTimeEmailLength, len(left), len(right))
	leftBytes := make([]byte, length)
	rightBytes := make([]byte, length)
	copy(leftBytes, left)
	copy(rightBytes, right)
	return subtle.ConstantTimeCompare(leftBytes, rightBytes) == 1
}
```
