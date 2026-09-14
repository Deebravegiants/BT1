Confirmed analog found: the Vault gateway's `RequestReplayGuard` marks a request digest as permanently "consumed" at the authorization step, *before* the actual downstream operation (`CreateSecrets`/`UpdateSecrets`/`DeleteSecrets`) is attempted. If that downstream call fails for any transient/internal reason after authorization succeeds, the client receives an error response but can never resubmit the identical request — the digest is already recorded and `CheckAndRecord` will reject it as a replay for the entire TTL window. This mirrors the M-1 bug-class: a system that is supposed to guarantee replayability of a client-submitted operation instead has a state transition ("authorized"/finalized) commit before the operation truly completes, permanently bricking the retry path and losing the user's ability to persist/manage secrets (their "funds"/data in this domain).

### Title
Vault Gateway `RequestReplayGuard` permanently consumes request digest before downstream secret operation completes, bricking legitimate retries - (File: core/capabilities/vault/authorizer.go)

### Summary
`authorizer.AuthorizeRequest` calls `a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt())` immediately after authorization succeeds and *before* `GatewayHandler.HandleGatewayMessage` invokes the actual `secretsService.CreateSecrets`/`UpdateSecrets`/`DeleteSecrets` call. If that later call fails (e.g. transient internal error, DON timeout, master public key unavailable in a later step, etc.), the request as a whole errors out to the client, but the digest has already been irreversibly marked as "seen" in `RequestReplayGuard`, so the identical request can never be resubmitted until the TTL expires. [1](#0-0) 

### Finding Description
The pipeline invariant documented in `GatewayVaultRequestProcessor` is: `ValidateStructureBeforeAuth → AuthorizeRequest → Prefix ID → StampAuthorizedParams → ValidateOwnerScopedLimits`, and `AuthorizeRequest` is explicitly stated to apply "the replay guard (digest deduplication)". [2](#0-1) 

`RequestReplayGuard.CheckAndRecord` records the digest with an expiry and returns `ErrRequestAlreadySeen` on any subsequent identical digest until that expiry passes — there is no mechanism to "un-record" a digest if downstream processing later fails. [3](#0-2) 

The recording happens inside `authorizer.AuthorizeRequest`, which is invoked from `GatewayVaultRequestProcessor.authorizeAndStamp` — i.e., purely as part of authorization/validation, well before the actual vault operation (`CreateSecrets`, `UpdateSecrets`, `DeleteSecrets`) is executed by `GatewayHandler.HandleGatewayMessage`. [4](#0-3) [5](#0-4) 

Concretely, `HandleGatewayMessage` runs `ProcessRequest` (which triggers replay-guard recording via `AuthorizeRequest`) and only afterward — in a separate step — calls `h.handleSecretsCreate` / `h.handleSecretsUpdate` / `h.handleSecretsDelete`, each of which can independently fail and return an error response to the gateway/client: [6](#0-5) 

Because the digest is derived from the request content (deterministic), and is consumed unconditionally at authorization time regardless of whether the downstream secret operation later succeeds or fails, any transient failure in the downstream call (DB error, TDH2 encryption service unavailability, network/DON dispatch failure, etc.) permanently blocks the client from resubmitting that exact request for the remainder of the digest's TTL. This is structurally the same root cause as M-1: a guarantee of replayability/idempotent retry is broken because a "committed" state (finalized in `OptimismPortal` / recorded digest in `RequestReplayGuard`) is set before the full operation is confirmed to have succeeded, and there is no corresponding "failed" bucket (like `failedMessages` in the CrossDomainMessenger) that would allow the operation to be legitimately replayed.

### Impact Explanation
An unprivileged, otherwise-legitimate client (a workflow owner submitting create/update/delete secret requests through the public gateway) can lose the ability to ever successfully submit a specific secret-management request if the downstream operation transiently fails after authorization succeeds. Since secrets are per-owner, per-namespace, per-key, this can permanently prevent legitimate secret creation/update/deletion for a given identifier — analogous to the original bug's "permanent loss of funds/replayability" for CrossDomainMessenger withdrawals, translated to "permanent loss of the ability to persist/modify a secret" for Vault. There is no self-recovery path exposed to the client; they must wait out the TTL (`expiresAt`) of the replay guard entry, if this is even discoverable, since the error surfaced to the client is a generic replay-guard message (`"request was already authorized previously"`) that does not distinguish "already succeeded" from "authorized once but failed downstream." [7](#0-6) 

### Likelihood Explanation
This requires no malicious actor — any transient failure downstream of authorization (which is common in distributed multi-node DON dispatch, encryption service hiccups, or ORM/storage errors) is sufficient to trigger the bricking condition on every retry attempt with identical parameters, since the digest is content-derived and deterministic. The window is bounded by the TTL configured via `AuthResult.ExpiresAt()`, but until it lapses, every identical resubmission is unconditionally rejected regardless of whether the previous attempt actually completed.

### Recommendation
Only record the digest in `RequestReplayGuard` once the downstream vault operation (`CreateSecrets`/`UpdateSecrets`/`DeleteSecrets`) has been confirmed to succeed, or introduce a compensating mechanism (analogous to `failedMessages` in `CrossDomainMessenger`) that allows a request whose downstream execution failed to be safely retried — e.g., recording provisional digests with a short-lived "in-flight" state that is either promoted to a long-TTL "completed" state on success or cleared on failure, rather than unconditionally committing the anti-replay record at authorization time regardless of the eventual outcome.

### Proof of Concept
1. A workflow owner sends a `secrets/create` JSON-RPC request through the gateway to `GatewayHandler.HandleGatewayMessage`.
2. `ProcessRequest` → `authorizeAndStamp` → `Authorizer.AuthorizeRequest` succeeds, computing `authResult.Digest()` and calling `replayGuard.CheckAndRecord(digest, expiresAt)`, which records the digest as seen. [1](#0-0) 
3. Control returns to `HandleGatewayMessage`, which then calls `h.handleSecretsCreate(ctx, gatewayID, req)`; assume `h.secretsService.CreateSecrets(...)` returns a transient error (e.g., encryption/storage backend momentarily unavailable). [8](#0-7) 
4. `handleSecretsCreate` returns an error response (`api.FatalError`) to the caller via the gateway.
5. The client, believing the operation is retryable (standard expectation for idempotent/retryable RPC operations), resubmits the exact same request.
6. `AuthorizeRequest` recomputes the same digest and `CheckAndRecord` now returns `ErrRequestAlreadySeen`, so the retry is rejected with `"replay guard rejected request" / "request was already authorized previously"` even though the original request never actually created the secret. [9](#0-8) 
7. The client cannot successfully create that secret until the recorded digest's TTL (`expiresAt`) lapses, with no indication from the error message that the block is transient rather than a genuine duplicate-submission rejection.

### Citations

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L20-30)
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
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-293)
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

	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID

	if err := stamp(prefixedRequestID); err != nil {
		p.lggr.Errorw("failed to stamp authorized request params", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("failed to stamp authorized request params: %w", err)
	}

	p.lggr.Debugw("authorized gateway vault request", "method", req.Method, "requestID", req.ID, "owner", authorizedOwner, "orgID", authResult.OrgID(), "workflowOwner", authResult.WorkflowOwner())
	return &AuthorizedGatewayVaultRequest{
		Req:        *req,
		AuthResult: authResult,
	}, nil
}
```

**File:** core/capabilities/vault/request_replay_guard.go (L9-47)
```go
var ErrRequestAlreadySeen = errors.New("request was already authorized previously")

// RequestReplayGuard prevents replay of already-processed requests by tracking
// request digests with expiry timestamps. It is safe for concurrent use.
//
// Used by both the AllowListBasedAuth flow and the JWTBasedAuth flow to ensure
// that a given request digest is only accepted once.
type RequestReplayGuard struct {
	mu      sync.Mutex
	seen    map[string]int64 // digest → unix expiry timestamp
	nowFunc func() time.Time // injectable for testing
}

// NewRequestReplayGuard creates a replay guard for authorized Vault requests.
func NewRequestReplayGuard() *RequestReplayGuard {
	return &RequestReplayGuard{
		seen:    make(map[string]int64),
		nowFunc: time.Now,
	}
}

// CheckAndRecord returns ErrRequestAlreadySeen if the digest was previously
// recorded and has not yet expired. Otherwise it records the digest with
// the given expiry timestamp (unix seconds, UTC).
//
// Expired entries are cleaned up on every call.
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

**File:** core/capabilities/vault/gw_handler.go (L180-236)
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
	}

	if err = h.gatewayConnector.SendToGateway(ctx, gatewayID, response); err != nil {
		reqLggr.Errorw("Failed to send message to gateway", "error", err)
		return err
	}

	reqLggr.Infow("Sent message to gateway", "resp", response)
	h.metrics.requestSuccess.Add(ctx, 1, metric.WithAttributes(
		attribute.String("gateway_id", gatewayID),
	))
	return nil
}
```

**File:** core/capabilities/vault/gw_handler.go (L275-336)
```go
func (h *GatewayHandler) handleSecretsCreate(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	vaultCapRequest := vaultcommon.CreateSecretsRequest{}
	if err := json.Unmarshal(*req.Params, &vaultCapRequest); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized create secrets request", "request", vaultCapRequest.String())
	vaultCapResponse, err := h.secretsService.CreateSecrets(ctx, &vaultCapRequest)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.FatalError, err)
	}

	jsonResponse, err := toJSONResponse(vaultCapResponse, req.Method)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}
	return jsonResponse
}

func (h *GatewayHandler) handleSecretsUpdate(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	vaultCapRequest := vaultcommon.UpdateSecretsRequest{}
	if err := json.Unmarshal(*req.Params, &vaultCapRequest); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized update secrets request", "request", vaultCapRequest.String())
	vaultCapResponse, err := h.secretsService.UpdateSecrets(ctx, &vaultCapRequest)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.FatalError, err)
	}

	jsonResponse, err := toJSONResponse(vaultCapResponse, req.Method)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}
	return jsonResponse
}

func (h *GatewayHandler) handleSecretsDelete(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.DeleteSecretsRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized delete secrets request", "request", r.String())
	resp, err := h.secretsService.DeleteSecrets(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to delete secrets: %w", err))
	}

	resultBytes, err := resp.ToJSONRPCResult()
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}

	return &jsonrpc.Response[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      req.ID,
		Method:  req.Method,
		Result:  (*json.RawMessage)(&resultBytes),
	}
}
```
