Audit Report

## Title
Unrecovered panic (negative-length `strings.Repeat`) from unvalidated workflow ID/owner format in HTTP trigger handler - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

## Summary
`normalizeHex` computes `expectedHexLength - len(hexStr)` and passes it directly to `strings.Repeat`, which panics on a negative count. `validateHexInput`, the only check performed before `normalizeHex` is called, verifies total length and hex-decodability but never requires the `0x` prefix to be present, so a 66-character (for `workflowID`) or 42-character (for `workflowOwner`) all-hex string without the `0x` prefix passes validation and triggers a panic in `normalizeHex`.

## Finding Description
`normalizeHex` strips an optional `0x` prefix, computes `expectedHexLength := length - 2`, and calls `strings.Repeat("0", expectedHexLength-len(hexStr))`: [1](#0-0) 

The upstream check, `validateHexInput`, only enforces `len(input) > expectedLength` (i.e., no more than `expectedLength` characters) and that `strings.TrimPrefix(input, "0x")` decodes as hex — it never checks that the prefix is actually present: [2](#0-1) 

This is called from `validateWorkflowID`/`validateWorkflowOwner` with `workflowIDLength = 66` and `workflowOwnerLength = 42`: [3](#0-2) [4](#0-3) 

If a client submits a `workflowID` that is exactly 66 lowercase hex characters with no `0x` prefix, `validateHexInput` passes (`len(input)==66`, not `>66`; valid hex). `resolveWorkflowID` then calls `normalizeHex(workflowID, 66)`: [5](#0-4) 
Inside, `TrimPrefix` is a no-op (no `"0x"` present), so `hexStr` stays 66 chars; `expectedHexLength = 66-2 = 64`; `64-66 = -2`; `strings.Repeat("0", -2)` panics with `"strings: negative Repeat count"`. The same logic applies to `workflowOwner` at length 42.

This is reachable pre-authorization: `HandleUserTriggerRequest` calls `validatedTriggerRequest` → `resolveWorkflowID` (which panics) before `authorizeRequest` is ever invoked: [6](#0-5) 
And this handler is invoked synchronously from `HandleJSONRPCUserMessage`, which is called from `gateway.ProcessRequest` on every incoming request: [7](#0-6) [8](#0-7) 

I confirmed there is no panic-recovery wrapper anywhere in the gateway package's request-handling path: a `grep` for `recover()` across the repo shows the gateway package only uses it in `response_cache_test.go` (a test file), and the repo's dedicated panic-recovery helpers (`recovery.WrapRecover`, `recovery.HandleFn`, `recovery.ReportPanics` in `core/recovery/recover.go`) are not referenced anywhere under `core/services/gateway/`. This means the described exploit chain and the absence of recovery are both verified in the code as reviewed. What I could **not** verify within available tools is the exact goroutine/HTTP-server topology that ultimately invokes `ProcessRequest` (i.e., whether `net/http`'s built-in per-connection panic recovery isolates the blast radius to a single request/connection, or whether some other transport mechanism is used that could crash the whole process/gateway service). This detail affects severity classification (single-request DoS vs. full-service crash) but does not affect the validity of the underlying panic bug itself.

## Impact Explanation
This is a genuine, code-confirmed denial-of-service vulnerability: an unauthenticated/unprivileged client can crash the request-handling goroutine processing their own HTTP trigger request (`workflows.execute`) by supplying a purposely malformed but well-formed-looking `workflowID`/`workflowOwner` value. At minimum this causes reliable, repeatable failure of the request path for the attacker's own request; depending on the transport-layer panic-recovery behavior (not fully confirmed), it could escalate to broader service disruption. This maps to the in-scope "service unavailability / severe degradation under realistic attacker input" impact class.

## Likelihood Explanation
High. The vulnerable code path (`validateHexInput` → `normalizeHex`) is reachable by any client able to send a JSON-RPC `workflows.execute` request to the gateway's HTTP trigger endpoint, requires no credentials, no prior authorization, and no special network position. The malicious input (66 or 42 hex characters without the `0x` prefix) is trivial to construct.

## Recommendation
- In `validateHexInput`, explicitly require the `0x` prefix (e.g., `if !strings.HasPrefix(input, "0x") { return error }`) before proceeding to length/hex checks.
- In `normalizeHex`, guard against `expectedHexLength - len(hexStr) < 0` and return an error instead of calling `strings.Repeat` with a potentially negative count.
- Add defense-in-depth panic recovery around per-request handler dispatch in the gateway (e.g., wrap `ProcessRequest`/`HandleJSONRPCUserMessage` with `core/recovery.WrapRecover` or an equivalent `recover()`), so malformed input in any handler cannot propagate into a process-level crash.

## Proof of Concept
Send a JSON-RPC `workflows.execute` request to the gateway's HTTP trigger endpoint with:
```json
{
  "jsonrpc": "2.0",
  "id": "poc",
  "method": "workflows.execute",
  "params": {
    "workflow": {
      "workflowID": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    },
    "input": {}
  }
}
```
where `workflowID` is exactly 66 lowercase hex characters with no `0x` prefix. `validateWorkflowID`/`validateHexInput` accept it (`len==66`, valid hex); `resolveWorkflowID` calls `normalizeHex(workflowID, 66)`, which panics on `strings.Repeat("0", -2)`. Equivalent Go unit test: call `normalizeHex(strings.Repeat("a", 66), 66)` directly and observe the panic, or call `httpTriggerHandler.HandleUserTriggerRequest` with the crafted JSON-RPC request above and observe the goroutine panic.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L34-41)
```go
const (
	// Reference: https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.8/workflow/dev/v2/WorkflowRegistry.sol
	workflowIDLength       = 66 // 0x + 64 hex characters = 32 bytes
	workflowOwnerLength    = 42 // 0x + 40 hex characters = 20 bytes
	maxWorkflowNameLength  = 64 // Maximum workflow name length
	WorkflowNameHashLength = 22 // 0x + 20 hex characters = 10 bytes
	maxWorkflowTagLength   = 32 // Maximum workflow tag length
)
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-109)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L285-301)
```go
func (h *httpTriggerHandler) validateWorkflowID(ctx context.Context, workflowID, requestID string, callback handlers.Callback) error {
	if err := validateHexInput(workflowID, workflowIDLength); err != nil {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "workflowID "+err.Error(), callback)
		return errors.New("workflowID " + err.Error())
	}

	return nil
}

func (h *httpTriggerHandler) validateWorkflowOwner(ctx context.Context, workflowOwner, requestID string, callback handlers.Callback) error {
	if err := validateHexInput(workflowOwner, workflowOwnerLength); err != nil {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "workflowOwner "+err.Error(), callback)
		return errors.New("workflowOwner " + err.Error())
	}

	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L333-340)
```go
// normalizeHex normalizes a hex string by stripping 0x prefix, padding with leading zeros, and adding 0x prefix back
func normalizeHex(input string, length int) string {
	hexStr := strings.TrimPrefix(input, "0x")
	// length-2 because we'll add "0x" prefix
	expectedHexLength := length - 2
	paddedHex := strings.Repeat("0", expectedHexLength-len(hexStr)) + hexStr
	return "0x" + paddedHex
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L342-353)
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

**File:** core/services/gateway/gateway.go (L270-279)
```go
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
	}
```
