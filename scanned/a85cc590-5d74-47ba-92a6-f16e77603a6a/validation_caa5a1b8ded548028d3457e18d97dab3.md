### Title
Gateway Vault handler `HandleNodeMessage` matches only on request ID, allowing a stale node response for a completed request to be merged into a newly-created request that reuses the same ID - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
Like the Sublime `depositCollateral` bug, where funds could be applied to a loan that had already reached a terminal state because the function never checked the loan's status, the gateway-side Vault `handler` never checks whether an `activeRequest` instance is still the *same logical request* it was created for before merging a late node response into it. It matches purely on the client-supplied `req.ID` string. Once a request completes (or times out) it is deleted from `activeRequests`, freeing that ID for immediate reuse by any subsequent, unrelated caller. A node response that arrives late for the finished request can then be attributed to a brand-new request that happens to reuse the same ID.

### Finding Description
`HandleJSONRPCUserMessage` creates an `activeRequest` keyed only by the raw, client-controlled `req.ID`: [1](#0-0) 

`HandleNodeMessage` looks up the pending request purely by `resp.ID` and, aside from checking that the response `Method` matches the stored request's `Method`, performs no check that the response corresponds to the exact request instance/session that is still logically "in progress": [2](#0-1) 

Once a request finishes (success, error, or timeout), it is removed from `activeRequests` in `sendResponse`, immediately freeing the ID for reuse: [3](#0-2) 

`removeExpiredRequests` also reads the timed-out request list under `RLock`, releases the lock, and only afterward calls `sendResponse` (which deletes from the map) — creating a window where a slow node reply for the timed-out request can still be matched via `getActiveRequest` before the entry is deleted: [4](#0-3) 

Because the map key is exactly the client-supplied `req.ID` (no per-session nonce, DON-generated UUID, or requester-binding), any caller can choose an arbitrary ID. If an attacker submits a request using the same ID as a request that just completed or timed out (which is trivial to predict/observe since it's the ID they choose or can guess/brute force for common IDs), a delayed/duplicate response from a slow or malicious-but-still-honest-looking node for the *old* request can be delivered into the *attacker's newly created* `activeRequest`, since the only binding is the string ID and method name.

### Impact Explanation
This is a "cross-user response confusion" bug: a node response intended for one caller's already-finished request can be aggregated into a different caller's newer request that reused the same client-supplied ID. Depending on aggregation logic (`baseAggregator.Aggregate`), this could pollute the response set feeding into quorum computation for the new request with data that never belonged to it, or spuriously satisfy quorum with stale/mismatched node responses, leading to incorrect success/error responses being served to the wrong request instance. Because request IDs are attacker/user chosen and the gateway performs no requester-affinity or nonce binding, this weakens the request/response integrity guarantee the Gateway is supposed to provide between clients and vault nodes.

### Likelihood Explanation
The race window is real but requires: (1) attacker/observer knowledge of when a prior request with a chosen ID completes or times out, and (2) a slow-responding node still holding an in-flight response for the old request. The default `RequestTimeoutSec` is 30s and cleanup runs every 5s, giving a real window for stale/delayed node replies to still be routed via `getActiveRequest` before removal, especially under network delay or partial DON outages. Exploitability is bounded by external requirements (timing, slow node), similar to the "external requirements" caveat the original judge cited when classifying the analogous Sublime issue as Medium.

### Recommendation
Bind responses to request instances rather than to the reusable string ID alone:
- Generate an internal, gateway-assigned nonce/UUID per `activeRequest` (independent of the client-supplied `ID`) and use it as the map key and as the ID forwarded to nodes; translate back to the client ID only when responding.
- Alternatively, store a monotonically increasing generation/version counter per ID and only accept node responses matching the current generation, atomically checking-and-clearing under the same lock used to delete on completion/timeout, eliminating the TOCTOU window in `removeExpiredRequests`.

### Proof of Concept
1. Client A sends a Vault request with `ID = "X"`. The gateway creates `activeRequests["X"]` and fans out to nodes.
2. One DON node is slow to respond; the request times out after `RequestTimeoutSec`, and `removeExpiredRequests` reads it into `expiredRequests` (still present in `activeRequests` at read time).
3. Immediately after (but before `sendResponse` deletes the map entry), Client B sends a new request also with `ID = "X"` for the same method; `newActiveRequest` succeeds since the old entry is about to be deleted, or races right after deletion, and `activeRequests["X"]` now points to Client B's request.
4. The slow node's delayed response for Client A's original request arrives with `resp.ID == "X"`; `HandleNodeMessage` looks it up via `getActiveRequest("X")`, finds Client B's request, and merges the stale response into Client B's aggregation — [5](#0-4) .

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L360-384)
```go
// removeExpiredRequests removes expired requests from the pending requests map
func (h *handler) removeExpiredRequests(ctx context.Context) {
	h.mu.RLock()
	var expiredRequests []*activeRequest
	now := h.clock.Now()
	for _, userRequest := range h.activeRequests {
		if now.Sub(userRequest.createdAt) > h.requestTimeout {
			expiredRequests = append(expiredRequests, userRequest)
		}
	}
	h.mu.RUnlock()

	for _, er := range expiredRequests {
		responses := er.copiedResponses()
		var nodeResponses strings.Builder
		for nodeKey, nodeResponse := range responses {
			_, _ = fmt.Fprintf(&nodeResponses, "%s ---::: %v               ", nodeKey, nodeResponse)
		}
		nodeResponsesStr := nodeResponses.String()
		err := h.sendResponse(ctx, er, h.errorResponse(er.req, api.RequestTimeoutError, errors.New("request expired without getting quorum of responses from nodes. Available responses: "+nodeResponsesStr), []byte(nodeResponsesStr)))
		if err != nil {
			h.lggr.Errorw("error sending response to user", "requestID", er.req.ID, "error", err)
		}
	}
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

**File:** core/services/gateway/handlers/vault/handler.go (L480-516)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	l := logger.With(h.lggr, "method", resp.Method, "requestID", resp.ID, "nodeAddr", nodeAddr)
	l.Debugw("handling node response")

	if !h.nodeRateLimiter.Allow(nodeAddr) {
		l.Debugw("node is rate limited", "nodeAddr", nodeAddr)
		return nil
	}

	ar := h.getActiveRequest(resp.ID)
	if ar == nil {
		// Request is not found, so we don't need to send a response to the user
		// This can happen if a slow node responds after the request has already been completed
		l.Debugw("no pending request found for ID")
		return nil
	}

	if resp.Result != nil && resp.Error != nil {
		l.Errorw("node response contains both a result and an error, dropping", "nodeAddr", nodeAddr)
		h.recordInvalidNodeResponseEnvelope(ctx, "node_response_result_and_error")
		return nil //nolint:nilerr // tampered envelope is intentionally dropped; handling succeeded so there is no error to report
	}

	if resp.Method != ar.req.Method {
		l.Errorw("node response method does not match request method, dropping", "nodeAddr", nodeAddr, "responseMethod", resp.Method, "requestMethod", ar.req.Method)
		h.recordInvalidNodeResponseEnvelope(ctx, "node_response_method_mismatch")
		return nil
	}

	ok := ar.addResponseForNode(nodeAddr, resp)
	if !ok {
		l.Errorw("duplicate response from node, ignoring", "nodeAddr", nodeAddr)
		return nil
	}

	copiedResponses := ar.copiedResponses()
	resp, err := h.aggregator.Aggregate(ctx, l, ar.req.ID, copiedResponses, resp)
```

**File:** core/services/gateway/handlers/vault/handler.go (L803-839)
```go
func (h *handler) sendResponse(ctx context.Context, userRequest *activeRequest, resp gwhandlers.UserCallbackPayload) error {
	switch resp.ErrorCode {
	case api.StaleNodeResponseError:
	case api.FatalError:
	case api.NodeReponseEncodingError:
	case api.RequestTimeoutError:
	case api.HandlerError:
	case api.ConflictError:
	case api.LimitExceededError:
		h.metrics.requestInternalError.Add(ctx, 1, metric.WithAttributes(
			attribute.String("don_id", h.donConfig.DonID),
			attribute.String("error", resp.ErrorCode.String()),
		))
	case api.InvalidParamsError:
	case api.UnsupportedMethodError:
	case api.UserMessageParseError:
	case api.UnsupportedDONIdError:
		h.metrics.requestUserError.Add(ctx, 1, metric.WithAttributes(
			attribute.String("don_id", h.donConfig.DonID),
		))
	case api.NoError:
		h.metrics.requestSuccess.Add(ctx, 1, metric.WithAttributes(
			attribute.String("don_id", h.donConfig.DonID),
		))
	}

	err := userRequest.SendResponse(resp)
	if err != nil {
		h.lggr.Errorw("error sending response to user", "requestID", userRequest.req.ID, "error", err)
		return err
	}

	h.mu.Lock()
	defer h.mu.Unlock()
	delete(h.activeRequests, userRequest.req.ID)
	h.lggr.Debugw("response sent to user", "requestID", userRequest.req.ID, "errorCode", resp.ErrorCode)
	return nil
```
