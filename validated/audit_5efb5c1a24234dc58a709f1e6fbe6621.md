Found the key issue: `setupCallback` in `http_trigger_handler.go` keys the in-flight `h.callbacks` map purely by the caller-supplied `requestID` (`req.ID`), with no per-owner/per-caller namespacing (unlike the vault gateway path, which prefixes the request ID with the authorized owner before using it as a map key). Since `authorizeRequest` (workflow-level auth) happens *before* `setupCallback`, but the callback map key itself is never scoped to the authorized workflow owner, any unprivileged caller who can guess or observe a `requestID` used against a *public* workflow (workflow IDs/names are not secret — they're looked up via `GetWorkflowReference`/`GetWorkflowID`) can pre-register that same `requestID` first, causing the legitimate caller's subsequent request to be rejected with `"requestID: %s has already been used"` before it is ever dispatched to nodes.

### Title
Unprivileged caller can pre-claim another user's HTTP trigger `requestID` to block workflow execution requests - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The Putty report shows that an attacker can supply attacker-controlled fields (arbitrary token/NFT contracts) that later cause a shared operation (`exercise()`/`withdraw()`) to permanently revert, denying legitimate counterparties access to the assets/executions they are entitled to. The chainlink gateway's HTTP workflow trigger handler has an analogous "locking" pattern: the `requestID` is fully caller-controlled and is used as the sole key into a shared, unauthenticated, gateway-wide map (`h.callbacks`) that gates whether a workflow-execution request is accepted at all.

### Finding Description
`HandleUserTriggerRequest` validates and authorizes the trigger request (`validatedTriggerRequest`, `resolveWorkflowID`, `authorizeRequest`), then calls `setupCallback`, which does: [1](#0-0) 

The `requestID` used as the map key is the raw, unauthenticated, user-supplied `req.ID` value; the only requirement enforced on it is non-empty and no `/` character: [2](#0-1) 

Unlike the vault gateway path — where `authorizeAndStamp` deliberately prefixes the request ID with the `authorizedOwner` before it is used as the key into the analogous `activeRequests` map, guaranteeing that IDs are namespaced per authenticated owner and cannot collide across users ( [3](#0-2) ) — the HTTP trigger handler's `h.callbacks` map has no such per-owner namespacing: [4](#0-3) 

Because `workflowID`/`workflowName`+`workflowOwner`+`workflowTag` are not secret (any caller can resolve them via `resolveWorkflowID` and target a specific victim's workflow), and `requestID` uniqueness is checked globally rather than per-authorized-owner/caller, an attacker who is authorized against *any* workflow (or even the same public workflow the victim intends to call) can submit a trigger request using the exact `requestID` the victim is about to use (e.g., a predictable, sequential, or otherwise guessable client-generated ID), claiming that slot in `h.callbacks` first. The victim's subsequent legitimate request with the same ID is rejected outright: [5](#0-4) 

### Impact Explanation
This is analogous to the Putty "locking orders" bug class in that a party who does not control the victim's execution path can nonetheless block that execution from ever being accepted/dispatched, purely by pre-occupying a shared resource keyed on attacker-influenceable data (the request ID). The attack does not require compromising the victim's credentials, only knowledge/guessability of the `requestID` value they will submit, and results in a request-availability denial (`jsonrpc.ErrConflict`, "requestID has already been used") for the legitimate caller of a specific workflow trigger. The severity is bounded by the requirement that the attacker must correctly guess/predict the victim's `requestID` and by the fact that the entry is reaped after `CleanUpPeriodMs`, but for any client using low-entropy or deterministic IDs (e.g., incrementing counters, timestamps, or client SDK defaults) this is a realistic DoS on a specific execution attempt.

### Likelihood Explanation
Likelihood depends entirely on how unpredictable client-chosen `requestID` values are; well-randomized UUIDs make guessing impractical, but nothing in the code enforces ID randomness/uniqueness format beyond the "no `/`" check, and no per-owner namespace prevents an unrelated, unprivileged caller from squatting on any ID string before the intended request arrives.

### Recommendation
Namespace the `h.callbacks` map key by the authorized workflow owner/caller identity (similar to the vault gateway's `authorizedOwner + separator + requestID` prefixing pattern) rather than relying solely on the raw, cross-tenant-shared `req.ID` string, so that ID collisions can only occur within the same authorized owner's own request stream, not across independent unprivileged callers.

### Proof of Concept
1. Attacker resolves a target victim's public `workflowID` via `resolveWorkflowID` (workflow identifiers/owners/names/tags are not secret and can be resolved through the same API).
2. Attacker predicts/observes the `requestID` the victim's client will use next (e.g., sequential integer, timestamp-based, or otherwise low-entropy ID scheme).
3. Attacker sends a `workflows.execute` HTTP trigger request against the target workflow using that exact `requestID`, successfully passing `authorizeRequest` for their own credentials and calling `setupCallback`, which inserts the entry into `h.callbacks[requestID]`.
4. Victim's legitimate request with the same `requestID` arrives; `setupCallback` finds `h.callbacks[requestID]` already populated and returns `jsonrpc.ErrConflict` ("requestID ... has already been used"), rejecting the victim's execution request entirely.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L58-72)
```go
type httpTriggerHandler struct {
	services.StateMachine
	config                  ServiceConfig
	shards                  []*shardEndpoint
	nodeAddrToShard         map[string]*shardEndpoint
	lggr                    logger.Logger
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
	stopCh                  services.StopChan
	workflowMetadataHandler *WorkflowMetadataHandler
	userRateLimiter         limits.RateLimiter
	metrics                 *metrics.Metrics
	wg                      sync.WaitGroup
	orgResolver             orgresolver.OrgResolver // optional; nil if the node isn't configured to resolve orgs (e.g. no Linking Service)
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L190-202)
```go
func (h *httpTriggerHandler) validateRequestID(ctx context.Context, requestID string, callback handlers.Callback) error {
	if requestID == "" {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "'id' field is required and cannot be empty. Use a new unique request 'id' for each request", callback)
		return errors.New("empty request ID")
	}
	// Request IDs from users must not contain "/", since this character is reserved
	// for internal node-to-node message routing (e.g., "http_action/{workflowID}/{uuid}").
	if strings.Contains(requestID, "/") {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "request ID must not contain '/'", callback)
		return errors.New("request ID must not contain '/'")
	}
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-426)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-281)
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
```
