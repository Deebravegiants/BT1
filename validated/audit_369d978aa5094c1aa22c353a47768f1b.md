## Analysis

The external report describes a **timing side-channel in credential comparison** — an early-exit, non-constant-time string comparison during authentication that lets an attacker infer secret bytes by measuring response latency across repeated requests.

Searching the chainlink codebase for analogous unprivileged-reachable secret comparisons, most authentication paths correctly use timing-safe comparisons: bcrypt's `CheckPasswordHash` [1](#0-0)  for session passwords, and `subtle.ConstantTimeCompare` for API tokens and external-initiator secrets [2](#0-1) [3](#0-2) .

However, the Prometheus metrics endpoint's bearer-token check uses a plain Go `!=` string comparison, which is **not constant-time** and is directly reachable by an unauthenticated network client hitting `/metrics`.

### Title
Non-constant-time Bearer token comparison on Prometheus metrics endpoint enables timing side-channel token recovery - ([File: core/web/router.go])

### Summary
The `prometheusHandler` middleware that protects the `/metrics` HTTP endpoint compares the client-supplied `Authorization` header against the configured secret token using a native string inequality operator (`!=`) rather than a constant-time comparison function.

### Finding Description
`prometheusHandler` is registered as the gin handler for the metrics path [4](#0-3) . Inside it, the expected value is built as `"Bearer " + token` and compared directly against the request's `Authorization` header value:
```go
bearer := "Bearer " + token
if header != bearer {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
``` [5](#0-4) 

Go's `!=` operator on strings performs a byte-by-byte comparison that returns as soon as a mismatch is found, so the time taken to reject an invalid token is proportional to the number of correct leading bytes supplied by the attacker. This is precisely the bug class in the referenced advisory (CVE-2021-33880): an "Observable Timing Discrepancy" in a credential check performed on unauthenticated HTTP requests, enabling a timing attack to incrementally guess the correct secret. Unlike the rest of the authentication code in this repo — which deliberately uses `subtle.ConstantTimeCompare` for API/external-initiator tokens [2](#0-1)  and bcrypt (inherently constant-time per comparison) for passwords [1](#0-0)  — this one path was missed.

### Impact Explanation
The `Prometheus.AuthToken` secret [6](#0-5)  gates a metrics endpoint that is often internet- or network-reachable. An attacker who can measure response timing with sufficient precision (byte-at-a-time or statistical timing attack) could recover the token without any prior credentials. Once recovered, the attacker gains authorized access to the node's `/metrics` endpoint, which can expose internal operational data (queue depths, job counts, chain/latency stats, potentially sensitive labels) useful for reconnaissance or further attacks. This does not directly grant fund movement or job execution, but is a genuine unprivileged-actor credential-disclosure primitive matching the "key/secret disclosure" acceptance criterion.

### Likelihood Explanation
Exploitability requires network access to the metrics port and the ability to perform many timed requests to statistically distinguish microsecond-level timing differences — feasible but non-trivial over the public internet (though much easier on a LAN or low-jitter path). CVSS for the analogous CVE is rated High for AC:H (high attack complexity), consistent with this instance: it is a real, root-caused issue but requires a sophisticated attacker and favorable network conditions.

### Recommendation
Replace the direct string comparison with `crypto/subtle.ConstantTimeCompare` (converting both sides to `[]byte` of equal length, or hashing both with HMAC/SHA-256 first to normalize length before comparing), matching the pattern already used elsewhere in this codebase for token/secret checks (e.g., `AuthenticateUserByToken`, `AuthenticateExternalInitiator`).

### Proof of Concept
1. Configure a node with `[Prometheus] AuthToken = "<secret>"`.
2. Send repeated GET requests to `/metrics` with `Authorization: Bearer <guess>` where `<guess>` varies by one trailing byte at a time.
3. Measure response latency for each guess; because `!=` short-circuits at the first mismatched byte, correct-prefix guesses take measurably longer to reject than incorrect-prefix guesses.
4. Iterate byte-by-byte to reconstruct the full `AuthToken` without ever needing a valid credential.

### Citations

**File:** core/utils/utils.go (L131-135)
```go
// CheckPasswordHash wraps around bcrypt.CompareHashAndPassword for a friendlier API.
func CheckPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
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

**File:** core/config/prometheus.go (L1-7)
```go
package config

type Prometheus interface {
	AuthToken() string
}


```
