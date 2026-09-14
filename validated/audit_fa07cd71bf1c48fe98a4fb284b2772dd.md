### Title
Non-constant-time token comparison on the `/metrics` Prometheus endpoint allows timing attack to brute-force `Prometheus.AuthToken` - (File: `core/web/router.go`)

### Summary
The chainlink node's Prometheus metrics HTTP endpoint authenticates requests by comparing the `Authorization` header against a `Bearer <token>` string using Go's native `!=` string comparison instead of a constant-time comparison. This is the same bug class as the referenced authentik CVE-2024-52307, where a non-constant-time comparison on a metrics endpoint's auth secret enabled a timing attack to recover the secret.

### Finding Description
`prometheusHandler` builds the expected value as `"Bearer " + token` and compares it to the request's `Authorization` header with plain Go string inequality: [1](#0-0) 

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
}
```

Go's `!=` for strings short-circuits on the first mismatched byte, leaking timing information proportional to the length of the correct-prefix match, exactly the flaw described in the authentik advisory for its `/-/metrics/` endpoint. This handler is wired into the node's public-facing gin engine via `prometheusUse`, which registers it on the metrics path of the same engine returned by `NewRouter`: [2](#0-1) [3](#0-2) 

Notably, every other authentication/secret-comparison path in this codebase (session tokens, bridge tokens, external initiator tokens, LDAP/OIDC email comparisons) correctly uses `crypto/subtle.ConstantTimeCompare`, e.g.: [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) 

This makes `prometheusHandler`'s plain `!=` comparison an outlier and the direct analog of the reported bug class: a metrics endpoint secured by a bearer token compared in non-constant time.

The token itself comes from operator configuration (`Prometheus.AuthToken`), documented as a sensitive secret: [8](#0-7) [9](#0-8) 

### Impact Explanation
If an unprivileged network client can reach the node's metrics path with many requests, the non-constant-time `!=` comparison leaks timing signal about how many leading bytes of the guessed bearer token match the real `Prometheus.AuthToken`. Over many measurements this can allow statistical recovery of the token, granting the attacker read access to `/metrics` (internal counters, potentially operational/topology information about the node). This mirrors the authentik disclosure impact: brute-forcing a secret meant to gate a metrics endpoint.

### Likelihood Explanation
Exploitability depends heavily on deployment: if the metrics endpoint is exposed on the public listener (same gin `engine` as the rest of the web routes, per `NewRouter`/`prometheusUse`) and not blocked by an external reverse proxy, an unauthenticated network attacker can send high volumes of timed requests. Realistic exploitation of Go string-comparison timing differences over a network is difficult (network jitter dominates single-byte timing differences) but not impossible with enough samples/statistical averaging, matching the "Medium" severity assigned to the original CVE for the same class of issue. Likelihood is reduced if operators do not set `Prometheus.AuthToken` (auth is skipped entirely) or if the metrics path is firewalled/only bound to an internal interface — but the code itself provides no constant-time guarantee.

### Recommendation
Replace the string equality check in `prometheusHandler` with `crypto/subtle.ConstantTimeCompare` on byte slices of equal padded length (consistent with the pattern already used elsewhere in this codebase, e.g. `constantTimeEmailCompare` in `core/sessions/localauth/orm.go`), for example:

```go
if subtle.ConstantTimeCompare([]byte(header), []byte(bearer)) != 1 {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
```

### Proof of Concept
1. Configure a node with `Prometheus.AuthToken` set to a long secret.
2. Send repeated HTTP requests to the metrics path with `Authorization: Bearer <guess>` where `<guess>` varies only in later bytes, measuring response latency for the `header != bearer` branch in `prometheusHandler` (`core/web/router.go:693`).
3. Statistically average response times per guessed prefix length to detect where the comparison fails later (indicating a correct prefix), progressively recovering the token byte-by-byte — analogous to the authentik `/-/metrics/` SECRET_KEY brute-force technique described in the advisory.

### Citations

**File:** core/web/router.go (L47-61)
```go
// NewRouter returns *gin.Engine router that listens and responds to requests to the node for valid paths.
func NewRouter(app chainlink.Application, prometheus *ginprom.Prometheus) (*gin.Engine, error) {
	engine := gin.New()
	engine.RemoteIPHeaders = nil // don't trust default headers: "X-Forwarded-For", "X-Real-IP"
	config := app.GetConfig()
	secret, err := app.SecretGenerator().Generate(config.RootDir())
	if err != nil {
		return nil, err
	}
	sessionStore := cookie.NewStore(secret)
	sessionStore.Options(config.WebServer().SessionOptions())
	cors := uiCorsHandler(config.WebServer().AllowOrigins())
	if prometheus != nil {
		prometheusUse(prometheus, engine, promhttp.HandlerOpts{EnableOpenMetrics: true})
	}
```

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

**File:** core/config/prometheus.go (L1-5)
```go
package config

type Prometheus interface {
	AuthToken() string
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
