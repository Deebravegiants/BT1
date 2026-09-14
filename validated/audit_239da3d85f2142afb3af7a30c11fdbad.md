### Title
Unprivileged replay-guard front-running causes permanent DOS of legitimate vault requests - (File: core/capabilities/vault/authorizer.go, core/capabilities/vault/request_replay_guard.go, core/capabilities/vault/allow_list_based_auth.go)

### Summary
The `repay()` front-running bug class (an attacker observing a pending, deterministic transaction and submitting a cheaper variant first so the victim's later call reverts) has a structural analog in the Vault gateway request pipeline. `AllowListBasedAuth.AuthorizeRequest` authorizes a request purely by recomputing a content digest of the request and matching it against an on-chain allowlist entry, with no signature binding the caller's identity to the submission. That digest is then consumed exactly once by a shared `RequestReplayGuard`.

### Finding Description
`allowListBasedAuth.AuthorizeRequest` computes `requestDigest` from the request's own content (`req.Digest()`) and checks it against allowlisted entries fetched from the workflow registry syncer [1](#0-0) . This is content-based authorization, not signer-based: whoever submits the exact byte-identical request first is treated as authorized, since a legitimate node/user client is expected to be the first submitter of a deterministic request derived from public on-chain allowlist parameters.

After either allowlist- or JWT-based authorization succeeds, `authorizer.AuthorizeRequest` unconditionally applies `a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt())` [2](#0-1) . `RequestReplayGuard.CheckAndRecord` is a simple "first writer wins" map keyed by digest: the first caller to record a digest succeeds, and every subsequent call with the same digest (until expiry) is rejected with `ErrRequestAlreadySeen`, regardless of who submitted it [3](#0-2) .

The gateway's public entry point `HandleJSONRPCUserMessage` accepts any unauthenticated user's JSON-RPC message and immediately funnels it into `h.requestProcessor.ProcessRequest`, which is `GatewayVaultRequestProcessor.ProcessRequest → authorizeAndStamp → authorizer.AuthorizeRequest` [4](#0-3) . Since allowlisted request parameters (owner, method, namespace, expiry) are registered on-chain in the workflow registry and are therefore public/derivable, an attacker can reconstruct the exact byte-identical JSON-RPC request that a legitimate owner/workflow is expected to submit and race it to the gateway before the legitimate client. This is directly analogous to the `repay()` finding: a deterministic, publicly-computable state-changing call that succeeds once and then permanently blocks the "real" caller's subsequent identical call, because the guard condition is checked against shared, externally-influenceable state rather than being scoped per-caller.

The code's own comment even flags this as a known ordering hazard between authorization and other checks: "Owner-scoped limit checks are deferred until after authorization... checking them pre-auth would let unauthenticated callers create unbounded limiter tenants," and a system test explicitly documents the replay guard rejecting legitimate retried requests: `sendConcurrentVaultCreate` treats "request was already authorized previously" as an accepted/expected outcome of concurrent submission [5](#0-4) , confirming the replay guard's race-sensitive, single-use-by-anyone semantics are a recognized operational reality, not a hypothetical.

### Impact Explanation
An unprivileged attacker who can compute or observe the exact upcoming allowlisted vault request (owner + method + namespace + request content are derived from on-chain, public workflow-registry data) can pre-submit that exact request to the gateway's public HTTP/JSON-RPC endpoint. Because the replay guard is keyed only by content digest and not by caller identity, the attacker's submission consumes the one-time allowlist slot. When the legitimate owner's client later submits the same (or a byte-identical retried) request, it is rejected with `ErrRequestAlreadySeen`, denying the real owner service for the allowlisted request's validity window. This is a targeted, low-cost, unprivileged denial-of-service against a specific owner's vault operation (secrets create/update/delete/list), matching the "Medium" impact classification of the referenced `repay()` DOS finding (griefing/DOS of a specific user's state-changing operation, not fund loss).

### Likelihood Explanation
Likelihood depends on the attacker being able to predict/observe the exact request content and expiry before the legitimate submission (analogous to mempool front-running in the original report). Since allowlist entries and their `RequestDigest`/`Owner`/`ExpiryTimestamp` are read from the on-chain workflow registry via `GetAllowlistedRequests` [6](#0-5) , and workflow registry state is public, an attacker monitoring the registry can, for many workflows, derive or brute-force the exact request needed to match a given digest depending on how much of the plaintext request is predictable/public. The exact difficulty of forging a byte-identical request (vs. only its digest) could not be fully verified from the available index (e.g., how much of `req.Params` is secret/opaque) — this affects real-world exploitability but does not change the underlying design flaw that authorization + replay protection here are content-based and caller-agnostic rather than caller-bound.

### Recommendation
- Bind allowlist/replay-guard authorization to a cryptographic proof of caller identity (e.g., signature over the request by the allowlisted owner) rather than only a content digest, so that request content alone cannot be "consumed" by a third party.
- Scope the replay guard per authorized owner/session rather than as a single global digest map, so an attacker cannot squat another owner's allowlisted digest.
- Consider allowing legitimate retries by the same authenticated owner even if the digest was previously seen (idempotent replay by the verified owner), rather than a strict single-use lock triggered by first-arrival.

### Proof of Concept
1. Owner O registers/derives an allowlisted vault request (method=`vault.secrets.create`, params P, ExpiryTimestamp T) on-chain via the workflow registry; this becomes visible to all observers through `WorkflowRegistrySyncer.GetAllowlistedRequests`.
2. Attacker computes/derives the exact request payload P and its digest `req.Digest()` matching the on-chain allowlisted entry (feasible when P's fields are public/derivable from registry state and workflow parameters).
3. Attacker submits this exact JSON-RPC request to the gateway's public endpoint before O's client does. `allowListBasedAuth.AuthorizeRequest` succeeds (digest matches, not expired) [7](#0-6) , and `replayGuard.CheckAndRecord` records the digest as seen [8](#0-7) .
4. Owner O's legitimate client later submits the identical request; `AuthorizeRequest` again succeeds against the allowlist, but `replayGuard.CheckAndRecord` now returns `ErrRequestAlreadySeen`, and `authorizer.AuthorizeRequest` propagates this as a failure [9](#0-8) , causing the gateway to respond "request not authorized" to O [10](#0-9) .

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L34-46)
```go
func (r *allowListBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	r.lggr.Debugw("AllowListBasedAuth authorizing request", "method", req.Method, "requestID", req.ID)
	requestDigest, err := req.Digest()
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to create digest", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to decode digest", "method", req.Method, "requestID", req.ID, "requestDigest", requestDigest, "error", err)
		return nil, err
	}
	requestDigestBytes32 := [32]byte(requestDigestBytes)
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L55-68)
```go
	if allowlistedRequest == nil {
		r.lggr.Debugw("AllowListBasedAuth request digest not allowlisted",
			"method", req.Method,
			"requestID", req.ID,
			"digestHexStr", requestDigest,
			"allowedRequestsStrs", allowedRequestsStrs)
		return nil, errors.New("request not allowlisted")
	}

	if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
		authorizedRequestStr := string(allowlistedRequest.RequestDigest[:])
		r.lggr.Debugw("AllowListBasedAuth authorization expired", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", authorizedRequestStr, "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
		return nil, errors.New("request authorization expired")
	}
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L79-92)
```go
func (r *allowListBasedAuth) findAllowlistedItemWithRetry(ctx context.Context, req jsonrpc.Request[json.RawMessage], requestDigest string, requestDigestBytes32 [32]byte) (*workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest, []string, error) {
	for attempt := 0; attempt <= r.retryCount; attempt++ {
		allowedRequests := r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)
		allowedRequestsStrs := make([]string, 0, len(allowedRequests))
		for _, rr := range allowedRequests {
			allowedReqStr := fmt.Sprintf("AuthorizedOwner: %s, RequestDigest: %s, ExpiryTimestamp: %d", rr.Owner.Hex(), hex.EncodeToString(rr.RequestDigest[:]), rr.ExpiryTimestamp)
			allowedRequestsStrs = append(allowedRequestsStrs, allowedReqStr)
		}
		r.lggr.Debugw("AllowListBasedAuth loaded allowlisted requests", "method", req.Method, "requestID", req.ID, "attempt", attempt+1, "allowedRequests", allowedRequestsStrs)

		allowlistedRequest := r.fetchAllowlistedItem(allowedRequests, requestDigestBytes32)
		if allowlistedRequest != nil {
			return allowlistedRequest, allowedRequestsStrs, nil
		}
```

**File:** core/capabilities/vault/authorizer.go (L99-112)
```go
func (a *authorizer) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	authResult, err := a.authorizeRequest(ctx, req)
	if err != nil {
		return nil, err
	}
	if authResult == nil {
		err = errors.New("auth mechanism returned nil auth result")
		a.lggr.Errorw("auth mechanism returned nil auth result", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "")
		return nil, err
	}
	if err := a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt()); err != nil {
		a.lggr.Debugw("replay guard rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "", "error", err)
		return nil, err
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

**File:** core/services/gateway/handlers/vault/handler.go (L394-434)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
		if cachedPublicKey == nil {
			// Not found in cache. Fetch from nodes.
			ar, err := h.newActiveRequest(req, callback)
			if err != nil {
				h.lggr.Errorw("failed to create new activeRequest", "error", err)
				return err
			}
			return h.handlePublicKeyGet(ctx, ar)
		}
		h.lggr.Debugw("returning cached public key response")
		return h.handlePublicKeyGetSynchronously(ctx, req, publicKeyResponseBytes, callback)
	}

	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
```

**File:** system-tests/tests/smoke/cre/vault_don_test.go (L638-669)
```go
// sendConcurrentVaultCreate sends an already-allowlisted create request to the gateway and tolerates
// the replay-guard outcome. Under burst load, the gateway can time out (503 "Request timed out") while
// DON still processes the create; the test's HTTP retry then re-sends the same request digest, which
// vault's replay guard rejects with "request was already authorized previously". That error proves the
// original request was accepted and processed, so we treat it as success — there is no later response
// payload to validate when this path fires.
func sendConcurrentVaultCreate(t *testing.T, gwURL, requestID string, jsonRequest jsonrpc.Request[json.RawMessage], authorizedOwner, expectedResponseOwner string, namespaces []string) {
	t.Helper()

	authToken := jsonRequest.Auth
	stripped := outboundRequestWithoutAuth(jsonRequest)
	requestBody, err := json.Marshal(stripped)
	require.NoError(t, err, "failed to marshal vault request")
	headers := map[string]string{}
	if authToken != "" {
		headers["Authorization"] = "Bearer " + authToken
	}

	statusCode, body := sendVaultRequestToGatewayWithHeaders(t, gwURL, requestBody, headers)

	// Under burst load the gateway can return 503 "Request timed out" when it gives up relaying the
	// response, even though the DON has already processed the request. Tolerate that here — the goal
	// of this subtest is to drive concurrent load for the docker-log batching assertions below, not
	// to verify per-request response payloads.
	if statusCode == http.StatusServiceUnavailable && bytes.Contains(body, []byte("Request timed out")) {
		framework.L.Info().Str("requestID", requestID).Msg("vault create gateway-to-DON timeout; treating as success for batching load test")
		return
	}
	// Replay guard can arrive on a non-200 HTTP status after a retried gateway call; check before StatusOK.
	if bytes.Contains(body, []byte("request was already authorized previously")) {
		framework.L.Info().Str("requestID", requestID).Msg("vault create returned replay-guard error after retry; DON processed the original request — treating as success")
		return
```
