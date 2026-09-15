## Analog Found: Integer Underflow → Panic in Gateway Workflow ID/Owner Normalization

### Title
Integer underflow in `normalizeHex` causes `strings.Repeat` panic reachable from unauthenticated HTTP trigger requests - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

### Summary
Similar to the Frontier MODEXP precompile bug (CVE-2022-21685), where insufficient bounds validation before a subtraction caused an integer underflow and a crash, the Chainlink gateway's `httpTriggerHandler.normalizeHex` function computes `expectedHexLength - len(hexStr)` without validating that `hexStr` (the raw hex digits, after best-effort `"0x"` stripping) is not longer than `expectedHexLength`. When this difference goes negative, it is passed directly to `strings.Repeat`, which panics on negative counts. This is reachable from an unprivileged, unauthenticated actor sending an HTTP trigger request to the gateway.

### Finding Description
`validateHexInput` (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:267-283`) only checks that the *raw* input string (including any `"0x"` prefix) does not exceed `expectedLength` (`workflowIDLength=66` or `workflowOwnerLength=42`), that it's lowercase, and that it's decodable as hex after stripping an optional `"0x"` prefix. It never verifies that the input actually contains the `"0x"` prefix, nor that the *hex-digit-only* length fits within `expectedLength-2`. [1](#0-0) 

Later, `normalizeHex` is called to pad/re-prefix the value:
```go
func normalizeHex(input string, length int) string {
	hexStr := strings.TrimPrefix(input, "0x")
	// length-2 because we'll add "0x" prefix
	expectedHexLength := length - 2
	paddedHex := strings.Repeat("0", expectedHexLength-len(hexStr)) + hexStr
	return "0x" + paddedHex
}
``` [2](#0-1) 

If a caller supplies an input **without** the `"0x"` prefix whose length equals `expectedLength` (e.g., a 66-character all-lowercase hex string for `workflowID`, or a 42-character one for `workflowOwner`), `TrimPrefix` is a no-op (nothing to strip), so `len(hexStr) == expectedLength`, while `expectedHexLength == expectedLength - 2`. The subtraction `expectedHexLength - len(hexStr)` becomes `-2`, and `strings.Repeat("0", -2)` panics, since Go's `strings.Repeat` panics on a negative count.

Both call sites are reachable directly from `resolveWorkflowID`, invoked for every incoming trigger request: [3](#0-2) 

This is invoked from `HandleUserTriggerRequest` → `resolveWorkflowID`, called after only `validatedTriggerRequest`/`validateWorkflowID`/`validateWorkflowOwner`, i.e., **before** authentication/authorization (`authorizeRequest`) is performed: [4](#0-3) 

The entry point is the gateway's public JSON-RPC request path (`gateway.ProcessRequest` → handler dispatch → `gatewayHandler.HandleJSONRPCUserMessage` → `triggerHandler.HandleUserTriggerRequest`), which is exposed to any external, unauthenticated client hitting the gateway's HTTP endpoint: [5](#0-4) [6](#0-5) 

### Impact Explanation
A single crafted request from an unauthenticated, unprivileged client (no valid workflow-owner signature or auth is required to reach this code, since the crash happens before `authorizeRequest`) can trigger a Go runtime panic in `strings.Repeat`. Whether this crashes the whole gateway process depends on whether the panic is recovered somewhere up the call stack (no such `recover()` was found in the gateway/handlers/capabilities/v2 package during this analysis). If unrecovered, this is a remote, unauthenticated denial-of-service against the gateway node, analogous to the Frontier MODEXP underflow causing "a node crash" — here on a production build, not merely a debug-only crash, since the panic path does not depend on debug-assertions.

### Likelihood Explanation
High likelihood: any unauthenticated caller can submit a `workflows.execute`-style HTTP trigger request with a `workflowID` or `workflowOwner` value that is exactly the maximum length and omits the `"0x"` prefix but is otherwise valid, lowercase hex. No signature/auth is required to reach the vulnerable normalization code, since it executes prior to `authorizeRequest`.

### Recommendation
- In `validateHexInput`, require the `"0x"` prefix explicitly (reject inputs lacking it) and validate the *hex-digit* length against `expectedLength-2`, not the raw input length.
- In `normalizeHex`, guard against `len(hexStr) > expectedHexLength` and return an error (or clamp) instead of calling `strings.Repeat` with a potentially negative count.
- Add a unit test with a `expectedLength`-sized hex string lacking the `"0x"` prefix to cover this edge case.

### Proof of Concept
1. Send a `workflows.execute` JSON-RPC request to the gateway with `params.workflow.workflowOwner` set to a 42-character all-lowercase hex string that does **not** start with `0x` (e.g., `"00"+strings.Repeat("a1", 20)` totaling 42 hex chars, no prefix) and no `workflowID`.
2. `validateWorkflowOwner` → `validateHexInput(workflowOwner, 42)` passes (length ≤ 42, lowercase, valid hex after no-op `TrimPrefix`).
3. `resolveWorkflowID` calls `normalizeHex(workflowOwner, 42)`: `hexStr` length is 42, `expectedHexLength = 40`, `strings.Repeat("0", 40-42)` → `strings.Repeat("0", -2)` → panic.

Note: I could not find a `recover()` guarding this specific request-handling goroutine within `core/services/gateway`, but I did not exhaustively trace every possible top-level HTTP server middleware; if such a middleware exists, the impact would be reduced to a single failed request rather than a process crash, similar to how Frontier's release-build impact was limited to out-of-gas rather than a full crash.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L267-283)
```go
func validateHexInput(input string, expectedLength int) error {
	if input != strings.ToLower(input) {
		return errors.New("must be lowercase")
	}

	if len(input) > expectedLength {
		return fmt.Errorf("hex string too long: expected at most %d characters, got %d", expectedLength, len(input))
	}

	hexStr := strings.TrimPrefix(input, "0x")
	_, err := hex.DecodeString(hexStr)
	if err != nil {
		return errors.New("must be a valid hex string")
	}

	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L334-340)
```go
func normalizeHex(input string, length int) string {
	hexStr := strings.TrimPrefix(input, "0x")
	// length-2 because we'll add "0x" prefix
	expectedHexLength := length - 2
	paddedHex := strings.Repeat("0", expectedHexLength-len(hexStr)) + hexStr
	return "0x" + paddedHex
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L342-366)
```go
func (h *httpTriggerHandler) resolveWorkflowID(ctx context.Context, triggerReq *jsonrpc.Request[gateway_common.HTTPTriggerRequest], requestID string, callback handlers.Callback) (string, error) {
	h.lggr.Debugw("resolving workflow ID", "workflowID", triggerReq.Params.Workflow.WorkflowID, "workflowOwner", triggerReq.Params.Workflow.WorkflowOwner, "workflowName", triggerReq.Params.Workflow.WorkflowName, "workflowTag", triggerReq.Params.Workflow.WorkflowTag, "requestID", requestID)
	workflowID := triggerReq.Params.Workflow.WorkflowID
	if workflowID != "" {
		workflowID = normalizeHex(workflowID, workflowIDLength)
		_, found := h.workflowMetadataHandler.GetWorkflowReference(workflowID)
		if !found {
			h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, fmt.Sprintf("Workflow not found. 'workflowID' %s is not a valid workflow ID", workflowID), callback)
			return "", errors.New("workflow not found")
		}
		return workflowID, nil
	}
	workflowOwner := normalizeHex(triggerReq.Params.Workflow.WorkflowOwner, workflowOwnerLength)
	workflowName := "0x" + hex.EncodeToString([]byte(workflows.HashTruncateName(triggerReq.Params.Workflow.WorkflowName)))
	workflowID, found := h.workflowMetadataHandler.GetWorkflowID(
		workflowOwner,
		workflowName,
		triggerReq.Params.Workflow.WorkflowTag,
	)
	if !found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "Workflow not found. Provide either a valid 'workflowID' or a valid combination of 'workflowOwner', 'workflowName', and 'workflowTag'", callback)
		return "", errors.New("workflow not found")
	}
	return workflowID, nil
}
```

**File:** core/services/gateway/gateway.go (L220-266)
```go
// Called by the server
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
	} else {
		// Legacy request with DON ID - validate and fetch handler
		isLegacyRequest = true
		if err = msg.Validate(); err != nil {
			return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
		}
		handlerKey = msg.Body.DonID
		var ok bool
		h, ok = g.handlers[handlerKey]
		if !ok {
			return newError(jsonRequest.ID, api.UnsupportedDONIdError, "Unsupported DON ID: "+handlerKey)
		}
	}

```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L392-402)
```go
func (h *gatewayHandler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback handlers.Callback) error {
	h.metrics.IncrementTriggerRequestCount(ctx, h.lggr)
	err := h.triggerHandler.HandleUserTriggerRequest(ctx, &req, callback, time.Now())
	if err != nil {
		h.lggr.Errorw("failed to handle user trigger request", "requestID",
			req.ID, "err", err)
		// error response is sent to the response channel by the trigger handler
		// so return nil after logging
	}
	return nil
}
```
