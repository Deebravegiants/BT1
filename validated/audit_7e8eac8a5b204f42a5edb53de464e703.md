## Analysis

The RLN bug pattern — an unprivileged actor griefing another user by supplying an ID/key that is not scoped to the caller's own identity — has a direct analog in the HTTP trigger handler of the gateway.

### Root cause

`httpTriggerHandler` keeps a single, gateway-wide map of in-flight requests keyed **only by the client-supplied JSON-RPC `id`** (`requestID`), with no scoping to the caller, workflow owner, or workflow ID: [1](#0-0) 

`validateRequestID` only rejects empty IDs or IDs containing `/` — it does not require the ID to be unique per caller or per workflow: [2](#0-1) 

The collision check in `setupCallback` looks the ID up in this single shared map and rejects the request outright if the slot is already taken — by anyone, for any workflow: [3](#0-2) 

Any caller authorized to trigger *some* workflow (even their own, unrelated one) reaches `authorizeRequest`/`checkRateLimit` before `setupCallback` is invoked, and can pick an arbitrary `id` value. Because the map is not partitioned per-workflow-owner, an attacker who chooses (or predicts/races) the same `id` as a victim's concurrent or imminent request occupies the shared slot first. The victim's legitimate call to `setupCallback` then hits the `found` branch and is rejected with `jsonrpc.ErrConflict` ("requestID ... has already been used"), denying/delaying that user's workflow execution — the same "spam a shared key to block someone else's operation" pattern as the RLN `slashCommitments` bug, just applied to trigger execution instead of slash reveal windows.

By contrast, the vault gateway handler avoids this exact issue by explicitly prefixing the request ID with the authorized owner before using it as a map key: [4](#0-3) 

`httpTriggerHandler` has no equivalent owner/workflow-scoping of `requestID` before using it as the `callbacks` map key.

### Title
Unprivileged HTTP trigger callers can grief another workflow's execution via requestID collision in the shared `callbacks` map - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

### Summary
`httpTriggerHandler.setupCallback` stores pending trigger requests in a single map keyed only by the caller-supplied JSON-RPC `id`, without namespacing by workflow owner or workflow ID. Any authorized caller can choose an arbitrary `id`, so a malicious or careless caller can occupy the same `id` slot that another user's request needs, causing that user's legitimate `workflows.execute` call to be rejected with a conflict error.

### Finding Description
`HandleUserTriggerRequest` validates and authorizes the caller against a specific workflow, then calls `setupCallback(ctx, req.ID, callback, requestStartTime, workflowID)` [5](#0-4) . `setupCallback` checks and inserts into `h.callbacks`, a map global to the handler instance and thus shared across every workflow and every workflow owner on that gateway node [3](#0-2) . The only validation on the `id` is that it is non-empty and contains no `/` [2](#0-1) ; there is no requirement that it be unpredictable, nor is it namespaced by the authorized workflow owner (unlike the vault handler's `owner + separator + id` scheme [4](#0-3) ).

Consequently, the "ownership" of a given `requestID` slot is first-come-first-served across all tenants of the gateway, not scoped to the caller who is entitled to use it — structurally the same flaw as `slashCommitments[account][hash]` being writable by any slasher regardless of who the hash "belongs to."

### Impact Explanation
A caller authorized only to trigger their own (or any) workflow can deny service to another tenant's workflow execution by pre-occupying a `requestID` the victim is expected to use (e.g., idempotency keys, sequential/predictable IDs, or IDs guessed/observed via side channels or shared conventions). The victim's real request fails with `jsonrpc.ErrConflict` and never reaches the DON, delaying or blocking that execution — a direct availability/griefing impact on another, unrelated user's workflow trigger, analogous to delaying another slasher's reveal window.

### Likelihood Explanation
Requires only capability to submit any authorized HTTP trigger request to the gateway and knowledge/prediction of another caller's chosen `id`. Many client integrations use predictable or low-entropy request IDs (timestamps, counters, UUIDs derived from public data), making collision more feasible than pure guessing of a keccak hash.

### Recommendation
Scope the `callbacks` map key (and the conflict check) by an identity the attacker cannot forge — e.g., `workflowOwner + separator + requestID` or `workflowID + separator + requestID` — mirroring the pattern already used in `gateway_vault_request_processor.go`'s `authorizeAndStamp`, so that a `requestID` collision can only occur within the same authorized owner's own requests.

### Proof of Concept
1. Attacker is authorized to trigger `workflowA` (their own workflow) and knows/predicts that a victim will soon submit a `workflows.execute` request for `workflowB` with JSON-RPC `id = "X"`.
2. Attacker submits a `workflows.execute` request for `workflowA` with `id = "X"` first; `setupCallback` inserts `h.callbacks["X"]` successfully.
3. Victim submits their legitimate request for `workflowB` with `id = "X"`; `setupCallback` finds `h.callbacks["X"]` already present and rejects it via `handleUserError(..., jsonrpc.ErrConflict, "requestID: X has already been used...")`, denying the victim's execution until the attacker's entry is reaped.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L58-65)
```go
type httpTriggerHandler struct {
	services.StateMachine
	config                  ServiceConfig
	shards                  []*shardEndpoint
	nodeAddrToShard         map[string]*shardEndpoint
	lggr                    logger.Logger
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L141-146)
```go
	doneCh, err := h.setupCallback(ctx, req.ID, callback, requestStartTime, workflowID)
	if err != nil {
		return err
	}

	return h.sendWithRetries(ctx, legacyExecutionID, executionIDWithTriggerIndex, reqWithKey, workflowID, doneCh)
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L278-281)
```go
	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID
```
