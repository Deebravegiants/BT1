### Title
Global (non-sender-scoped) `req.ID` map allows an unprivileged client to force another user's Vault / Confidential-Relay gateway request to fail - ([File: core/services/gateway/handlers/vault/handler.go], [File: core/services/gateway/handlers/confidentialrelay/handler.go])

### Summary
The `V3Vault.repay`/`liquidate` bug lets an attacker submit a cheap, minimal transaction that mutates shared state (debt shares) so a legitimate user's subsequent call reverts because it hits a strict equality/limit check on that shared state. The same DoS *shape* — an unprivileged actor claiming a shared resource key first, at negligible cost, causing a legitimate request to fail outright — exists in the Chainlink gateway's `HandleJSONRPCUserMessage` request bookkeeping for the Vault and Confidential-Relay handlers, which key in-flight requests solely by the caller-supplied JSON-RPC `id`, with no per-sender namespacing.

### Finding Description
Both gateway handlers maintain a single, handler-wide `activeRequests map[string]*activeRequest` keyed only by the raw JSON-RPC request `id` supplied by the caller: [1](#0-0) [2](#0-1) 

`HandleJSONRPCUserMessage` only validates that `req.ID` is non-empty and ≤200 characters — it performs no per-sender scoping of the ID before calling `newActiveRequest`: [3](#0-2) [4](#0-3) 

Both `newActiveRequest` implementations reject a request outright if the same `id` string is already active, regardless of who submitted it:
```go
if h.activeRequests[req.ID] != nil {
    return nil, errors.New("request ID already exists: " + req.ID)
}
```
This "request ID already exists" error is returned synchronously from `HandleJSONRPCUserMessage`, i.e. before authorization/attestation processing runs to completion for the *colliding* second caller (for Vault, authorization actually runs before this check, but the check itself, and the confidential-relay handler's version, run with zero identity binding — see below).

By contrast, the codebase already has the correct pattern elsewhere: `core/services/gateway/handlers/common/requestcache.go` explicitly scopes its pending-request key by `globalID{sender, id}`: [5](#0-4) 

That sender+id composite key is the correct mitigation for exactly this class of collision — it is absent from both the Vault and Confidential-Relay handlers' `activeRequests` maps. Tests in both packages confirm the current (vulnerable) contract: sending the *same* `id` a second time — with no requirement that it come from the same authenticated principal — always fails with "already exists"/"already authorized previously": [6](#0-5) [7](#0-6) 

The gateway's `multiHandler.HandleJSONRPCUserMessage` dispatches directly to the per-method handler by `Method` with no upstream deduplication or sender-aware ID rewriting: [8](#0-7) 

Consequently, any two unrelated, unprivileged callers of the gateway's Vault or Confidential-Relay JSON-RPC methods who submit a request with the same `id` value will have one of the two calls unconditionally rejected — purely because of the shared, un-namespaced map key. An attacker does not need to defeat authorization/attestation to cause the collision-rejection itself to fire; the "ID already exists" check fires as soon as an entry is present in the map for that id (for the Confidential-Relay handler this happens immediately in `HandleJSONRPCUserMessage`, before any content/attestation validation of *either* request). This mirrors the reported bug's core mechanic: an unprivileged actor performs a cheap/no-cost operation (choosing an arbitrary, colliding request ID) that forces a legitimate operation on the same key to revert/fail.

### Impact Explanation
This is a request-level denial-of-service against the internet-facing Vault and Confidential-Relay gateway handlers. If a victim's client uses a predictable or low-entropy `id` scheme (e.g., sequential counters, deterministic IDs derived from workflow/execution identifiers, or a fixed value reused by a retry loop), any unauthenticated/unprivileged network caller who can reach the gateway's JSON-RPC endpoint for these methods can pre-empt that ID, causing:
- The victim's genuine Vault secrets request (create/update/delete/list) to fail with "request ID already exists," or
- The victim's genuine Confidential-Relay capability/secrets request to fail the same way.

Because the Vault handler processes authorization (`ProcessRequest`) prior to `newActiveRequest`, exploitation there is somewhat harder for a purely unauthenticated attacker (the attacker still needs to submit *some* authorized-looking or at least well-formed vault request to occupy the slot — but it does not need to be for the same owner/secret, since the map is keyed by `req.ID` alone, not owner+ID). For the Confidential-Relay handler, `newActiveRequest` is called immediately in `HandleJSONRPCUserMessage`, with no authorization gate at all in that code path, meaning collision alone (no valid attestation, no valid workflow) is sufficient to occupy an `id` slot.

The severity depends on how request IDs are generated by legitimate clients (this is not fully knowable from static analysis of this repo alone — client-side ID generation lives in SDK/workflow code outside what was inspected). If IDs are sufficiently random/high-entropy per request, exploitation requires either predicting or observing a victim's ID in-flight (e.g., via network timing/side channels), which raises the bar but does not eliminate the design flaw: the map is architecturally missing the sender-scoping that the codebase's own `requestcache.go` demonstrates is the intended, correct pattern.

### Likelihood Explanation
Moderate. The vulnerable code path is reachable by any client that can send JSON-RPC user messages to the gateway for the `vault` or `confidentialrelay` handlers — these are explicitly described as internet-facing gateway handlers. No special privilege is needed to submit a request with an arbitrary `id`. The main uncertainty (not resolvable from this repo) is the entropy/predictability of `id` values used by legitimate callers; if IDs are anything less than cryptographically random and unique per caller (e.g., workflow-execution-derived, sequential, or retried with a fixed ID as the confidential-relay code's own comments about "retry ... same logical identity" suggest is a real scenario), collision is trivial to engineer.

### Recommendation
Scope the `activeRequests` map key by sender/authenticated identity in addition to the caller-supplied `id`, following the existing `globalID{sender, id}` pattern already used in `core/services/gateway/handlers/common/requestcache.go`. Concretely:
- In `core/services/gateway/handlers/vault/handler.go`, key `activeRequests` by a composite of the authorized owner (or gateway-node/sender identity) and `req.ID`, not `req.ID` alone.
- In `core/services/gateway/handlers/confidentialrelay/handler.go`, perform the same composite keying, and additionally ensure `newActiveRequest` is not invoked (or the ID-collision check does not leak information/reject) until minimal caller identity has been established, so an unauthenticated collision cannot preempt a legitimate slot.
- Add regression tests confirming that two different senders may reuse the same `id` value concurrently without one rejecting the other, mirroring the sender-scoped test coverage that presumably exists for `requestcache.go`.

### Proof of Concept
Conceptual PoC (cannot be executed here, but derivable directly from existing unit tests):
1. Victim (owner A) sends a legitimate `secrets.create`/`capability.exec` JSON-RPC request to the gateway with `id = "X"`.
2. Before the victim's request completes/expires, attacker (unrelated identity, or for Confidential-Relay, no valid attestation at all) sends any request to the same handler method with the same `id = "X"`.
3. Whichever of the two requests reaches `newActiveRequest` second receives `errors.New("request ID already exists: " + req.ID)` and is dropped — as directly demonstrated by the existing tests: [6](#0-5) [7](#0-6) 

These tests currently validate the "same ID always collides" behavior as *intended*, but they do not (and cannot, given the current key design) distinguish "same sender retries" from "different, unrelated senders collide," which is the crux of the vulnerability.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L394-401)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-412)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	labels := h.extractRequestLabels(req)
	l := h.requestLogger(req, labels)
	l.Debugw("handling confidential relay request", "nodes", len(h.donConfig.Members), "f", h.donConfig.F)

	ar, err := h.newActiveRequest(req, labels, callback)
	if err != nil {
		return err
	}

	return h.fanOutToNodes(ctx, l, ar)
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L414-430)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], labels requestLabels, callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID, "executionID", labels.ExecutionID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		labels:    labels,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```

**File:** core/services/gateway/handlers/common/requestcache.go (L34-66)
```go
type globalID struct {
	sender string
	id     string
}

type pendingRequest[T any] struct {
	handlers.Callback
	responseData *T
	timeoutTimer *time.Timer
	mu           sync.Mutex
}

func NewRequestCache[T any](timeout time.Duration, maxCacheSize uint32) RequestCache[T] {
	return &requestCache[T]{cache: make(map[globalID]*pendingRequest[T]), timeout: timeout, maxCacheSize: maxCacheSize}
}

func (c *requestCache[T]) NewRequest(lggr logger.Logger, request *api.Message, callback handlers.Callback, responseData *T) error {
	if request == nil {
		return errors.New("request is nil")
	}
	if responseData == nil {
		return errors.New("responseData is nil")
	}
	key := globalID{request.Body.Sender, request.Body.MessageID}
	c.mu.Lock()
	defer c.mu.Unlock()
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
	if len(c.cache) >= int(c.maxCacheSize) {
		return errors.New("request cache is full")
	}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler_test.go (L863-881)
```go
func TestConfidentialRelayHandler_DuplicateRequestID(t *testing.T) {
	t.Parallel()
	h, cb, don, _ := setupHandler(t, 4)
	don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Return(nil)

	params := json.RawMessage(`{"workflow_id":"wf1"}`)
	req := jsonrpc.Request[json.RawMessage]{
		ID:     "req-dup",
		Method: MethodCapabilityExec,
		Params: &params,
	}

	err := h.HandleJSONRPCUserMessage(t.Context(), req, cb)
	require.NoError(t, err)

	cb2 := common.NewCallback()
	err = h.HandleJSONRPCUserMessage(t.Context(), req, cb2)
	require.ErrorContains(t, err, "request ID already exists")
}
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L707-753)
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

		err = h.HandleNodeMessage(t.Context(), &response, NodeOne.Address)
		require.NoError(t, err)
```

**File:** core/services/gateway/multihandler.go (L62-69)
```go
func (m *multiHandler) HandleJSONRPCUserMessage(ctx context.Context, jsonRequest jsonrpc.Request[json.RawMessage], callback handlers.Callback) error {
	h, err := m.getHandler(jsonRequest.Method)
	if err != nil {
		return fmt.Errorf("failed to get handler for method %s: %w", jsonRequest.Method, err)
	}

	return h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
}
```
