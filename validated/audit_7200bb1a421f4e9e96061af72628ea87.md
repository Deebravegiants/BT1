### Title
JWT replay-protection cache in the HTTP Trigger gateway is in-memory only and reset on process restart, permitting reuse of previously-consumed, still-valid JWTs - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The `WorkflowMetadataHandler.Authorize` method deduplicates JWT `jti` values using an in-memory `jwtReplayCache` to prevent replay of workflow-trigger request tokens. This cache is never persisted; on any gateway process restart the map starts empty, so a previously used but not-yet-expired JWT (tokens may live up to 5 minutes per `maxJWTExpiryDuration`) can be replayed exactly once per restart. This is the same bug class as the dfinity ledger report: authoritative state needed to prevent double-use/double-spend is held only in volatile memory and is not restored/reconciled across a service restart/upgrade, so state that should persist a security invariant is silently "forgotten."

### Finding Description
`Authorize` verifies a signed request JWT and then checks/records its `jti` solely in the process-local `jwtReplayCache`: [1](#0-0) 

The cache itself is a plain in-memory map with no backing store: [2](#0-1) [3](#0-2) 

`NewWorkflowMetadataHandler` constructs a brand-new, empty `jwtReplayCache` every time the handler/process is created, with no load-from-disk/DB step: [4](#0-3) 

Tokens are valid for up to `maxJWTExpiryDuration` (5 minutes), and validity is enforced purely by the JWT's own `exp`/`iat` claims plus signature — nothing in `VerifyRequestJWT` ties a token to a single-use guarantee; that guarantee is provided *only* by the external `jwtReplayCache`: [5](#0-4) [6](#0-5) 

Because the replay-protection state is not durable, any restart of the gateway process (crash, redeploy, rolling upgrade, OOM-kill, host reboot) wipes `jwtReplayCache.cache` while previously-issued, already-used, but still-unexpired JWTs remain cryptographically valid. This exactly mirrors the reported bug class: authoritative anti-double-use state (ledger balances / used-jti set) is derived from durable inputs (blocks / JWTs) but the derived state itself is kept only in memory and is not reconstructed or persisted across a restart/upgrade, silently reintroducing a previously prevented condition (double-spend / token replay).

### Impact Explanation
The `jwtReplayCache` is the sole mechanism preventing replay of `MethodWorkflowExecute`/HTTP-trigger requests reachable from unprivileged, internet-facing callers through the gateway's `Authorize` path. An unprivileged client that has legitimately (or by interception) obtained one used JWT can resubmit the identical signed request once after any gateway restart and have it accepted as if it were fresh, because `isReplay` will return `false` against the freshly-initialized empty map. This allows unauthorized re-execution of a workflow trigger request that the system was specifically designed to accept only once, i.e., request impersonation/replay bypass at the internet-facing gateway.

### Likelihood Explanation
Likelihood is moderate: exploitation requires (a) possession of a previously-used, not-yet-expired JWT (tokens live up to 5 minutes) and (b) a gateway restart occurring within that window. Gateway restarts happen routinely in production (rolling deploys, autoscaling, crash/OOM recovery, host maintenance) and are not attacker-controlled but are a normal, expected operational event, not an "operator-only" precondition requiring privileged access — the attacker only needs to have captured a valid JWT and wait for/observe a restart to fire the replay within the token's remaining lifetime.

### Recommendation
Persist the used-`jti` set (or at least records within the maximum token lifetime window) to a durable store (database/shared cache such as Redis) keyed with expiry, so that replay protection survives process restarts, mirroring the ledger fix of serializing balances alongside blocks. If multi-instance/HA gateway deployments exist, the store should also be shared across instances to prevent replay by routing a request to a peer instance rather than a restarted one.

### Proof of Concept
1. Client submits a valid `MethodWorkflowExecute` request signed with a JWT (`jti = X`, `exp` = now+5m) to the gateway; `Authorize` calls `VerifyRequestJWT`, passes, then `h.jwtCache.recordUsage("X")` (line 105) marks it used.
2. Gateway process restarts (deploy/crash/OOM) before the JWT's `exp` elapses. `NewWorkflowMetadataHandler` recreates `jwtCache` as an empty map (line 76), with no reload of previously recorded `jti`s.
3. Attacker (who has recorded/observed the same JWT from step 1) resubmits the identical request/JWT.
4. `VerifyRequestJWT` succeeds (signature/claims unchanged and still within `exp`); `h.jwtCache.isReplay("X")` now returns `false` because the cache is empty post-restart, so the check at line 87-90 does not trigger, and the request is authorized a second time — a successful replay of a token that was supposed to be single-use.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L29-34)
```go
// jwtReplayCache manages used JWT IDs to prevent replay attacks
type jwtReplayCache struct {
	mu            sync.RWMutex
	cleanupPeriod time.Duration
	cache         map[string]time.Time // jti -> timestamp
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L58-78)
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
	}
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-108)
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

	keys, exists := h.authorizedKeys[workflowID]
	if !exists {
		h.lggr.Errorw("Workflow ID not found in authorized keys", "workflowID", workflowID)
		return nil, fmt.Errorf("workflow ID %s not found", workflowID)
	}
	key := gateway.AuthorizedKey{
		KeyType:   gateway.KeyTypeECDSAEVM,
		PublicKey: strings.ToLower(signer.Hex()),
	}
	if _, exists = keys[key]; !exists {
		h.lggr.Errorw("Signer not found in authorized keys", "signer", signer.Hex())
		return nil, fmt.Errorf("signer '%s' is not authorized for workflow '%s'. Ensure that the signer is registered in the workflow definition", signer.Hex(), workflowID)
	}
	h.jwtCache.recordUsage(claims.ID)

	return &key, nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L392-412)
```go
func newJWTReplayCache(cleanupPeriod time.Duration) *jwtReplayCache {
	return &jwtReplayCache{
		cache:         make(map[string]time.Time),
		cleanupPeriod: cleanupPeriod,
	}
}

func (cache *jwtReplayCache) isReplay(jti string) bool {
	cache.mu.RLock()
	defer cache.mu.RUnlock()

	_, exists := cache.cache[jti]
	return exists
}

func (cache *jwtReplayCache) recordUsage(jti string) {
	cache.mu.Lock()
	defer cache.mu.Unlock()

	cache.cache[jti] = time.Now()
}
```

**File:** core/utils/jwt.go (L19-22)
```go
const (
	maxJWTExpiryDuration     = 5 * time.Minute // Maximum allowed expiry duration
	defaultIssuedAtTolerance = 5 * time.Minute // Default tolerance for issuedAt validation to handle clock drift
)
```

**File:** core/utils/jwt.go (L228-303)
```go
// VerifyRequestJWT verifies a signed JWT for a JSON-RPC request
// It recovers and returns the public key used to sign the JWT, checks the issuer, validates the digest,
// and performs all validations done by jwt.ParseWithClaims() including expiration checks.
func VerifyRequestJWT[T any](tokenString string, req jsonrpc.Request[T], opts ...VerifyOption) (*JWTClaims, gethcommon.Address, error) {
	options := &verifyOptions{}
	for _, opt := range opts {
		opt(options)
	}

	maxExpiryDuration := maxJWTExpiryDuration
	if options.maxExpiryDuration != nil {
		maxExpiryDuration = *options.maxExpiryDuration
	}

	issuedAtTolerance := defaultIssuedAtTolerance
	if options.issuedAtTolerance != nil {
		issuedAtTolerance = *options.issuedAtTolerance
	}
	signedString, signature, err := splitToken(tokenString)
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	decodedSignature, err := base64.RawURLEncoding.DecodeString(signature)
	if err != nil {
		return nil, gethcommon.Address{}, fmt.Errorf("signature segment is not valid base64url: %w", err)
	}
	pubKey, err := GetSignersEthAddress([]byte(signedString), decodedSignature)
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	verifiedToken, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (any, error) {
		if token.Method.Alg() != EthereumSigningMethod.Alg() {
			return nil, fmt.Errorf("unsupported JWT 'alg': '%s'. Expected '%s'", token.Method.Alg(), EthereumSigningMethod.Alg())
		}
		if _, ok := token.Method.(*SigningMethodEth); !ok {
			return nil, jwt.ErrSignatureInvalid
		}
		return pubKey, nil
	})
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	verifiedClaims, ok := verifiedToken.Claims.(*JWTClaims)
	if !ok {
		return nil, gethcommon.Address{}, errors.New("claims payload is not in the expected format")
	}
	if !verifiedToken.Valid {
		return nil, gethcommon.Address{}, errors.New("signature or claims validation failed")
	}
	reqDigest, err := req.Digest()
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	if verifiedClaims.ID == "" {
		return nil, gethcommon.Address{}, errors.New("JWT ID (jti) is required but missing")
	}
	if verifiedClaims.ExpiresAt == nil {
		return nil, gethcommon.Address{}, errors.New("expiredAt (exp) is required but missing")
	}
	if verifiedClaims.IssuedAt == nil {
		return nil, gethcommon.Address{}, errors.New("issuedAt (iat) is required but missing")
	}
	now := time.Now()
	issuedAt := verifiedClaims.IssuedAt
	if issuedAt.After(now.Add(issuedAtTolerance)) {
		return nil, gethcommon.Address{}, fmt.Errorf("issuedAt (iat) is too far in the future (beyond tolerance of %.0f seconds)", issuedAtTolerance.Seconds())
	}
	duration := verifiedClaims.ExpiresAt.Sub(verifiedClaims.IssuedAt.Time)
	if duration > maxExpiryDuration {
		return nil, gethcommon.Address{}, fmt.Errorf("token lifetime %.0f sec exceeds the maximum allowed %.0f sec. Reduce the gap between 'iat' and 'exp'", duration.Seconds(), maxExpiryDuration.Seconds())
	}
	if verifiedClaims.Digest != "0x"+reqDigest {
		return nil, gethcommon.Address{}, fmt.Errorf("claim digest '%s' does not match calculated request digest '0x%s'", verifiedClaims.Digest, reqDigest)
	}

	return verifiedClaims, pubKey, nil
```
