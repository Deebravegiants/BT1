Based on my investigation, I found a concrete, unprivileged-actor-reachable design flaw in the vault gateway handler's request-ID namespace, not a direct analog of the token-price-manipulation report, but a genuine authentication/authorization-adjacent bug fitting the required categories (gateway message envelopes / handlers / caches).

### Title
Unauthenticated `PublicKeyGet` requests can squat owner-prefixed vault request IDs, enabling unprivileged denial-of-service against targeted vault owners - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
The Vault gateway handler shares a single `activeRequests` map keyed by `req.ID` across two security domains: authorized, owner-prefixed secrets requests (`SecretsCreate/Update/Delete/List`) and unauthenticated `PublicKeyGet` requests. Because `PublicKeyGet` skips authorization and uses the raw, attacker-supplied `req.ID` directly as the map key, an unprivileged client can pre-register any ID string — including the exact `owner::id` value that a legitimate, authorized secrets request will later be assigned — and thereby block that victim's request.

### Finding Description
`HandleJSONRPCUserMessage` branches on method before any authorization check: [1](#0-0) 

For `MethodPublicKeyGet`, the code calls `h.newActiveRequest(req, callback)` using the client-supplied `req.ID` verbatim — no ownership/authorization stamping is applied. For all other vault methods, the ID is only inserted into the same map *after* going through `h.requestProcessor.ProcessRequest`, which authorizes the caller and rewrites `req.ID` to `authorizedOwner + RequestIDSeparator + originalRequestID`: [2](#0-1) 

Both code paths insert into the identical `h.activeRequests` map: [3](#0-2) 

`newActiveRequest` rejects any request whose ID already exists, and the existing test explicitly validates this "already exists" behavior blocks the second submitter's request entirely rather than merging or queuing it: [4](#0-3) 

Because `owner` values (Ethereum-style workflow-owner addresses) are public/discoverable (e.g. on-chain, or via allowlist enumeration) and `RequestId` values used by legitimate clients are frequently short, sequential, or otherwise predictable, an attacker can precompute `owner + RequestIDSeparator + guessedID` strings and submit them as unauthenticated `PublicKeyGet.ID` values ahead of time. When the real owner's secrets request later authorizes and gets stamped to that same ID, `newActiveRequest` returns `"request ID already exists"`, and `HandleJSONRPCUserMessage` returns that error immediately without ever forwarding the request to the vault DON nodes: [5](#0-4) 

The gateway's top-level `ProcessRequest` propagates this straight back to the caller as an HTTP error, confirming to the attacker that their guess was live and denying the victim's operation: [6](#0-5) 

### Impact Explanation
An unauthenticated/unprivileged client can selectively deny legitimate `SecretsCreate`, `SecretsUpdate`, `SecretsDelete`, and `SecretsList` operations for a targeted vault owner by pre-registering the deterministic `owner::id` request ID via a cost-free `PublicKeyGet` call. This is a request/ID impersonation across security domains that results in denial of service for vault secret management, without requiring any credentials, JWT, or allowlist membership.

### Likelihood Explanation
Exploitation requires only network access to the gateway's public endpoint (no authentication) and knowledge/guessing of the target owner address plus the request ID the legitimate client will use. Owner addresses are generally public, and many callers use predictable/sequential request IDs, making this practically exploitable, though the attacker must win a timing race (register before the victim's request completes authorization).

### Recommendation
Segregate the request-ID namespace by security domain — e.g., prefix unauthenticated `PublicKeyGet` request IDs with a fixed, reserved marker (or use a separate map) so they can never collide with owner-prefixed authorized secrets request IDs. Alternatively, require `PublicKeyGet` IDs to be rejected if they contain the `RequestIDSeparator` sequence, closing the cross-domain collision entirely.

### Proof of Concept
1. Attacker learns/derives the checksummed workflow-owner address `0xVictim` (public on-chain data) that a victim will use for a `SecretsCreate` call, and knows the victim tends to use request ID `"1"`.
2. Attacker sends an unauthenticated JSON-RPC request to the gateway: `{"method":"vault_publicKeyGet","id":"0xVictim::1"}`. This bypasses authorization entirely (per `handler.go:404-420`) and inserts `activeRequests["0xVictim::1"]`.
3. Victim later submits a legitimate `vault_secretsCreate` request with `id:"1"`. After successful authorization, the processor rewrites the ID to `"0xVictim::1"` (per `gateway_vault_request_processor.go` `authorizeAndStamp`), and `newActiveRequest` fails with `"request ID already exists: 0xVictim::1"`, so the victim's secret-creation request is never forwarded to the vault DON.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L404-420)
```go
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
```

**File:** core/services/gateway/handlers/vault/handler.go (L426-441)
```go
	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
	authorizedOwner := authorized.AuthResult.AuthorizedOwner()

	h.lggr.Debugw("handling authorized vault request", "method", req.Method, "requestID", req.ID, "authorizedOwner", authorizedOwner)
	ar, activeRequestErr := h.newActiveRequest(req, callback)
	if activeRequestErr != nil {
		return activeRequestErr
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L457-472)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L707-750)
```go
	t.Run("unhappy path - duplicate requestId", func(t *testing.T) {
		h, callback, don, _ := setupHandler(t)
		don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Return(nil)

		requestID := "1"
		reqData := &vaultcommon.ListSecretIdentifiersRequest{
			RequestId: requestID,
			Owner:     owner,
		}
		reqDataBytes, err := json.Marshal(reqData)
		require.NoError(t, err)

		validJSONRequest := jsonrpc.Request[json.RawMessage]{
			ID:     requestID,
			Method: vaulttypes.MethodSecretsList,
			Params: (*json.RawMessage)(&reqDataBytes),
		}

		responseData := &vaultcommon.ListSecretIdentifiersResponse{
			Identifiers: []*vaultcommon.SecretIdentifier{
				{
					Key:       "foo",
					Owner:     owner,
					Namespace: "default",
				},
			},
		}
		resultBytes, err := json.Marshal(responseData)
		require.NoError(t, err)
		expectedRequestID := owner + vaulttypes.RequestIDSeparator + requestID
		response := jsonrpc.Response[json.RawMessage]{
			ID:     expectedRequestID,
			Result: (*json.RawMessage)(&resultBytes),
			Method: vaulttypes.MethodSecretsList,
		}
		resultBytes, err = json.Marshal(responseData)
		require.NoError(t, err)

		err = h.HandleJSONRPCUserMessage(t.Context(), validJSONRequest, callback)
		require.NoError(t, err)

		// send duplicate request
		err = h.HandleJSONRPCUserMessage(t.Context(), validJSONRequest, callback)
		require.ErrorContains(t, err, "request was already authorized previously")
```

**File:** core/services/gateway/gateway.go (L276-279)
```go
	}
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
	}
```
