### Title
Missing single-completion guard allows a vault gateway request to be answered twice via a race between node-response success and expiry paths - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
CVE-2018-9517 is a Linux kernel use-after-free in `pppol2tp_connect` caused by two concurrent code paths racing to finalize/tear down the same socket state without a single-owner guard. The Chainlink Gateway's `confidentialrelay` handler explicitly recognizes and defends against the equivalent class of bug for its per-request lifecycle object (`activeRequest`), using an `atomic.Bool` `completed` flag with `CompareAndSwap` so that only the first of several racing completion paths (node response, quorum grace, expiry) is allowed to finalize the request: [1](#0-0) 

The `vault` handler manages the analogous per-request object (`activeRequest`) with the same set of racing completion paths — successful node/quorum completion via `HandleNodeMessage` → `sendSuccessResponse` and timeout completion via `removeExpiredRequests` — but its `sendResponse` function has **no** such completion guard: [2](#0-1) 

### Finding Description
`vault.handler.sendResponse` unconditionally calls `userRequest.SendResponse(resp)` and only afterward removes the request from `h.activeRequests` under `h.mu`: [3](#0-2) 

Two independent goroutines can hold a reference to the same `*activeRequest` at the same time:
- The periodic cleanup goroutine (`removeExpiredRequests`) reads `h.activeRequests` under `RLock`, copies out expired entries, releases the lock, and then calls `sendResponse` on each expired request: [4](#0-3) 
- Concurrently, `HandleNodeMessage` (invoked per incoming node response) fetches the same `*activeRequest` via `getActiveRequest`, and — once quorum/aggregation succeeds — calls `sendSuccessResponse` → `sendResponse` on the exact same object: [5](#0-4) 

Because there is no `completed`/CAS-style flag on `vault.activeRequest` (unlike `confidentialrelay.activeRequest`, which carries `completed atomic.Bool` precisely to prevent this): [6](#0-5) , both the expiry path and the node-quorum path can observe the same still-present entry in `h.activeRequests` before either deletes it, and both proceed to call `userRequest.SendResponse(resp)` on the shared object. This is structurally the same "resource is torn down/answered from two racing paths with no ownership token" defect class as `pppol2tp_connect`'s UAF: the fix pattern chosen by the codebase for the sibling `confidentialrelay` handler (`sendResponseAndClearRequest`'s `CompareAndSwap`) demonstrates that this exact race is a known, previously-fixed bug class in this gateway, but `vault`'s `sendResponse` was not given the same protection.

The confidentialrelay handler's own code comments confirm this is a recognized race class in this codebase: "Concurrent completion paths (node-message forward, terminal-state forward, quorum grace, expiry) may all race here; only the first claimer sends." [7](#0-6) 

### Impact Explanation
A double call to `userRequest.SendResponse` on the same request/callback is the moral equivalent of a double-free/use-after-free on the request's completion object: depending on the underlying `Callback` implementation (a channel-based one-shot callback, per the `handlerscommon` package used across handlers), a second `SendResponse` on an already-completed callback is likely to panic (e.g., send on/close of an already-closed channel), crashing the goroutine handling gateway traffic and potentially the whole gateway process. This is reachable purely by an unprivileged client's ordinary request timing (their own vault secrets request, e.g. `MethodSecretsGet`/`MethodSecretsCreate`) intersecting with the DON's legitimate node responses arriving near the configured `RequestTimeoutSec` boundary — no malicious node or peer behavior is required. A crash of the gateway process is a availability/DoS impact affecting all tenants sharing that gateway instance, and in the JSON-RPC response-confusion case, could also surface a stale/duplicate response to the wrong logical completion path.

### Likelihood Explanation
Likelihood is moderate: it requires the cleanup ticker (`defaultCleanUpPeriod = 5s`) to fire for a request that is simultaneously reaching quorum on the node-response path — i.e., a request whose timeout and node-quorum-completion occur within a narrow window. This is a naturally occurring race under load (many concurrent vault requests, slow/variable node latency) rather than something requiring attacker-controlled internal timing precision, since the attacker (an authenticated vault client) only needs to submit ordinary requests and let normal timeout/response timing collide — no special privileges beyond normal authenticated API access are needed.

### Recommendation
Add the same single-owner completion guard used in `confidentialrelay.activeRequest` to `vault.activeRequest`: introduce an `atomic.Bool` (or similar) `completed` field, and in `vault.handler.sendResponse`, `CompareAndSwap(false, true)` before calling `userRequest.SendResponse`, returning early (as a no-op) if another path already claimed the request. This mirrors `sendResponseAndClearRequest` in `core/services/gateway/handlers/confidentialrelay/handler.go` and eliminates the double-completion race.

### Proof of Concept
Conceptual reproduction (exact panic behavior of the shared `Callback.SendResponse` implementation could not be fully confirmed within this investigation because `core/services/gateway/handlers/common/callback.go` was not inspected in depth):
1. Submit an authenticated vault request (e.g. `secrets_get`) that requires quorum from multiple DON nodes.
2. Arrange (or wait, under normal load) for the DON's collective node responses to reach quorum at very nearly the same time the cleanup goroutine's `defaultCleanUpPeriod` tick observes the request as expired (`now.Sub(userRequest.createdAt) > h.requestTimeout`).
3. `HandleNodeMessage`'s success path and `removeExpiredRequests`' expiry path both retrieve the same `*activeRequest` and both call `h.sendResponse(ctx, ar, ...)`, each unconditionally invoking `userRequest.SendResponse(resp)`.

**Uncertainty note:** I was not able to inspect `core/services/gateway/handlers/common/callback.go` in this session (ran out of tool iterations) to confirm whether a second `SendResponse` call panics, is silently swallowed, or returns an error. The structural race itself (two completion paths against a shared, unguarded `activeRequest`) is confirmed directly in `vault/handler.go`, and its severity depends on that callback implementation's behavior on double-send, which should be verified by a Devin agent with full file access before treating this as more than a probable finding.

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L110-126)
```go
type activeRequest struct {
	req       jsonrpc.Request[json.RawMessage]
	labels    requestLabels
	responses map[string]*jsonrpc.Response[json.RawMessage]
	mu        sync.Mutex
	completed atomic.Bool

	// graceStarted is set the first time the request holds F+1 signed responses, so
	// the grace deadline is armed once per request rather than moved forward by every
	// later response. graceDeadline is guarded by mu and is only meaningful once
	// graceStarted is set.
	graceStarted  atomic.Bool
	graceDeadline time.Time

	createdAt time.Time
	gwhandlers.Callback
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L730-746)
```go
// sendResponseAndClearRequest claims the request, sends payload, and removes it from
// activeRequests. Concurrent completion paths (node-message forward,
// terminal-state forward, quorum grace, expiry) may all race here; only the first
// claimer sends. Metrics are recorded only after a successful send so losers do not
// double-count.
func (h *handler) sendResponseAndClearRequest(ctx context.Context, ar *activeRequest, payload gwhandlers.UserCallbackPayload) error {
	if !ar.completed.CompareAndSwap(false, true) {
		// Another path already answered this request.
		return nil
	}

	sendErr := ar.SendResponse(payload)

	h.mu.Lock()
	delete(h.activeRequests, ar.req.ID)
	h.mu.Unlock()

```

**File:** core/services/gateway/handlers/vault/handler.go (L361-384)
```go
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
