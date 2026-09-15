### Title
Non-constant-time Prometheus metrics Bearer token comparison enables timing side-channel - (File: core/web/router.go)

### Summary
The `/metrics` endpoint guard in `prometheusHandler` compares the caller-supplied `Authorization` header against the expected bearer token using Go's native `!=` string comparison instead of a constant-time comparison, mirroring the root cause of GHSA-vg5x-6q66-rvgx (Barzahlen `Webhook::verify` using non-constant-time comparison for secret verification).

### Finding Description
`prometheusHandler` builds the expected value as `"Bearer " + token` and then does a direct short-circuiting string comparison against the request's `Authorization` header: [1](#0-0) 

Go's `==`/`!=` on strings short-circuits on the first mismatching byte, so the time taken to reject an incorrect header leaks the number of correct leading bytes of the shared secret token. This is architecturally identical to the reported bug class (CWE-208 Observable Timing Discrepancy / CWE-203 Information Exposure Through Discrepancy): a secret-bearing token is verified with a variable-time equality check reachable by an unauthenticated network caller, rather than `crypto/subtle.ConstantTimeCompare` or an HMAC-based digest comparison.

This is notably inconsistent with the rest of the authentication surface in the same codebase, which correctly uses `subtle.ConstantTimeCompare` for equivalent secret-verification operations:
- API token auth: [2](#0-1) 
- External initiator auth: [3](#0-2) 
- Bridge incoming token auth: [4](#0-3) 
- LDAP/OIDC email comparisons: [5](#0-4) 

The `prometheusHandler` path is the outlier that performs a raw variable-time comparison of attacker-supplied input against a static secret.

### Impact Explanation
An unprivileged network client that can reach the node's `/metrics` endpoint (protected only by this static bearer token, configured via `PrometheusAuthToken`/similar ginprom config) can perform a byte-by-byte timing attack to incrementally recover the shared Prometheus token. Once recovered, the attacker gains unauthorized access to internal metrics, which on a Chainlink node can expose operational details (job counts, queue depths, error rates, potentially chain/labels) useful for further reconnaissance or DoS targeting — impact is confidentiality/information-disclosure rather than direct fund movement, consistent with the CVSS vector of the original advisory (C:L/I:N/A:N).

### Likelihood Explanation
Exploitability requires: (1) the Prometheus token feature being enabled with a non-empty token (`token == ""` bypasses the check entirely, so this only matters when auth is configured), and (2) network-level timing measurement precision sufficient to distinguish per-byte comparison differences, which is a well-established, practical technique over both LAN and, with enough samples, WAN links. No authentication or privilege beyond basic HTTP access to the metrics port is required, matching the "unprivileged-actor, internet-facing gateway" scope of this analog.

### Recommendation
Replace the direct string comparison in `prometheusHandler` with a constant-time comparison, consistent with the pattern already used elsewhere in the codebase:
```go
if subtle.ConstantTimeCompare([]byte(header), []byte(bearer)) != 1 {
    c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
    return
}
```
Ensure both byte slices are of equal, fixed length before comparison (or pad, as done in `constantTimeEmailCompare`) to avoid leaking length information as well.

### Proof of Concept
1. Configure a node with Prometheus metrics auth enabled (non-empty token) as wired in `prometheusUse`/`prometheusHandler`.
2. Send repeated HTTP GET requests to the metrics path with `Authorization: Bearer <guess>` headers, incrementally brute-forcing one byte at a time from the token prefix.
3. Measure response latency for each guess at `header != bearer` in [6](#0-5) ; guesses that match more leading bytes of the true token take marginally longer to reject due to the extra byte comparisons performed by the runtime before the mismatch is detected.
4. Repeat per byte position to reconstruct the full token, granting unauthorized access to `/metrics`.

### Citations

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
