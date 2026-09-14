## Analysis Result

### Title
Unbounded JWT replay-cache growth in the HTTP-trigger gateway allows authorized-but-unprivileged workflow callers to exhaust gateway memory - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The reported Vert.x CVE-2024-1300 is a classic "attacker-controlled key drives unbounded cache growth" bug (SNI hostname → SSL context cache, no eviction until OOM). The same bug class exists in Chainlink's HTTP-trigger gateway handler: JWT `jti` values (fully client-chosen, e.g. a fresh UUID per request) are stored in an in-memory map that is only pruned by a periodic ticker running once per `JWTReplayPeriodMs` (default 24 hours), with no maximum size bound, unlike the sibling `requestCache` in the same codebase which does enforce `maxCacheSize`.

### Finding Description
`WorkflowMetadataHandler.Authorize` is invoked for every incoming user HTTP-trigger request via `httpTriggerHandler.authorizeRequest` [1](#0-0) , which is called from `HandleUserTriggerRequest` before the per-workflow rate limiter is checked [2](#0-1) .

Inside `Authorize`, the JWT is first cryptographically self-verified (the "signer" public key is recovered from the signature itself via `GetSignersEthAddress`, not looked up from a pre-registered allowlist at that stage) [3](#0-2) . The caller then only needs the recovered address to be present in `authorizedKeys[workflowID]` — i.e., any actor who legitimately holds a signing key authorized for at least one deployed workflow (a normal external workflow owner, not a node operator) [4](#0-3) .

Once authorized, the request's client-chosen `jti` is unconditionally recorded in `jwtCache.cache`: [5](#0-4) 

The cache is a plain `map[string]time.Time` with no size cap [6](#0-5) , and is pruned only by a ticker that fires once every `cleanupPeriod` (`JWTReplayPeriodMs`, default 24 hours) [7](#0-6) [8](#0-7) . Between cleanups, nothing bounds how many entries accumulate.

Because `jti` is a UUID chosen entirely by the caller and cheap to generate offline (only a local ECDSA signature is required per request, no expensive per-request work on the client side), an authorized-but-unprivileged workflow caller can send an unbounded stream of otherwise-valid, uniquely-`jti`'d trigger requests. Each one adds a permanent (until the next 24h cleanup) entry to `jwtCache.cache` on the gateway process, exactly mirroring the Vert.x SNI cache-growth pattern: a low-privilege, externally-reachable input value is used unconditionally as a cache key with no eviction policy other than a long-interval timer.

Notably, this differs from the peer `requestCache` implementation in the same package tree, which does enforce `maxCacheSize` [9](#0-8) , and from `RequestReplayGuard` in the vault package, which proactively evicts expired entries on every call [10](#0-9) . The JWT replay cache lacks both protections.

### Impact Explanation
An authenticated-but-unprivileged workflow client (holding only a signing key authorized for one of their own deployed workflows — not a node operator or gateway admin) can grow an unbounded in-process map on the gateway node by flooding it with uniquely-`jti`'d, otherwise valid, signed trigger requests. Since the cache lives in the gateway process shared by all workflows/DON members, sustained abuse can exhaust gateway memory, causing a process crash or OOM kill (CWE-400/CWE-772), denying service to all workflows served by that gateway — not just the abuser's own workflow.

### Likelihood Explanation
Exploitation requires only:
1. A signing key that is `authorized` for at least one existing workflow (a routine credential any legitimate workflow owner has, not an operator-only secret).
2. The ability to generate fresh JWTs locally (cheap ECDSA signing) and send them to the internet-facing gateway HTTP trigger endpoint.

No race condition, no node compromise, and no operator privileges are needed — only volume of legitimate-looking requests, which the per-workflow rate limiter (`checkRateLimit`) does not prevent because it is invoked strictly after the cache-writing `authorizeRequest` step [11](#0-10) .

### Recommendation
- Enforce a maximum size on `jwtReplayCache` (mirroring `requestCache.maxCacheSize`), rejecting/evicting when the bound is exceeded.
- Reduce the cleanup interval so it is decoupled from the full replay TTL, or evict opportunistically on each `recordUsage`/`isReplay` call (as `RequestReplayGuard` already does elsewhere in the codebase).
- Consider rate-limiting or throttling per-signer *before* `Authorize` writes to the JWT cache, not only after successful authorization.

### Proof of Concept
1. As a legitimate workflow owner, obtain a signing key authorized for workflow `W`.
2. Repeatedly craft valid JSON-RPC `workflows.execute` HTTP-trigger requests to the gateway, each with a fresh `jti` (UUID) and valid signature/digest, per `CreateRequestJWT`/`VerifyRequestJWT` [12](#0-11) .
3. Send these requests in a tight loop to the gateway's public trigger endpoint. Each authorized request adds one entry to `jwtCache.cache` [4](#0-3) .
4. Observe `jwtCache.cache` size grow unbounded (visible via `RecordJwtCacheSize` metric) until the next periodic cleanup (up to 24 hours later by default), demonstrating unbounded memory growth from an unprivileged, authorized-only actor.

**Uncertainty**: I could not verify from the index whether any additional global request-size/body limits or WAF-level protections exist in front of the gateway HTTP endpoint that might reduce practical exploitability (e.g., overall connection/request-rate throttling independent of the per-workflow limiter). If further verification of deployment-level mitigations is needed, a full Devin session with repository/runtime access would be required.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-376)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
}
```

**File:** core/utils/jwt.go (L168-216)
```go
func CreateRequestJWT[T any](req jsonrpc.Request[T], opts ...Option) (*jwt.Token, error) {
	// Apply options
	options := &jwtOptions{}
	for _, opt := range opts {
		opt(options)
	}

	expiryDuration := maxJWTExpiryDuration
	if options.expiryDuration != nil {
		expiryDuration = *options.expiryDuration
	}

	digest, err := req.Digest()
	if err != nil {
		return nil, err
	}

	var issuer string
	if options.issuer != nil {
		issuer = *options.issuer
	}

	var subject string
	if options.subject != nil {
		subject = *options.subject
	}

	var audience []string
	if options.audience != nil {
		audience = options.audience
	}

	now := time.Now()
	jti := uuid.New().String()

	claims := JWTClaims{
		Digest: "0x" + digest,
		RegisteredClaims: jwt.RegisteredClaims{
			ID:        jti,
			Issuer:    issuer,
			Subject:   subject,
			Audience:  jwt.ClaimStrings(audience),
			ExpiresAt: jwt.NewNumericDate(now.Add(expiryDuration)),
			IssuedAt:  jwt.NewNumericDate(now),
		},
	}

	return jwt.NewWithClaims(&SigningMethodEth{}, claims), nil
}
```

**File:** core/utils/jwt.go (L228-266)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L29-34)
```go
// jwtReplayCache manages used JWT IDs to prevent replay attacks
type jwtReplayCache struct {
	mu            sync.RWMutex
	cleanupPeriod time.Duration
	cache         map[string]time.Time // jti -> timestamp
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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L298-304)
```go
		h.runTicker(h.jwtCache.cleanupPeriod, func(ctx context.Context) {
			now := time.Now()
			expiredCount := h.jwtCache.cleanupOldEntries(now.Add(-h.jwtCache.cleanupPeriod))
			h.metrics.IncrementJwtCacheCleanUpCount(ctx, int64(expiredCount), h.lggr)
			h.metrics.RecordJwtCacheSize(ctx, int64(len(h.jwtCache.cache)), h.lggr)
			h.lggr.Debugw("Workflow execution cache cleanup completed", "expired_entries", expiredCount, "remaining_entries", len(h.jwtCache.cache))
		})
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L407-412)
```go
func (cache *jwtReplayCache) recordUsage(jti string) {
	cache.mu.Lock()
	defer cache.mu.Unlock()

	cache.cache[jti] = time.Now()
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L41-43)
```go
	defaultOutboundRequestCacheTTLMs     = 1000 * 60 * 10      // 10 minutes
	defaultJWTReplayPeriodMs             = 1000 * 60 * 60 * 24 // 24 hours
	defaultSendResponseTimeoutMs         = 1000 * 5            // 5 seconds
```

**File:** core/services/gateway/handlers/common/requestcache.go (L27-33)
```go
type requestCache[T any] struct {
	cache        map[globalID]*pendingRequest[T]
	maxCacheSize uint32
	timeout      time.Duration
	mu           sync.Mutex
}

```

**File:** core/capabilities/vault/request_replay_guard.go (L35-47)
```go
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
}
```
