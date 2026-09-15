## Title
Stale/late node trigger responses can be misdelivered to an unrelated, reused request ID, causing cross-user response confusion in the gateway HTTP trigger handler - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

### Summary
The Chakra report's root cause is that a failed/expired async cross-chain state is torn down (marked `Failed`) without any mechanism to reconcile it with the original caller, and — more generally — that the protocol reuses/loses track of transaction identity across an asynchronous boundary. The `HTTPTriggerHandler` in the gateway has an analogous asynchronous lifecycle problem: request identity (`requestID`) is only protected from collision while an entry is "in-flight" in `h.callbacks`. Once a request is torn down by the reaper (`reapExpiredCallbacks`) without ever completing, its ID becomes free for reuse, but out-of-band, delayed node responses for the *old* request are still routed purely by that string ID with no execution nonce, allowing them to be matched against a brand-new, unrelated request that later reuses the same ID.

### Finding Description
`setupCallback` only rejects a `requestID` while it is present in `h.callbacks`: [1](#0-0) 

Entries are removed either when quorum is reached (`HandleNodeTriggerResponse`, marking `processed=true` and later reaped) or, critically, by `reapExpiredCallbacks`, which deletes an **unprocessed** entry once it exceeds the clean-up period, closing `doneCh` with no response ever sent to the user: [2](#0-1) 

Once deleted, the `requestID` is free to be reused by any subsequent request (`setupCallback` no longer sees a conflict). Node responses, however, are matched purely by `resp.ID` string against the live `h.callbacks` map — there is no execution nonce, workflowID, or owner binding checked against the *actual* originating request beyond what is looked up in the map at the time the response arrives: [3](#0-2) 

If a slow/late node response belonging to the reaped (old) request arrives after a **new, unrelated** request has registered the same `requestID` (e.g., a different workflow, different owner, different input) and that new request happens to be assigned to a shard (`donID`) that also served the old request, the aggregator lookup `saved.responseAggregators[shard.donID]` succeeds, and the late response is fed into the new request's `IdenticalNodeResponseAggregator`: [4](#0-3) 

`CollectAndAggregate` only aggregates responses by content-digest and does not validate that the response corresponds to the request currently associated with that ID beyond the map lookup already performed by the caller: [5](#0-4) 

If enough stale/late node responses for the old execution accumulate to reach quorum, `saved.SendResponse` is invoked and the wrong (stale, unrelated) execution result is delivered to the new caller as if it were the answer to their own request: [6](#0-5) 

This mirrors the Chakra bug class: an asynchronous cross-boundary operation (cross-chain message / gateway-to-node trigger) can terminate in a failed/expired state, and the system's later handling of a delayed/late follow-up ("cross_chain_callback" / late node response) is not correctly reconciled against the *current* owner of that transaction identity, resulting in state — or in this case, response content — being misapplied to a party that never issued that operation.

### Impact Explanation
A caller could receive output data belonging to a completely different, unrelated workflow execution (potentially another workflow owner's execution), instead of the result of their own request. Depending on what these workflow outputs contain, this is a confidentiality/integrity issue for the second (legitimate) caller receiving unauthorized or wrong data, and a correctness issue that could cause a client to act on the wrong result. This is a cross-user response confusion vulnerability class, matching the accepted category from the rules.

### Likelihood Explanation
Exploitation/occurrence requires: (1) an unprocessed request being reaped (achievable simply by allowing a request to time out, which is entirely in an unprivileged caller's control by intentionally causing slow responses or picking marginal timing), (2) a new request reusing the exact same `requestID` string before or shortly after the stale node responses trickle in, and (3) that new request being assigned to at least one shard/DON in common with the old request (likely in real deployments where a small number of DONs serve many workflows). Because `requestID` is entirely user-supplied and uniqueness is enforced only transiently, a client (malicious or accidental) can trivially engineer condition (2), and condition (3) is a property of deployment topology rather than an obstacle. This makes the scenario plausible without any node/operator compromise, purely from the internet-facing gateway API surface.

### Recommendation
- Bind response matching to a globally unique, non-reusable execution identifier for the full lifetime a response could arrive (e.g. combine `requestID` with the legacy/derived `executionID` or a per-registration monotonic nonce), and validate that a late response's originating shard/workflow matches the one recorded for the *current* holder of that ID before aggregating.
- When an ID is reaped, tombstone it (rather than freeing it for immediate reuse) for at least the maximum plausible late-response window, so stale responses are provably rejected instead of silently matched to a different request.
- On reap of an unprocessed callback, send an explicit timeout/error response to the caller (mirroring `handleUserError`) instead of only incrementing a metric, so callers get a definitive terminal answer rather than depending on their own client-side timeout — closing the same "no notification of failure" gap the underlying report is centered on.

### Proof of Concept
1. Client A sends a trigger request with `id="X"` for `workflowID=W1` (owner O1), assigned to shard `donID=D`. Some nodes in `D` respond slowly.
2. Before quorum is reached, `CleanUpPeriodMs` elapses; `reapExpiredCallbacks` deletes the entry for `id="X"` and closes `doneCh`, without notifying Client A of failure (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:561-581`).
3. Client B (or Client A again) immediately sends a new trigger request also using `id="X"`, for a different `workflowID=W2` (owner O2), which also happens to be assigned to shard `D`. `setupCallback` accepts it since the old entry is gone (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:419-426`).
4. The slow nodes from step 1's shard `D` finally deliver their (stale) response for `id="X"`. `HandleNodeTriggerResponse` finds the *new* callback entry for `id="X"` (belonging to W2/O2), matches shard `D` to a valid aggregator, and feeds in the stale W1 response (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:474-517`).
5. If enough such stale responses accumulate to reach the shard's quorum threshold, `saved.SendResponse` fires, delivering Client B the result of Client A/O1's W1 execution instead of the actual W2 result — a concrete cross-user response confusion.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L474-497)
```go
func (h *httpTriggerHandler) HandleNodeTriggerResponse(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	h.lggr.Debugw("handling trigger response", "requestID", resp.ID, "nodeAddr", nodeAddr, "error", resp.Error, "result", resp.Result)
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()
	saved, exists := h.callbacks[resp.ID]
	if !exists {
		return errors.New("callback not found for request ID: " + resp.ID)
	}
	if saved.processed {
		h.lggr.Debugw("request already processed, ignoring late response", "requestID", resp.ID, "nodeAddr", nodeAddr)
		return nil
	}

	// Route the response into the aggregator for the shard that owns this node.
	shard, ok := h.nodeAddrToShard[nodeAddr]
	if !ok {
		return fmt.Errorf("received trigger response from unknown node %s (no owning shard)", nodeAddr)
	}
	agg, ok := saved.responseAggregators[shard.donID]
	if !ok {
		// The node belongs to a shard this workflow isn't assigned to (or the
		// callback was captured before the workflow was assigned there).
		return fmt.Errorf("node %s (shard %s) is not assigned to workflow for request ID %s", nodeAddr, shard.donID, resp.ID)
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L498-530)
```go
	aggResp, err := agg.CollectAndAggregate(resp, nodeAddr)
	if err != nil {
		return err
	}
	if aggResp == nil {
		h.lggr.Debugw("Not enough responses to aggregate", "requestID", resp.ID, "nodeAddress", nodeAddr, "shard", shard.donID)
		return nil
	}
	rawResp, err := json.Marshal(aggResp)
	if err != nil {
		return errors.New("failed to marshal response: " + err.Error())
	}

	err = saved.SendResponse(handlers.UserCallbackPayload{
		RawResponse: rawResp,
		ErrorCode:   api.NoError,
	})
	if err != nil {
		return err
	}

	// First shard to reach quorum wins: after successfully sending the response,
	// mark the callback as processed and close doneCh, stopping all shard sends.
	// The entry is kept in the map so late responses are recognized as such and
	// is removed later by the periodic reaper.
	saved.processed = true
	close(saved.doneCh)
	h.callbacks[resp.ID] = saved
	latencyMs := time.Since(saved.requestStartTime).Milliseconds()
	h.metrics.RecordRequestHandlerLatency(ctx, latencyMs, h.lggr)
	h.metrics.IncrementRequestSuccess(ctx, h.lggr)
	h.lggr.Debugw("Sent response to user", "requestID", resp.ID, "latencyMs", latencyMs)
	return nil
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L561-581)
```go
// reapExpiredCallbacks removes callbacks that are older than the maximum age
func (h *httpTriggerHandler) reapExpiredCallbacks(ctx context.Context) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()
	now := time.Now()
	var expiredCount int
	for reqID, callback := range h.callbacks {
		if now.Sub(callback.createdAt) > time.Duration(h.config.CleanUpPeriodMs)*time.Millisecond {
			if !callback.processed {
				h.metrics.IncrementRequestErrors(ctx, jsonrpc.ErrInternal, h.lggr)
			}
			h.cleanupCallback(reqID)
			expiredCount++
		}
	}
	if expiredCount > 0 {
		h.metrics.IncrementPendingRequestsCleanUpCount(ctx, int64(expiredCount), h.lggr)
		h.lggr.Infow("Removed expired callbacks", "count", expiredCount, "remaining", len(h.callbacks))
	}
	h.metrics.RecordPendingRequestsCount(ctx, int64(len(h.callbacks)), h.lggr)
}
```

**File:** core/services/gateway/common/aggregation/response_aggregator.go (L38-75)
```go
func (agg *IdenticalNodeResponseAggregator) CollectAndAggregate(
	resp *jsonrpc.Response[json.RawMessage],
	nodeAddress string) (*jsonrpc.Response[json.RawMessage], error) {
	if resp == nil {
		return nil, errors.New("response cannot be nil")
	}
	if nodeAddress == "" {
		return nil, errors.New("node address cannot be empty")
	}

	key, err := resp.Digest()
	if err != nil {
		return nil, fmt.Errorf("error generating digest for response: %w", err)
	}

	// Check if the node already submitted a different response
	if oldKey, exists := agg.nodeToResponse[nodeAddress]; exists && oldKey != key {
		if nodes, ok := agg.responses[oldKey]; ok {
			nodes.Remove(nodeAddress)
			// Clean up empty response groups
			if len(nodes) == 0 {
				delete(agg.responses, oldKey)
			}
		}
	}

	if _, ok := agg.responses[key]; !ok {
		agg.responses[key] = make(StringSet)
	}
	agg.responses[key].Add(nodeAddress)
	agg.nodeToResponse[nodeAddress] = key

	if len(agg.responses[key]) >= agg.threshold {
		return resp, nil
	}

	return nil, nil
}
```
