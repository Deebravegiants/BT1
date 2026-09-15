### Title
DOS via replay-guard front-running lets an unprivileged client permanently block a legitimate Vault owner's allowlisted request - (File: core/capabilities/vault/request_replay_guard.go)

### Summary
The reported bug class is a strict-equality/exact-match check on externally influenceable state (`_reserve0 == _reserve1`) that an unprivileged actor can front-run to permanently deny a legitimate privileged call. The chainlink Vault authorization pipeline has the same shape: authorization for a gateway-routed Vault request is granted purely by an exact digest match against an on-chain allowlist entry, and a single global `RequestReplayGuard` accepts the *first* caller who presents that exact digest, permanently rejecting every subsequent (including the legitimate) caller with the same digest until expiry.

### Finding Description
`allowListBasedAuth.AuthorizeRequest` computes `req.Digest()` (a hash over the JSON-RPC method/id/params) and looks it up against on-chain allowlisted digests published by `WorkflowRegistry.AllowlistRequest` [1](#0-0) . Ownership of the digest is proven only by *knowing the exact preimage bytes*, not by any signature over the caller — anyone who can reconstruct the exact `{method, id, params}` that hashes to an allowlisted digest is authorized as that digest's owner.

Once authorized, `authorizer.AuthorizeRequest` immediately calls the shared, single, in-memory `RequestReplayGuard.CheckAndRecord(digest, expiresAt)`, which accepts the digest exactly once and rejects every following attempt with `ErrRequestAlreadySeen` ("request was already authorized previously") until the entry expires [2](#0-1) [3](#0-2) . This is a strict, first-come-first-served exact-match gate — structurally identical to the reported `_reserve0 == _reserve1` check: whoever satisfies the exact condition first "wins," and the legitimate actor who arrives second is permanently locked out for the entry's lifetime.

`GatewayVaultRequestProcessor` documents that "AuthorizeRequest ... also applies the replay guard (digest deduplication)" as an unconditional step in the pipeline before any request-specific processing [4](#0-3) , and `authorizeAndStamp` treats any authorizer error, including the replay-guard rejection, as an unrecoverable `"request not authorized"` failure for that call [5](#0-4) .

The gateway's public entrypoint (`gateway.ProcessRequest`) accepts JSON-RPC requests from any unprivileged HTTP client and routes them by method/DON to the handler without any per-caller authentication ahead of the Vault-specific authorization step [6](#0-5) ; the vault gateway handler on the node side likewise treats `MethodSecretsDelete`/`MethodSecretsList` calls generically through the shared processor before dispatching to the secrets service [7](#0-6) .

For `vault.secrets.list` / `vault.secrets.delete` requests using the non-JWT (allowlist) path, the digest is computed over publicly-guessable content: the request `id`, `owner` (public on-chain address once the client's `AllowlistRequest` tx lands), and `namespace` (commonly a fixed/default value such as `"main"`/`"default"` as seen throughout the codebase's own tests) [8](#0-7) . An attacker monitoring `WorkflowRegistry.AllowlistRequest` events on-chain learns the exact digest the legitimate owner is about to submit, and — if the accompanying id/namespace/owner combination is predictable or reused (e.g., a fixed request ID or default namespace) — can reconstruct the exact preimage and submit it to the public gateway HTTP endpoint before the legitimate client does.

### Impact Explanation
If the attacker wins the race, `RequestReplayGuard.CheckAndRecord` records the digest as "seen." The legitimate owner's subsequent (identical) request is then rejected with `ErrRequestAlreadySeen`/"request was already authorized previously" for the remainder of the allowlisted digest's expiry window [9](#0-8) . This is a genuine, unprivileged-actor-triggerable denial of service on the Vault capability: the owner cannot list or delete their own secrets using that pre-committed on-chain authorization until it expires and they re-allowlist a new digest (incurring an additional on-chain transaction and delay). The codebase's own system tests explicitly acknowledge and special-case the replay-guard collision ("Replay guard can arrive on a non-200 HTTP status after a retried gateway call...") [10](#0-9) , confirming the replay guard is reachable and race-sensitive via the public gateway, though those tests treat it as a benign retry collision from the *same* client rather than a hostile third party.

### Likelihood Explanation
Exploitability is bounded by how guessable the full request preimage (`id`, `namespace`, `owner`) is for a given deployment/workflow. In the worst case (fixed/default namespace, deterministic or short request IDs, and a publicly known owner from the on-chain allowlist event) the attack is straightforward and cheap — it only requires racing a single HTTP POST to the gateway ahead of the legitimate client, with no privileged keys or credentials needed. In the best case (long random UUID request IDs) it becomes a brute-force race that is much harder but not proven infeasible given the small window between the on-chain `AllowlistRequest` transaction and the gateway call. I could not verify from the available code whether callers are required or encouraged to use unpredictable request IDs, so likelihood is assessed as **Medium** with the caveat that concrete exploitability depends on caller-controlled entropy that this review could not fully audit.

### Recommendation
- Bind replay-guard acceptance to the authenticated caller as well as the digest (e.g., require the JWT/allowlist owner to match the *sender* rather than accepting any submitter of the correct bytes), or
- Scope the `RequestReplayGuard` per-owner instead of globally, so an unrelated caller cannot consume another owner's digest slot, and
- Consider requiring high-entropy, caller-committed request IDs (or a client-bound nonce/signature over the exact wire bytes) as part of the digest so that an on-chain-visible allowlist entry alone is insufficient to reconstruct a submittable request.

### Proof of Concept
Conceptual sequence (based on code inspection; not independently executed):
1. Legitimate owner submits `WorkflowRegistry.AllowlistRequest(digest, expiry)` on-chain for a `vault.secrets.list` request with `namespace="main"`, a fixed/known `id`, and their own `owner` address.
2. Attacker observes the `AllowlistRequest` transaction/event (public), and — knowing/guessing the exact `id`/`namespace` used by the client's tooling — reconstructs the identical JSON-RPC request bytes and POSTs it to the public gateway endpoint before the legitimate client does [11](#0-10) .
3. `allowListBasedAuth.AuthorizeRequest` finds the matching allowlisted digest and returns a valid `AuthResult` for the attacker's request [12](#0-11) .
4. `authorizer.AuthorizeRequest` calls `replayGuard.CheckAndRecord(digest, expiresAt)`, which succeeds for the attacker's (first) request and records the digest [13](#0-12) .
5. The legitimate owner's subsequent identical request now fails authorization with `ErrRequestAlreadySeen` ("request was already authorized previously") until the allowlist entry expires, exactly mirroring the existing test assertion for this error path [14](#0-13) .

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L34-76)
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
	if r.workflowRegistrySyncer == nil {
		r.lggr.Errorw("AllowListBasedAuth workflowRegistrySyncer is nil", "method", req.Method, "requestID", req.ID)
		return nil, errors.New("internal error: workflowRegistrySyncer is nil")
	}
	allowlistedRequest, allowedRequestsStrs, err := r.findAllowlistedItemWithRetry(ctx, req, requestDigest, requestDigestBytes32)
	if err != nil {
		return nil, err
	}
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

	digestKey := string(allowlistedRequest.RequestDigest[:])
	r.lggr.Debugw("AllowListBasedAuth authorization succeeded", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", digestKey, "owner", allowlistedRequest.Owner.Hex(), "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
	return &AuthResult{
		workflowOwner: allowlistedRequest.Owner.Hex(),
		digest:        digestKey,
		expiresAt:     int64(allowlistedRequest.ExpiryTimestamp),
	}, nil
```

**File:** core/capabilities/vault/authorizer.go (L99-119)
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
	if ownerErr := validateSecretOwnersMatchAuthorized(req, authResult.AuthorizedOwner()); ownerErr != nil {
		a.lggr.Errorw("owner binding rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "hasAuth", req.Auth != "", "error", ownerErr)
		return nil, ownerErr
	}
	a.lggr.Debugw("request authorized", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "")
	return authResult, nil
}
```

**File:** core/capabilities/vault/request_replay_guard.go (L9-9)
```go
var ErrRequestAlreadySeen = errors.New("request was already authorized previously")
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L20-34)
```go
// GatewayVaultRequestProcessor orchestrates the shared gateway-routed vault JSON-RPC pipeline
// used by the gateway public handler and the node-side gateway connector handler.
//
// Pipeline invariant:
//
//	ValidateStructureBeforeAuth → AuthorizeRequest → Prefix ID → StampAuthorizedParams → ValidateOwnerScopedLimits
//	    (no param mutation)        (on raw bytes)               (namespace + request_id)      (ciphertext size)
//
// AuthorizeRequest runs while params are still digest-safe. It also applies the replay guard
// (digest deduplication) and validates that payload owners match the authorized workflow owner
// before this processor rewrites the request ID or stamps params.
//
// Owner-scoped limit checks are deferred until after authorization: each new owner tenant
// registered by a scoped limiter spawns a persistent background updater, so checking them
// pre-auth would let unauthenticated callers create unbounded limiter tenants.
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-276)
```go
func (p *GatewayVaultRequestProcessor) authorizeAndStamp(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	stamp func(prefixedRequestID string) error,
) (*AuthorizedGatewayVaultRequest, error) {
	incomingOwner := ""
	if idx := strings.Index(req.ID, vaulttypes.RequestIDSeparator); idx != -1 {
		incomingOwner = req.ID[:idx]
	}

	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}
```

**File:** core/services/gateway/gateway.go (L220-265)
```go
// Called by the server
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
	} else {
		// Legacy request with DON ID - validate and fetch handler
		isLegacyRequest = true
		if err = msg.Validate(); err != nil {
			return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
		}
		handlerKey = msg.Body.DonID
		var ok bool
		h, ok = g.handlers[handlerKey]
		if !ok {
			return newError(jsonRequest.ID, api.UnsupportedDONIdError, "Unsupported DON ID: "+handlerKey)
		}
	}
```

**File:** core/capabilities/vault/gw_handler.go (L180-223)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

	var response *jsonrpc.Response[json.RawMessage]
	var authResult *AuthResult

	switch req.Method {
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}

	if response == nil {
		switch req.Method {
		case vaulttypes.MethodSecretsCreate:
			response = h.handleSecretsCreate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsUpdate:
			response = h.handleSecretsUpdate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsDelete:
			response = h.handleSecretsDelete(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsList:
			response = h.handleSecretsList(ctx, gatewayID, req, authResult)
		}
```

**File:** core/capabilities/vault/allow_list_based_auth_test.go (L134-154)
```go
func TestAllowListBasedAuth_ListSecrets(t *testing.T) {
	params, err := json.Marshal(vaultcommon.ListSecretIdentifiersRequest{
		Namespace: "b",
	})
	allowListedReq := jsonrpc.Request[json.RawMessage]{
		ID:     "123",
		Method: vaulttypes.MethodSecretsList,
		Params: (*json.RawMessage)(&params),
	}
	require.NoError(t, err)
	notAllowedParams, err := json.Marshal(vaultcommon.ListSecretIdentifiersRequest{
		Namespace: "not allowed",
	})
	require.NoError(t, err)
	notAllowListedReq := jsonrpc.Request[json.RawMessage]{
		ID:     "123",
		Method: vaulttypes.MethodSecretsList,
		Params: (*json.RawMessage)(&notAllowedParams),
	}
	require.NoError(t, err)
	testAuthForRequests(t, allowListedReq, notAllowListedReq)
```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L666-670)
```go
		}
		if result.GetId().Key != secretID {
			return fmt.Errorf("namespace %s key mismatch: got %q want %q", namespace, result.GetId().Key, secretID)
		}
		if !slices.Contains(expectedResponseOwners, result.GetId().Owner) {
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L745-750)
```go
		err = h.HandleJSONRPCUserMessage(t.Context(), validJSONRequest, callback)
		require.NoError(t, err)

		// send duplicate request
		err = h.HandleJSONRPCUserMessage(t.Context(), validJSONRequest, callback)
		require.ErrorContains(t, err, "request was already authorized previously")
```
