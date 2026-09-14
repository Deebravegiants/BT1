### Title
Gateway Vault handler violates checks-effects-interactions: response is sent to the user before the request is removed from `activeRequests`, allowing duplicate concurrent responses/DoS from unprivileged node messages - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The gateway-side Vault handler's `sendResponse` performs the external interaction (delivering the result to the caller via `userRequest.SendResponse(resp)`) before mutating internal state (`delete(h.activeRequests, userRequest.req.ID)`). This mirrors the reported CEI violation in `LeverageModule::_mint()`, where the external/observable action (`_safeMint`) happens before the state update (`tokenIdNext += 1`), leaving a window in which the stale state can be acted upon again.

### Finding Description
`sendResponse` is the single choke point that both (1) invokes the user-facing callback and (2) removes the request from `h.activeRequests`: [1](#0-0) 

Note the ordering: `userRequest.SendResponse(resp)` is called first, and only afterward, under `h.mu.Lock()`, is the entry deleted from `h.activeRequests`. Between these two steps the request is still "active" and discoverable by `getActiveRequest`.

`HandleNodeMessage` is reachable from any DON node message (an unprivileged/external-initiator-adjacent surface relative to the gateway) and looks up the active request, records the per-node response, aggregates, and on quorum calls `sendSuccessResponse` → `sendResponse`: [2](#0-1) 

Because different nodes' responses can be processed by different goroutines concurrently, and the request is only "checked" via `ar.addResponseForNode` (per-node dedup) and `getActiveRequest` (returns non-nil until the CEI-violating delete happens), two concurrent goroutines that each independently observe quorum being reached (e.g., the last two nodes needed to cross the aggregation threshold arriving back-to-back) can both proceed past their own `errors.Is(err, errInsufficientResponsesForQuorum)` check and both call `sendSuccessResponse`/`sendResponse` for the same `ar` before either has deleted it from `activeRequests`. This results in `userRequest.SendResponse` being invoked more than once for the same logical request.

### Impact Explanation
Delivering more than one response for a single request ID via the gateway callback path is a state-mutation-after-external-interaction defect analogous to the reported bug class. Depending on the concrete `Callback.SendResponse` implementation (a one-shot channel/response writer per gateway HTTP request), a second invocation can panic (e.g., "send on closed channel") or silently overwrite/duplicate a response delivered to the HTTP caller, producing cross-request response confusion or a crash/DoS of the handling goroutine. This is reachable without any privileged capability — it only requires ordinary DON node responses arriving in the expected concurrent pattern once quorum is reached.

### Likelihood Explanation
The race window is narrow (only the time between `userRequest.SendResponse` and the mutex-protected delete) but is systematically reachable: whenever aggregation quorum is reached by two node responses processed in parallel goroutines (which is the normal operating mode of `HandleNodeMessage`, one goroutine per incoming node message), both can observe non-error quorum status before the deletion completes. No malicious node behavior is required — only ordinary timing of two legitimate DON members' responses.

### Recommendation
Apply the CEI pattern: remove/mark the `activeRequest` as completed (e.g., delete from `h.activeRequests` or set a "responded" flag under `h.mu`) before performing the external `userRequest.SendResponse(resp)` call, and make the state transition itself the gate that only allows a single caller to proceed to `SendResponse`. For example, use a `sync.Once` on the `activeRequest`, or perform the deletion first and skip sending if the request was already deleted/claimed by a concurrent goroutine.

### Proof of Concept
1. Configure a Vault DON with quorum threshold reachable by 2 of N nodes.
2. Send a valid `MethodSecretsCreate`/similar request through the gateway; it fans out to all DON members via `fanOutToVaultNodes`.
3. Arrange (or naturally have, given real network timing) two node responses to arrive close together such that `HandleNodeMessage` is invoked concurrently by two goroutines for the same request ID once quorum is reached.
4. Both goroutines pass `ar.addResponseForNode` (different node addresses, so both succeed) and both compute quorum via `h.aggregator.Aggregate`, and thus both call `h.sendSuccessResponse(ctx, l, ar, resp)` → `h.sendResponse`.
5. Because the entry is not removed from `activeRequests` until after `userRequest.SendResponse` returns, both goroutines call `userRequest.SendResponse(resp)` on the same underlying callback before either has deleted it, resulting in a double-send for one request ID.

Note: I could not fully verify the exact runtime behavior of `handlerscommon.Callback.SendResponse` (channel-based, presumably single-use) within the indexed context, so the precise failure mode (panic vs. silent duplicate delivery) should be confirmed by inspecting `core/services/gateway/handlers/common` in a full checkout.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L480-534)
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
	switch {
	case errors.Is(err, errInsufficientResponsesForQuorum):
		l.Debugw("aggregating responses, waiting for other nodes...", "error", err)
		return nil
	case err != nil:
		l.Error("quorum unobtainable, returning response to user...", "error", err, "responses", maps.Values(copiedResponses))
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, err, nil))
	}

	switch resp.Method {
	case vaulttypes.MethodPublicKeyGet:
		h.tryCachePublicKeyResponse(resp, l)
	default:
		// Do nothing for other methods
	}

	return h.sendSuccessResponse(ctx, l, ar, resp)
}
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
