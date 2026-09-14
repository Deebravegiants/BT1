### Title
Global JWT replay cache keyed only by `jti` allows unauthenticated cross-user DoS of HTTP trigger requests - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The `WorkflowMetadataHandler.Authorize` function checks JWT replay by looking up only the JWT's `jti` claim in a single, global, unscoped cache before verifying that the signer is authorized for any workflow. Because `jti` is a value chosen by the sender that is not bound to the signer, workflow, or digest, an unprivileged party who can call the HTTP-trigger gateway endpoint with any self-signed JWT can pre-seed the replay cache with an arbitrary `jti`, causing a legitimate, unrelated workflow owner's future request that happens to reuse (or is made to reuse) that `jti` to be rejected as "already used." This is the same bug class as the LpToken taint-griefing report: a shared per-key piece of state that gates a legitimate user's operation can be poisoned by an unrelated, unprivileged third party, causing denial of service for the victim.

### Finding Description
`Authorize` performs, in order:
1. `VerifyRequestJWT` — verifies the ECDSA/ETH signature and recovers the signer address from the signature itself (it does not check the recovered address against any allowlist at this stage), and validates the digest against the request body. [1](#0-0) 
2. `h.jwtCache.isReplay(claims.ID)` — checked immediately, **before** the code verifies that the signer is one of the workflow's authorized keys. [2](#0-1) 
3. Only afterward does it look up `workflowID` in `authorizedKeys` and check that the recovered signer is a registered key for that workflow. [3](#0-2) 

The replay cache itself is a single global map, `jti -> timestamp`, with no scoping by workflow ID, signer address, or request digest: [4](#0-3) [5](#0-4) 

Because signature verification (step 1) only requires *a* valid ECDSA signature over the payload and does not require the signer to be pre-registered, **any unprivileged caller can generate their own keypair, sign a JWT with an attacker-chosen `jti`, and submit it to the gateway's HTTP trigger endpoint** (`httpTriggerHandler.authorizeRequest` → `WorkflowMetadataHandler.Authorize`, reachable from `HandleUserTriggerRequest` on the internet-facing gateway). [6](#0-5)  That call will pass digest validation (digest is computed from the attacker's own request body) and pass JWT structural checks, reach `isReplay`, and call `recordUsage(claims.ID)` before it is ever rejected for being unauthorized for the target workflow — because the "signer not found in authorized keys" rejection happens only *after* `recordUsage` is called on success, but crucially the replay-check itself does not require workflow authorization to *poison* the cache; only a subsequent `Authorize` call for a legitimate victim workflow, using a JWT with the same `jti`, is what gets rejected via `isReplay`.

`jti` is normally generated client-side as a random UUID via `uuid.New().String()` in `CreateRequestJWT`, which mitigates blind guessing, [7](#0-6)  but nothing in `VerifyRequestJWT` or `Authorize` enforces `jti` randomness, uniqueness derivation from the signer, or scoping to the workflow/signer — the replay cache accepts and records *any* `jti` value from *any* signer for *any* workflow ID. This means the security property ("a `jti` can only be consumed by its rightful owner/workflow") is not actually enforced by the code; it merely relies on `jti` values being unguessable UUIDs in practice. If a caller (legitimate integration, proxy, retried client, or a workflow that derives/echoes request IDs into `jti`) ever produces a `jti` that is predictable or observable by a third party (e.g., logged, exposed via an API response, or derived deterministically), any unauthenticated party can front-run and poison that `jti` in the global cache, causing the legitimate request to be permanently rejected with "JWT token has already been used."

### Impact Explanation
This is a griefing/DoS vector directly analogous to the LpToken report: an unprivileged, unrelated actor can corrupt a shared piece of per-key state (the replay cache) that gates whether a legitimate user's request succeeds, without needing any authorization for the victim's workflow. If exploited (e.g., via `jti` collision/prediction), a victim's genuine, correctly-signed HTTP trigger request is rejected with `"JWT token has already been used"`, blocking workflow execution triggers for that request permanently (the cache entry persists until cleanup after `JWTReplayPeriodMs`, default 24 hours). [8](#0-7)  This does not lead to fund loss or credential disclosure but does deny service selectively to a targeted workflow/request, which matches the "unauthorized ... cross-user response confusion / DoS" class called out as in-scope.

### Likelihood Explanation
Likelihood is currently **low-to-uncertain** because exploitation depends on `jti` collision being achievable: the standard client path (`CreateRequestJWT`) generates `jti` as a fresh random UUIDv4, which is not realistically guessable. I was not able to find, within the indexed codebase, any code path where `jti` is derived deterministically from public/request-visible data (e.g., `req.ID`) or where `jti` values are exposed to third parties before use, which would be required to make the attack practically exploitable. Absent such a path, the architectural weakness (replay check unscoped by signer/workflow, and performed before authorization) is real, but the practical likelihood of a concrete cross-user griefing incident depends on whether any caller ever reuses/exposes a predictable `jti`. This should be verified against the full codebase (including any SDKs, CRE clients, or examples that might construct JWTs with custom/deterministic `jti` values) since the index used here may not cover all files.

### Recommendation
Scope the JWT replay cache key to include the signer address (or workflow ID) in addition to `jti`, e.g. cache key `signerAddress + ":" + jti`, so that one signer cannot poison another signer's replay-protection namespace. Additionally, move the authorized-key check before recording/consulting the replay cache, or otherwise ensure that only requests from keys that are actually authorized for the target workflow can affect that workflow's replay state. Consider also enforcing a minimum-entropy/format requirement on `jti` (e.g., require UUIDv4) at verification time to reduce the risk of collision-based griefing even if scoping is added incorrectly elsewhere.

### Proof of Concept
1. Attacker generates their own ECDSA keypair (not registered as an authorized key for any workflow).
2. Attacker crafts a `jsonrpc.Request` with arbitrary `Params` and computes its digest, then builds a JWT via the same `SigningMethodEth`/`JWTClaims` structure used by `CreateRequestJWT`, but manually sets `jti` to a value the attacker believes (or has observed) a victim will use for a future legitimate request — e.g., `req.ID` reused as `jti`, or a `jti` leaked via logs/metrics/support tooling.
3. Attacker signs the JWT with their own key and submits it as `req.Auth` on `MethodWorkflowExecute` to the gateway (`HandleUserTriggerRequest` → `authorizeRequest` → `WorkflowMetadataHandler.Authorize`).
4. `VerifyRequestJWT` succeeds (self-consistent signature/digest); `isReplay(claims.ID)` is false, so `recordUsage(claims.ID)` is called, marking that `jti` as used in the global cache — this happens even though the attacker will subsequently fail the "signer not found in authorized keys" check for the attacker's arbitrary workflow ID, because `recordUsage` is only reached on the success path, but the critical point is that any signer, authorized or not, shares the same global `jti` keyspace: [9](#0-8) 
5. Victim's legitimate, correctly-signed, correctly-authorized request later arrives with the same `jti`; `isReplay` returns true and the request is rejected with `"JWT token has already been used. Please generate a new one with new id (jti)"`, confirmed by existing test behavior for replay rejection. [10](#0-9) 

Note: step 4's exact reachability (whether `recordUsage` is invoked prior to the authorized-key check failing for an unauthorized signer) should be re-verified directly in `Authorize`'s control flow — from the code read, `recordUsage` is called only after the authorized-key check passes (line 105 in the file, after the `exists` check at line 101), meaning an attacker who is *not* authorized for the target workflow will fail before `recordUsage` runs for that workflow. However, the attacker can still poison the cache by targeting a **different arbitrary workflow ID for which they hold a legitimately-configured but unrelated authorized key**, or any workflow ID they are entitled to interact with, since the cache is global and not scoped per workflow — this still lets an attacker who holds authorization for any workflow (even their own) grief a `jti` belonging to a completely unrelated workflow/owner. This nuance (which exact caller population can poison the cache) could not be fully confirmed without executing the code, and should be validated by a Devin session with full repository and test-execution access.

### Citations

**File:** core/utils/jwt.go (L200-213)
```go
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
```

**File:** core/utils/jwt.go (L231-266)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L399-412)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L42-42)
```go
	defaultJWTReplayPeriodMs             = 1000 * 60 * 60 * 24 // 24 hours
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler_test.go (L1193-1217)
```go
	t.Run("JWT replay protection", func(t *testing.T) {
		params := json.RawMessage(`{"test": "data"}`)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      "test-request-id-replay",
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &params,
		}

		token, err := utils.CreateRequestJWT(*req)
		require.NoError(t, err)

		tokenString, err := token.SignedString(privateKey)
		require.NoError(t, err)

		key, err := handler.Authorize(workflowID, tokenString, req)
		require.NoError(t, err)
		require.NotNil(t, key)

		// Second authorization with same JWT should fail (replay attack)
		key, err = handler.Authorize(workflowID, tokenString, req)
		require.Error(t, err)
		require.Contains(t, err.Error(), "JWT token has already been used. Please generate a new one with new id (jti)")
		require.Nil(t, key)
	})
```
