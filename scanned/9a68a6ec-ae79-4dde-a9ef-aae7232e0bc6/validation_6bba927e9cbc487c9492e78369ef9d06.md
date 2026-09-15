### Title
JWT request-auth window can exceed the intended maximum token lifetime by combining `issuedAtTolerance` and `maxExpiryDuration` - (File: `core/utils/jwt.go`)

### Summary
`VerifyRequestJWT` bounds the JWT lifetime by checking `exp - iat <= maxExpiryDuration` and separately allows `iat` to be up to `issuedAtTolerance` in the future relative to the verifier's clock. Because these two independently-configurable/default bounds are enforced separately rather than against the combined value measured from the verifier's actual "now", a token's real validity window (from the verifier's perspective) can be up to `issuedAtTolerance + maxExpiryDuration`, not the intended `maxExpiryDuration`. This is the same bug class as the referenced Gondi finding: two values that are each bounded individually are added together at runtime, and the sum is never checked against the hard maximum the code is trying to enforce.

### Finding Description
`VerifyRequestJWT` in `core/utils/jwt.go` performs two independent checks: [1](#0-0) 

- `issuedAt` (`iat`) is allowed to be up to `issuedAtTolerance` (default `defaultIssuedAtTolerance = 5 * time.Minute`) ahead of the verifier's real clock.
- The token's `duration = exp - iat` is capped at `maxExpiryDuration` (default `maxJWTExpiryDuration = 5 * time.Minute`). [2](#0-1) 

Both checks are only ever validated against each other's *relative* reference point (`iat`), never against the combined bound from the verifier's actual `now()`. A caller that crafts `iat = now + issuedAtTolerance` and `exp = iat + maxExpiryDuration` passes both checks, yet the token remains valid (`exp > now`) for up to `issuedAtTolerance + maxExpiryDuration` (up to 10 minutes by default) from the moment of verification — double the intended 5-minute maximum lifetime the function is designed to enforce. This mirrors the referenced pattern exactly: the code fixes a maximum via one bound (`_liquidationAuctionDuration < MAX_AUCTION_DURATION`) while ignoring that another independently-configurable addend (`getMaxExtension`) can push the effective combined value past the intended hard cap.

This function is reachable by unprivileged remote callers: `WorkflowMetadataHandler.Authorize` in the gateway's HTTP-trigger capability path calls `utils.VerifyRequestJWT(token, *req)` with no options (so defaults apply) to authenticate/authorize workflow-execute requests coming from workflow nodes through the Gateway: [3](#0-2) 

The same handler maintains a JWT replay cache keyed by `jti` with a TTL of `JWTReplayPeriodMs`: [4](#0-3) 

If the configured/default `JWTReplayPeriodMs` (`defaultJWTReplayPeriodMs`, defined in `http_handler.go`) is shorter than the actual maximum achievable token lifetime (`issuedAtTolerance + maxExpiryDuration`), a captured token could, in principle, remain cryptographically valid (per `VerifyRequestJWT`) after its `jti` has already been evicted from the replay-protection cache, weakening the intended replay-window guarantee. I was not able to confirm the exact numeric value of `defaultJWTReplayPeriodMs` from the indexed content, so this secondary replay-window implication is noted as unverified and should be checked directly in `core/services/gateway/handlers/capabilities/v2/http_handler.go`.

### Impact Explanation
The primary, directly provable impact is that the intended hard cap on JWT lifetime (`maxJWTExpiryDuration`, 5 minutes) is not actually enforced end-to-end: a token can remain valid for up to double that duration (10 minutes) from the verifier's true clock, because the future-dated-`iat` tolerance and the `exp-iat` duration cap are checked independently instead of against the combined effective validity window. This weakens the freshness/short-lived-token security property that `VerifyRequestJWT` is designed to provide for authenticating workflow-execute requests at the Gateway, extending the attack window for token replay or reuse if the token or its signature material is intercepted.

### Likelihood Explanation
Likelihood is limited by the fact that an attacker still needs a validly-signed token (signed with the legitimate node's private key, per the ECDSA `SigningMethodEth` signature check) — this is not an authentication bypass, but a bound-enforcement gap that only doubles the effective validity/replay window of an already-obtained valid token. It requires the caller (which controls `iat`/`exp` when creating its own token via `CreateRequestJWT`, or an interceptor of a legitimately-issued token) to deliberately set `iat` near the future tolerance edge and `exp` at `iat + maxExpiryDuration`. No caller-supplied override is required since the defaults themselves already allow this doubling.

### Recommendation
Enforce the maximum token lifetime against the verifier's actual clock rather than against `iat` alone, e.g.:
```go
if verifiedClaims.ExpiresAt.Time.Sub(now) > maxExpiryDuration {
    return nil, gethcommon.Address{}, fmt.Errorf("token lifetime from now exceeds maximum allowed %.0f sec", maxExpiryDuration.Seconds())
}
```
in addition to (or instead of) the existing `exp - iat` check, so that `issuedAtTolerance` cannot be combined with `maxExpiryDuration` to extend the effective validity window past the intended cap. Separately, verify that `JWTReplayPeriodMs` (default and any configured value) is always `>= issuedAtTolerance + maxExpiryDuration` so the replay-protection cache TTL cannot be shorter than the worst-case token validity window.

### Proof of Concept
Using `core/utils/jwt.go` defaults (`maxJWTExpiryDuration = 5m`, `defaultIssuedAtTolerance = 5m`):
1. Attacker/caller sets `iat = now + 4m59s` (just inside the 5-minute future-tolerance check at line 292).
2. Attacker/caller sets `exp = iat + 4m59s` (just inside the 5-minute `exp-iat` duration check at lines 295-298).
3. At verification time (`now`), `exp ≈ now + 9m58s`, so the token is valid for nearly 10 minutes from the verifier's true clock — double the documented/intended 5-minute maximum (`maxJWTExpiryDuration`), even though both individual checks in `VerifyRequestJWT` pass.

This is consistent with the existing test `TestVerifyRequestJWT_Integration/"should reject JWT with issuedAt in the future"` which shows tokens with `iat` up to the tolerance boundary are accepted [5](#0-4) , combined with the separate `exp-iat` cap test [6](#0-5)  — neither test exercises the combined/compounded scenario, confirming the gap is unmitigated.

### Citations

**File:** core/utils/jwt.go (L19-22)
```go
const (
	maxJWTExpiryDuration     = 5 * time.Minute // Maximum allowed expiry duration
	defaultIssuedAtTolerance = 5 * time.Minute // Default tolerance for issuedAt validation to handle clock drift
)
```

**File:** core/utils/jwt.go (L290-298)
```go
	now := time.Now()
	issuedAt := verifiedClaims.IssuedAt
	if issuedAt.After(now.Add(issuedAtTolerance)) {
		return nil, gethcommon.Address{}, fmt.Errorf("issuedAt (iat) is too far in the future (beyond tolerance of %.0f seconds)", issuedAtTolerance.Seconds())
	}
	duration := verifiedClaims.ExpiresAt.Sub(verifiedClaims.IssuedAt.Time)
	if duration > maxExpiryDuration {
		return nil, gethcommon.Address{}, fmt.Errorf("token lifetime %.0f sec exceeds the maximum allowed %.0f sec. Reduce the gap between 'iat' and 'exp'", duration.Seconds(), maxExpiryDuration.Seconds())
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L58-76)
```go
func NewWorkflowMetadataHandler(lggr logger.Logger, cfg ServiceConfig, shards []*shardEndpoint, nodeAddrToShard map[string]*shardEndpoint, metrics *metrics.Metrics) *WorkflowMetadataHandler {
	aggs := make(map[string]*aggregation.WorkflowMetadataAggregator, len(shards))
	for _, shard := range shards {
		threshold := shard.f + 1
		aggs[shard.donID] = aggregation.NewWorkflowMetadataAggregator(lggr, threshold, time.Duration(cfg.CleanUpPeriodMs)*time.Millisecond, metrics)
	}
	return &WorkflowMetadataHandler{
		lggr:            logger.Named(lggr, "HTTPTriggerWorkflowMetadataHandler"),
		authorizedKeys:  make(map[string]map[gateway.AuthorizedKey]struct{}),
		workflowRefToID: make(map[workflowReference]string),
		workflowIDToRef: make(map[string]workflowReference),
		workflowShards:  make(map[string][]*shardEndpoint),
		aggs:            aggs,
		shards:          shards,
		nodeAddrToShard: nodeAddrToShard,
		config:          cfg,
		stopCh:          make(services.StopChan),
		metrics:         metrics,
		jwtCache:        newJWTReplayCache(time.Duration(cfg.JWTReplayPeriodMs) * time.Millisecond),
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-90)
```go
func (h *WorkflowMetadataHandler) Authorize(workflowID string, token string, req *jsonrpc.Request[json.RawMessage]) (*gateway.AuthorizedKey, error) {
	claims, signer, err := utils.VerifyRequestJWT(token, *req)
	if err != nil {
		h.lggr.Errorw("Failed to verify JWT", "error", err)
		return nil, err
	}

	if h.jwtCache.isReplay(claims.ID) {
		h.lggr.Warnw("JWT token has already been used", "workflowID", workflowID, "signer", signer.Hex(), "jti", claims.ID)
		return nil, errors.New("JWT token has already been used. Please generate a new one with new id (jti)")
	}
```

**File:** core/utils/jwt_test.go (L335-365)
```go
	t.Run("should reject JWT with issuedAt in the future", func(t *testing.T) {
		digest, err := req.Digest()
		require.NoError(t, err)

		now := time.Now()
		// issuedAt is 7 mins in the future (beyond default 5-min tolerance)
		issuedAt := now.Add(7 * time.Minute)
		// expiresAt is 8 minute in the future (after issuedAt)
		expiresAt := now.Add(8 * time.Minute)

		claims := JWTClaims{
			Digest: "0x" + digest,
			RegisteredClaims: jwt.RegisteredClaims{
				ID:        "test-jti",
				ExpiresAt: jwt.NewNumericDate(expiresAt),
				IssuedAt:  jwt.NewNumericDate(issuedAt),
			},
		}

		token := jwt.NewWithClaims(&SigningMethodEth{}, claims)
		tokenString, err := token.SignedString(privateKey)
		require.NoError(t, err)

		_, _, err = VerifyRequestJWT(tokenString, req)
		require.Error(t, err)
		require.Contains(t, err.Error(), "issuedAt (iat) is too far in the future")

		// Should succeed with custom 10-minute tolerance
		_, _, err = VerifyRequestJWT(tokenString, req, WithIssuedAtTolerance(10*time.Minute))
		require.NoError(t, err)
	})
```

**File:** core/utils/jwt_test.go (L393-418)
```go
	t.Run("should validate that expiredAt exceeds max expiry", func(t *testing.T) {
		digest, err := req.Digest()
		require.NoError(t, err)

		now := time.Now()
		issuedAt := now
		expiresAt := now.Add(maxJWTExpiryDuration * 2)

		claims := JWTClaims{
			Digest: "0x" + digest,
			RegisteredClaims: jwt.RegisteredClaims{
				ID:        "test-jti",
				ExpiresAt: jwt.NewNumericDate(expiresAt),
				IssuedAt:  jwt.NewNumericDate(issuedAt),
			},
		}

		token := jwt.NewWithClaims(&SigningMethodEth{}, claims)
		tokenString, err := token.SignedString(privateKey)
		require.NoError(t, err)

		_, _, err = VerifyRequestJWT(tokenString, req)
		require.Error(t, err)
		require.Contains(t, err.Error(), "token lifetime")
		require.Contains(t, err.Error(), "exceeds the maximum allowed")
	})
```
