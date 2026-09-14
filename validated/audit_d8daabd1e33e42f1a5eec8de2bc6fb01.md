### Title
Unrecovered panic (negative `strings.Repeat` count) in HTTP trigger `workflowID` normalization causes gateway DoS - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
The FreeImage CVE is a buffer-overflow rooted in trusting an attacker-controlled length/index field without validating it against the actual buffer size before a write. The closest reachable analog in this Go codebase is not memory corruption (Go's runtime prevents that class of bug) but the same root-cause pattern — an unvalidated, attacker-controlled length is used to compute a fill/copy count without checking that the count is non-negative — which triggers a runtime panic (`strings: negative Repeat count`) instead of writing out of bounds. This is reachable directly from an unauthenticated/unprivileged HTTP trigger request to the internet-facing capabilities gateway, before authorization is performed.

### Finding Description
`validateHexInput` only rejects hex strings that are **longer** than `expectedLength`, it never enforces the "0x"-prefixed canonical shape: [1](#0-0) 

`validateWorkflowID` calls `validateHexInput(workflowID, workflowIDLength)` (66) as part of `validateWorkflowFields`, which runs inside `validatedTriggerRequest` — i.e., before `resolveWorkflowID`/`authorizeRequest` are ever invoked: [2](#0-1) [3](#0-2) 

If a client supplies a `workflowID` that is exactly 66 lowercase hex characters **without** the `0x` prefix (e.g., 66 `'0'` characters), it passes `validateHexInput` (length check is `> expectedLength`, so `== 66` passes; `hex.DecodeString` on 66 hex chars succeeds since `TrimPrefix` is a no-op when there's no `0x`). Execution then reaches `resolveWorkflowID`, which calls `normalizeHex(workflowID, workflowIDLength)`: [4](#0-3) 

`normalizeHex` computes `expectedHexLength := length - 2` (64) and then `strings.Repeat("0", expectedHexLength-len(hexStr))`. Since `hexStr` here is 66 characters (no `0x` was present to strip) and `expectedHexLength` is 64, the repeat count is `64 - 66 = -2`, which makes `strings.Repeat` panic with `"strings: Repeat count negative"`.

No panic-recovery middleware was found wrapping this request path (`core/services/gateway/network/httpserver.go` and the user-message dispatch in `core/services/gateway/gateway.go` / `http_handler.go` contain no `recover()`), meaning this panic is very likely to escape the request goroutine and crash the Gateway process (or at minimum the goroutine servicing that request without a recovered error response), denying service to all other workflows and nodes relying on that gateway instance.

### Impact Explanation
An unprivileged, unauthenticated caller of the gateway's `workflows.execute` HTTP trigger endpoint can crash the internet-facing Gateway service with a single crafted request, before any authorization/allowlist check occurs (`authorizeRequest` runs after `resolveWorkflowID`). This is a availability-impacting bug reachable pre-auth from the public API surface, analogous in mechanism (unchecked length-derived count feeding a low-level buffer/fill primitive) to the referenced CVE's `_assignPixel<>()` overflow, though the consequence in Go is a panic/crash (DoS) rather than arbitrary code execution.

### Likelihood Explanation
High — triggering requires only a single, trivially crafted JSON-RPC `workflows.execute` request with a `workflowID` field of exactly 66 lowercase hex characters lacking the `0x` prefix. No authentication, allowlisting, or special network position is required, since the panic occurs in the validation/resolution pipeline that precedes `authorizeRequest`.

### Recommendation
- In `validateHexInput`, require the canonical `0x`-prefixed form (reject inputs without the `0x` prefix, or reject inputs whose length doesn't match exactly `expectedLength` after normalization).
- In `normalizeHex`, guard against `expectedHexLength - len(hexStr)` being negative (return an error / reject the input) instead of assuming the trimmed string is always shorter than the target length.
- Add panic recovery around the gateway's per-request handling path (`ProcessRequest` / `HandleJSONRPCUserMessage` dispatch) so that a bug in a single handler cannot crash the whole Gateway service.

### Proof of Concept
Send an unauthenticated JSON-RPC request to the gateway's HTTP trigger endpoint:
```json
{
  "jsonrpc": "2.0",
  "id": "poc-1",
  "method": "workflows.execute",
  "params": {
    "input": {},
    "workflow": {
      "workflowID": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  }
}
```
Note: the `workflowID` value is 66 lowercase `'0'` characters (matching `workflowIDLength = 66`) with **no** `0x` prefix. This passes `validateHexInput` (length not `>` 66) and reaches `normalizeHex("000...0" (66 chars), 66)`, computing `strings.Repeat("0", 64-66)`, which panics with `strings: negative Repeat count`, crashing the handling goroutine/process since no recovery is present in the request path. [5](#0-4)

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L285-292)
```go
func (h *httpTriggerHandler) validateWorkflowID(ctx context.Context, workflowID, requestID string, callback handlers.Callback) error {
	if err := validateHexInput(workflowID, workflowIDLength); err != nil {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "workflowID "+err.Error(), callback)
		return errors.New("workflowID " + err.Error())
	}

	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L333-366)
```go
// normalizeHex normalizes a hex string by stripping 0x prefix, padding with leading zeros, and adding 0x prefix back
func normalizeHex(input string, length int) string {
	hexStr := strings.TrimPrefix(input, "0x")
	// length-2 because we'll add "0x" prefix
	expectedHexLength := length - 2
	paddedHex := strings.Repeat("0", expectedHexLength-len(hexStr)) + hexStr
	return "0x" + paddedHex
}

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
