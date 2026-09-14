Based on my investigation, I found a concrete analog in the legacy WebAPI capabilities gateway handler.

### Title
Cross-request response confusion via unauthenticated MessageID in WebAPI gateway trigger callback resolution - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The `handler.HandleLegacyUserMessage` / `handleWebAPITriggerMessage` flow in the legacy WebAPI capabilities gateway handler resolves a pending user callback purely by matching `msg.Body.MessageID`, without verifying that the responding message's content (topics, payload, trigger event) actually corresponds to what the original requester asked for, and without waiting for quorum across DON nodes. This mirrors the `NomadFacet.onReceive()` bug class: a request-identifying token (`transferId` / `MessageID`) is trusted as sufficient proof of correspondence between two independently-submitted payloads, when it is not cryptographically bound to the payload content by the party consuming it.

### Finding Description
`HandleLegacyUserMessage` stores the user's callback keyed only by the client-supplied `msg.Body.MessageID`: [1](#0-0) 

`handleWebAPITriggerMessage` then completes that callback using **whatever `msg` a node reports** for that `MessageID`, taking the **first** node's response unconditionally, with an explicit TODO acknowledging the missing quorum check: [2](#0-1) 

The only verification performed on the incoming node response is that the `Sender` field parses to a signature matching a real DON member (`msg.Validate()` inside `common.ValidatedMessageFromResp`) and that `msg.Body.Sender == nodeAddr`: [3](#0-2) 

Nothing ties the `MessageID` to a hash or signature of the *original request's* payload/topics/timestamp. If two different clients submit `HandleLegacyUserMessage` requests with the same `MessageID` (a client-chosen, unauthenticated string — validated only for length/null-suffix in `Message.Validate()`), the callback map (`h.savedCallbacks[msg.Body.MessageID]`) is a single global keyspace shared across all users of the DON, exactly like `s.reconciledTransfers[transferId]` in the report is a single global keyspace on Connext's side that trusted an unverified `_extraData`-derived ID.

### Impact Explanation
An unprivileged external actor who can reach the gateway's HTTP API (`ProcessRequest` → `HandleLegacyUserMessage`) can pick an arbitrary `MessageID` and race a victim's legitimate request using the same ID. Whichever request a DON node answers first "wins" and its response is delivered to whichever caller's callback is still registered under that ID — since the map is keyed by ID and deleted upon first match, this can result in cross-user response confusion: a victim receiving a response addressed to (and generated from) an unrelated attacker-controlled request, or the attacker's callback being resolved with the victim's data, depending on race timing. This matches "cross-user response confusion," one of the concrete accepted impact classes for this analog.

### Likelihood Explanation
This requires only unprivileged client access to the gateway's legacy JSON-RPC endpoint plus knowledge/control of the `MessageID` field — no privileged role, no malicious node, and no network-layer trust assumption beyond the existing gateway ingress. The comment in the code ("TODO: in practice, we should wait for at least 2F+1 nodes to respond") indicates the developers are aware the current design is a placeholder/single-node-trust model, increasing confidence this is a real, currently-reachable gap rather than a hardened path (contrast with the newer `v2` HTTP trigger handler and the `vault` handler, both of which enforce per-request unique-ID checks, BFT quorum aggregation via `CollectAndAggregate`/`Aggregate`, and (for vault) additional `SignedPayloadRequestID` binding — see `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go` and `core/services/gateway/handlers/vault/handler.go`).

### Recommendation
- Reject duplicate `MessageID`s from different senders/sessions (the newer `newActiveRequest` pattern used in `v2/http_trigger_handler.go` and `vault/handler.go`, which errors on `req.ID already exists`, should be applied here too).
- Require BFT quorum (2F+1) across DON node responses before resolving the callback, as already noted by the TODO, instead of accepting the first responder unconditionally.
- Bind the `MessageID`/request identity cryptographically to the original request's payload hash (or scope the ID by a caller/session identifier) so a node response cannot be matched to a callback whose original request payload it does not correspond to.

### Proof of Concept
1. Attacker sends `HandleLegacyUserMessage` (or the corresponding gateway HTTP JSON-RPC user request) with `MessageID = "X"` and attacker-chosen `TriggerRequestPayload`.
2. Concurrently, victim sends a legitimate request also using `MessageID = "X"` (possible if IDs collide by chance, are predictable, or are attacker-supplied where the protocol allows client-chosen IDs) — both `HandleLegacyUserMessage` calls insert into the shared `h.savedCallbacks["X"]` map, with the second overwriting the first.
3. A DON node responds first to whichever request it processes first; `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds whichever callback is currently stored, deletes the entry, and delivers that node's response payload — potentially the victim's data going to the attacker's callback or vice versa — with no verification that the response corresponds to the request that established that particular callback.

**Uncertainty note:** I could not fully verify from the indexed code whether the gateway's outward-facing HTTP entrypoint enforces per-caller uniqueness or randomization of `MessageID` before it reaches `HandleLegacyUserMessage` (this depends on `ProcessRequest` in `core/services/gateway/gateway.go`, which only checks length ≤ 200, not uniqueness or ownership). If such an external uniqueness constraint exists elsewhere, it would reduce likelihood; a full Devin session would be needed to trace all call sites of `HandleLegacyUserMessage` to confirm whether `MessageID` is ever attacker-influenced end-to-end in the currently-deployed workflow entrypoints.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L148-162)
```go
func (h *handler) handleWebAPITriggerMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.mu.Lock()
	savedCb, found := h.savedCallbacks[msg.Body.MessageID]
	delete(h.savedCallbacks, msg.Body.MessageID)
	h.mu.Unlock()

	if found {
		// Send first response from a node back to the user, ignore any other ones.
		// TODO: in practice, we should wait for at least 2F+1 nodes to respond and then return an aggregated response
		// back to the user.
		codec := api.JSONRPCCodec{}
		return savedCb.SendResponse(handlers.UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(msg), ErrorCode: api.NoError})
	}
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L248-267)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	msg, err := common.ValidatedMessageFromResp(resp)
	if err != nil {
		return err
	}
	if msg.Body.Sender != nodeAddr {
		return errors.New("message sender mismatch when reading from node ")
	}
	start := time.Now()
	switch msg.Body.Method {
	case MethodWebAPITrigger:
		err = h.handleWebAPITriggerMessage(ctx, msg, nodeAddr)
	case MethodWebAPITarget, MethodComputeAction, MethodWorkflowSyncer:
		err = h.handleWebAPIOutgoingMessage(ctx, msg, nodeAddr)
	default:
		err = fmt.Errorf("unsupported method: %s", msg.Body.Method)
	}
	h.metrics.recordHandleDuration(ctx, time.Since(start), msg.Body.Method, err == nil)
	return err
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L410-420)
```go

	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```
