### Title
Prometheus metrics endpoint bearer token compared with non-constant-time `!=` string comparison, vulnerable to timing attacks - ([File: core/web/router.go])

### Summary
The `/metrics` endpoint authentication in `prometheusHandler` compares the caller-supplied `Authorization` header directly against the configured secret bearer token using Go's native `!=` string operator instead of a constant-time comparison, unlike every other secret-comparison path in this codebase.

### Finding Description
`prometheusHandler` builds the expected value as `"Bearer " + token` (where `token` is `PrometheusSecrets.AuthToken`, exposed via `config.Prometheus.AuthToken()`) and compares it to the request's `Authorization` header using `header != bearer`: [1](#0-0) 

Go's `!=` on strings short-circuits at the first differing byte, so the comparison time leaks information about how many leading bytes of the guessed token are correct — the classic CWE-208 timing side channel referenced in the external Spring Boot DevTools advisory (secret comparison via non-constant-time equality).

This stands in sharp contrast to the rest of the authentication surface in this repository, all of which explicitly use `crypto/subtle.ConstantTimeCompare` for secret/token verification: [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

The route is registered unauthenticated-by-default at the gin-engine level and only gated by this handler: [6](#0-5) 

The secret itself is a static, long-lived TOML-configured value (`PrometheusSecrets.AuthToken`), not salted/hashed per request: [7](#0-6) 

### Impact Explanation
An unprivileged network-adjacent attacker who can send repeated HTTP requests to the metrics endpoint could, in principle, use response-timing differences on the `header != bearer` comparison to incrementally recover the configured Prometheus `AuthToken`. Once recovered, the attacker gains access to the `/metrics` endpoint, which can expose internal operational/telemetry data about the node. This does not by itself grant fund movement or job execution, but it is a genuine authentication-bypass-via-secret-disclosure primitive matching the CWE-208 bug class from the report.

### Likelihood Explanation
Exploitability is constrained by real-world timing-attack feasibility over HTTP/network jitter, which is why the original Spring Boot advisory itself carries `AC:H` (high attack complexity) despite being rated High severity. The same caveat applies here: this is a plausible but non-trivial exploitation path requiring many timed requests and a favorable low-noise network position (`AV:A`-like access is most realistic, i.e., same-network attacker, not fully remote-anonymous). Likelihood is Low-to-Medium.

### Recommendation
Replace the plain `!=` comparison with a constant-time comparison consistent with the rest of the codebase, e.g.:
```go
if subtle.ConstantTimeCompare([]byte(header), []byte(bearer)) != 1 {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
```
This mirrors the pattern already used in `core/sessions/session.go`, `core/bridges/external_initiator.go`, and `core/bridges/bridge_type.go`.

### Proof of Concept
1. Configure a node with `Prometheus.AuthToken = "supersecrettoken"`.
2. From a network-adjacent host, send repeated `GET /metrics` requests with `Authorization: Bearer <guess>` headers, incrementally brute-forcing byte-by-byte while measuring response latency of the `header != bearer` comparison path in `prometheusHandler`.
3. Statistically significant timing differences between early-mismatch and late-mismatch guesses reveal correct-prefix bytes, allowing incremental secret reconstruction — analogous to CVE-2026-40972's DevTools remote secret timing attack.

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

**File:** core/services/chainlink/config_prometheus.go (L1-16)
```go
package chainlink

import (
	"github.com/smartcontractkit/chainlink/v2/core/config/toml"
)

type prometheusConfig struct {
	s toml.PrometheusSecrets
}

func (p *prometheusConfig) AuthToken() string {
	if p.s.AuthToken == nil {
		return ""
	}
	return string(*p.s.AuthToken)
}
```
