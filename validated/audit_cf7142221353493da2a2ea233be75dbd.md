The relevant analog to CVE-2017-2624 (timing side-channel via non-constant-time secret comparison) is a real, distinct pattern in the codebase, and it stands out precisely because the rest of the authentication code base already defends against it.

Every other credential-comparison path in the repo explicitly uses `crypto/subtle.ConstantTimeCompare`: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

However, the Prometheus metrics endpoint bearer-token check in `prometheusHandler` in `core/web/router.go` uses a plain Go string inequality (`!=`) instead of a constant-time comparison: [6](#0-5) 

This handler is wired directly into the main internet-facing gin engine that serves the node's HTTP API: [7](#0-6) 

### Title
Non-constant-time bearer token comparison enables timing-based brute force of the Prometheus metrics endpoint auth token - (File: core/web/router.go)

### Summary
The `/metrics` endpoint exposed by `prometheusUse`/`prometheusHandler` compares the client-supplied `Authorization` header against the configured bearer token using Go's native `!=` string comparison, which (like C's `memcmp`, the root cause of CVE-2017-2624) short-circuits on the first mismatching byte. This produces a measurable timing difference correlated with how many leading bytes of the guessed token are correct, enabling an efficient byte-by-byte timing attack to recover the token.

### Finding Description
`prometheusHandler` builds `bearer := "Bearer " + token` and checks `if header != bearer`. Go's string comparison, like memcmp, compares byte-by-byte and returns as soon as a mismatch is found, so the amount of time taken depends on the length of the correct prefix shared between the attacker's guess and the real token — exactly the same class of flaw described in CVE-2017-2624 for Xorg's MIT-cookie comparison. All other credential-comparison sites in this codebase (session tokens, external-initiator secrets, bridge tokens, LDAP/OIDC email checks) correctly use `subtle.ConstantTimeCompare`, showing that this is a real inconsistency rather than an intentional design choice. [8](#0-7) 

### Impact Explanation
If the operator configures a Prometheus auth token (`Prometheus.AuthToken` per `core/services/chainlink/config.go`), an unauthenticated remote attacker able to reach the metrics endpoint can use timing measurements to incrementally guess the token byte-by-byte, bypassing the intended protection and gaining unauthorized access to metrics data (which can include internal operational/telemetry information about the node).

### Likelihood Explanation
Exploitation requires network access to the `/metrics` path and a configured non-empty token (if the token is empty, no auth is enforced at all per the `token == ""` branch), plus the ability to make many timed requests and average out network jitter — a well-understood, previously demonstrated attack class (same as CVE-2017-2624), making this a credible but non-trivial "AC:H"-style attack.

### Recommendation
Replace the plain `!=` string comparison with `subtle.ConstantTimeCompare([]byte(header), []byte(bearer)) == 1` (matching the pattern already used elsewhere in the codebase, e.g. in `core/sessions/session.go` and `core/bridges/external_initiator.go`), ensuring equal-length inputs or hashing before comparison to avoid leaking length information as well.

### Proof of Concept
1. Configure the node with `Prometheus.AuthToken = "supersecrettoken"` and expose the `/metrics` endpoint.
2. From a network position with low-jitter access to the endpoint, send repeated requests with `Authorization: Bearer <guess>` while incrementally brute-forcing each byte of the token, measuring response latency for `header != bearer` at line 693.
3. Because the comparison exits early on the first differing byte, correct-prefix guesses will show a measurably higher average latency than incorrect ones, allowing incremental recovery of the full token without ever needing all `256^n` combinations at once — the same efficient timing attack methodology described in CVE-2017-2624.

### Citations

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
