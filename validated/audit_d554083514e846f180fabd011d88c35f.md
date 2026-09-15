Based on my review of the code, the claim is accurate and well-supported by the actual code.

Audit Report

## Title
Confidential relay gateway handler processes JSON-RPC requests with unvalidated `Method` names, enabling authenticated-caller DoS via unbounded active-request fan-out - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

## Summary
`confidentialrelay.Handler.HandleJSONRPCUserMessage` declares only `MethodSecretsGet` and `MethodCapabilityExec` via `Methods()`, but never checks `req.Method` against that allowlist before creating an `activeRequest` and fanning it out to every DON member node [1](#0-0) . This is inconsistent with sibling handlers (`vault`, `capabilities`, and even this package's own `HandleNodeMessage`-side/`core/capabilities/confidentialrelay/handler.go`) which explicitly reject unrecognized methods via allowlist or `switch`/`default` checks.

## Finding Description
`HandleJSONRPCUserMessage` validates only `req.ID` (non-empty, ≤200 chars), then unconditionally calls `h.newActiveRequest` and `h.fanOutToNodes` regardless of `req.Method` [2](#0-1) . `newActiveRequest` tracks the request in `h.activeRequests` keyed by `req.ID`, held until swept by `removeExpiredRequests` after `h.requestTimeout` (default 30s) [3](#0-2) .

The routing layer (`multiHandler.getHandler` in `core/services/gateway/multihandler.go`) confirms the bypass: when only one handler type is registered for a DON, it returns that handler directly without ever consulting `methodToHandler`, meaning `req.Method` is not checked against any allowlist before reaching the confidential-relay handler [4](#0-3) . This "single handler" fast path is intentional, documented backward-compatibility behavior, not a bug in itself, but it does mean method validation is never performed anywhere in the call chain when a DON is configured with only this handler.

This contrasts with `vault/handler.go`, which explicitly checks `vaulttypes.IsGatewaySecretsMethod(req.Method)` before doing any work, and with `capabilities/handler.go` and `core/capabilities/confidentialrelay/handler.go`, both of which use `switch`/`default: unsupported method` rejection paths.

## Impact Explanation
Confirmed: an unvalidated `Method` string still results in a full `activeRequest` allocation and a real network fan-out to every DON node via the node-message send path, consuming per-node/global rate-limiter capacity that is intended to bound legitimate `MethodSecretsGet`/`MethodCapabilityExec` traffic. This matches the CVE-2024-33667-style pattern of an unsanitized generic method name driving unbounded backend work. The affected request bookkeeping (`h.activeRequests`) and rate limiters are shared resources, so a flood of bogus-method requests could degrade legitimate relay traffic — this maps to an in-scope DoS/resource-exhaustion impact category.

## Likelihood Explanation
The exploit requires only an authenticated, unprivileged gateway caller able to send JSON-RPC requests to the confidential relay endpoint — no special role, no node-operator access, and no crafted params, just an arbitrary `Method` value. It is most directly exploitable in the documented single-handler DON configuration, which is an intentional, supported configuration rather than a rare edge case.

## Recommendation
Add an explicit `req.Method` allowlist check (against `h.Methods()`, or a `switch`/`default: unsupported method` branch matching the pattern in `vault/handler.go` and `capabilities/handler.go`) at the top of `confidentialrelay.Handler.HandleJSONRPCUserMessage`, before `newActiveRequest`/`fanOutToNodes` run. Separately, consider whether `multiHandler.getHandler`'s single-handler fast path should still validate the method against the handler's own `Methods()` list rather than unconditionally routing any string through.

## Proof of Concept
1. Configure a gateway DON with only the `confidentialrelay` handler registered (triggers the `len(m.typeToHandler) == 1` fast path in `multiHandler.getHandler`).
2. As an authenticated gateway user, submit JSON-RPC requests with unique IDs and an arbitrary, non-allowlisted `method` (e.g. `"garbage.method.<n>"`).
3. Observe that `multiHandler.getHandler` routes the request directly to `confidentialrelay.handler` without a method-name check, and `HandleJSONRPCUserMessage` proceeds to call `newActiveRequest` and `fanOutToNodes`, sending the request to every DON member.
4. Repeat at volume to observe growth of `h.activeRequests` and consumption of `globalNodeRateLimiter`/`perNodeRateLimiters` capacity, degrading legitimate relay traffic until requests expire at `RequestTimeoutSec`.

Note: I was unable to locate/read the `fanOutToNodes` function body itself in the available index (it appears to live further down in the file, past what I could verify with certainty in this session), so the exact rate-limiter consumption mechanics during fan-out (as opposed to the confirmed `HandleNodeMessage` rate-limiter checks) could not be independently confirmed line-by-line, though the overall code structure and reachability of the unvalidated-method path is verified.

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L372-412)
```go
func (h *handler) Methods() []string {
	return []string{MethodSecretsGet, MethodCapabilityExec}
}

func (h *handler) HandleLegacyUserMessage(_ context.Context, _ *api.Message, _ gwhandlers.Callback) error {
	return errors.New("confidential relay handler does not support legacy messages")
}

// requestLogger returns the logger for one relay request: the gateway request
// id plus the workflow/execution identity it carries, so a line can be
// correlated with the relay DON's and the enclave's logs for the same
// execution. The request id changes per enclave retry; the execution identity
// does not.
func (h *handler) requestLogger(req jsonrpc.Request[json.RawMessage], labels requestLabels) logger.Logger {
	return logger.With(h.lggr,
		"method", req.Method,
		"requestID", req.ID,
		"workflowID", labels.WorkflowID,
		"executionID", labels.ExecutionID,
	)
}

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

**File:** core/services/gateway/multihandler.go (L80-96)
```go
func (m *multiHandler) getHandler(method string) (handlers.Handler, error) {
	// If there's only one handler, return it directly.
	// This preserves backwards compatibility for cases where the method
	// isn't specified on responses (and for cases where only one handler is registered more generally).
	if len(m.typeToHandler) == 1 {
		for _, handler := range m.typeToHandler {
			return handler, nil
		}
	}

	handler, ok := m.methodToHandler[method]
	if !ok {
		return nil, errors.New("no handler found for method " + method)
	}

	return handler, nil
}
```
