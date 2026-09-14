### Title
Non-constant-time comparison of Prometheus bearer token allows timing side-channel attack - ([File: core/web/router.go])

### Summary
The `/metrics` endpoint authentication in `prometheusHandler` compares the caller-supplied `Authorization` header against the configured secret bearer token using Go's native `!=` string comparison rather than a constant-time comparison primitive. This mirrors the CVE-2013-1624 bug class (Bouncy Castle CBC-padding MAC check): a secret-bearing comparison implemented without timing-side-channel mitigations, enabling a remote attacker to distinguish correct vs. incorrect prefix bytes of the secret via response timing.

### Finding Description
`prometheusHandler` in `core/web/router.go` guards the Prometheus metrics endpoint with a shared-secret bearer token supplied via node config: [1](#0-0) 

The critical comparison is:
```go
bearer := "Bearer " + token
if header != bearer {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
```
Go's `!=` on strings short-circuits at the first mismatching byte, so the time taken to reject a request is a function of how many leading bytes of the attacker-supplied header match the real secret. This is the same class of bug identified in the external report: a MAC/secret comparison implemented without constant-time semantics, allowing timing-based recovery of secret material.

By contrast, every other secret/token comparison in this codebase (API key/secret auth, external initiator auth, session email compare, bridge token auth) explicitly uses `crypto/subtle.ConstantTimeCompare` to avoid exactly this issue: [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

This makes `prometheusHandler` the outlier: the one place a shared secret is checked with a variable-time comparison, reachable by any unauthenticated network client hitting the metrics path.

### Impact Explanation
An attacker who can reach the metrics endpoint (mounted via `prometheusUse`, registered as a `GET` route on the gin engine) can send repeated requests with guessed `Authorization: Bearer <guess>` headers and use statistical timing analysis to incrementally recover the correct token, byte by byte — analogous to the padding-oracle/MAC-timing attack described in the Bouncy Castle advisory. A successfully recovered token grants read access to internal Prometheus metrics, which can leak operational/internal state (job counts, chain/latency data, potentially sensitive labels) that should require the configured secret.

### Likelihood Explanation
Exploitation requires: (1) the node operator has configured a non-empty `PrometheusAuthToken` (if empty, the endpoint is unauthenticated by design and not part of this analog), and (2) the attacker has network access to the metrics port. Practical exploitation of Go string-comparison timing differences over a network is noisy and requires many samples/statistical averaging, similar to the original TLS CBC-padding timing attacks — feasible but non-trivial, especially over WAN latency. This keeps likelihood at low-to-medium, consistent with the Medium severity of the underlying CVE analog.

### Recommendation
Replace the raw string comparison in `prometheusHandler` with a constant-time comparison, mirroring the pattern already used elsewhere in the codebase, e.g.:
```go
if subtle.ConstantTimeCompare([]byte(header), []byte(bearer)) != 1 {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
```
Additionally consider hashing/HMAC-ing the token server-side (as done for API tokens/bridge tokens) so that even the length of the secret is not implicitly leaked via comparison behavior.

### Proof of Concept
1. Configure a chainlink node with Prometheus metrics enabled and a non-empty auth token (`Prometheus.AuthToken` per `core/services/chainlink/config.go`).
2. From an unauthenticated network position, send many `GET /metrics` requests with `Authorization: Bearer <candidate>` headers, incrementally brute-forcing the token one byte at a time and measuring response latency for each candidate prefix.
3. Because `header != bearer` in `core/web/router.go` returns as soon as a mismatch is found, correct-prefix guesses will exhibit a measurably longer processing path (matching more bytes before the mismatch) than incorrect ones over sufficient trials, allowing incremental token recovery — analogous to the CBC-padding timing oracle in the referenced Bouncy Castle CVE. [1](#0-0)

### Citations

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

**File:** core/web/auth/auth.go (L92-107)
```go
	// We need to first load the user row so we can compare tokens using the stored salt
	user, err := authr.FindUserByAPIToken(ctx, token.AccessKey)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) || errors.Is(err, clsessions.ErrUserSessionExpired) {
			return auth.ErrorAuthFailed
		}
		return err
	}

	ok, err := clsessions.AuthenticateUserByToken(token, &user)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
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
