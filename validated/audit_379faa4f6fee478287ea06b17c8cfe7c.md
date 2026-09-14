### Title
Unauthenticated panic (DoS) via negative-count `strings.Repeat` in HTTP-trigger workflow ID/owner normalization - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
The gateway's HTTP trigger handler validates `workflowID`/`workflowOwner` hex strings only on their *raw* length before an optional `"0x"` prefix is stripped, then computes a padding width as `expectedHexLength - len(hexStr)` and feeds it directly into `strings.Repeat` without checking for a negative value. An attacker who omits the `"0x"` prefix and supplies a full-length hex string can drive this subtraction negative, causing `strings.Repeat` to panic. This is the same bug class as the LiquidJS report: a width/length value derived from unchecked, attacker-controlled input is forwarded into a padding primitive with no bounds check, but here the failure mode is a panic (crash) rather than unbounded memory growth.

### Finding Description
`validateHexInput` only bounds the total length of the raw input string: [1](#0-0) 

It does **not** require the `"0x"` prefix to be present — `hex.DecodeString` is applied to whatever remains after `TrimPrefix`, so a 66-character (for `workflowID`) or 42-character (for `workflowOwner`) string consisting purely of lowercase hex digits with no `"0x"` prefix passes validation, since it satisfies `len(input) <= expectedLength` and decodes as valid hex.

That same raw string is then passed to `normalizeHex`: [2](#0-1) 

Here, `hexStr := strings.TrimPrefix(input, "0x")` is a no-op when there is no `"0x"` prefix, so `len(hexStr)` equals the full validated length (e.g., 66 for workflowID). `expectedHexLength := length - 2` (64 for workflowID, 40 for workflowOwner) is then compared against `len(hexStr)`: `expectedHexLength - len(hexStr)` evaluates to `64 - 66 = -2`. `strings.Repeat` panics on a negative count (`"strings: negative Repeat count"`), so this call panics.

`normalizeHex` is invoked directly from `resolveWorkflowID`, which is called from `HandleUserTriggerRequest` before any authentication/authorization step (`authorizeRequest` runs after `resolveWorkflowID`): [3](#0-2) [4](#0-3) 

That means the panic is reachable by any unprivileged, unauthenticated client sending a well-formed JSON-RPC `workflows.execute` request to the gateway with a crafted `workflowID` or `workflowOwner` (66 or 42 lowercase hex characters, no `"0x"` prefix) — no valid key, signature, or registered workflow is required to trigger it, since the crash happens before `authorizeRequest`.

### Impact Explanation
A panic thrown from a request-handling code path that lacks a `recover()` wrapper can crash the goroutine/process handling gateway traffic, denying service to all legitimate workflow triggers routed through that gateway node. This matches the report's CWE-400/DoS impact category, though the root cause here is an unguarded negative-length arithmetic feeding a padding primitive rather than unbounded growth. I was not able to confirm from the available index whether the gateway's outer JSON-RPC/HTTP transport wraps request handling in a `recover()` (no `recover()` calls were found under `core/services/gateway/**` except in a test file), so the severity ranges from "single request fails ungracefully" (if some outer layer recovers) up to "gateway process crash" (if not) — this should be verified directly in the gateway server/transport code before treating it as a full process-crash DoS.

### Likelihood Explanation
High likelihood of triggering: the only requirement is a single, unauthenticated HTTP/JSON-RPC POST to the gateway's `workflows.execute` endpoint with a `workflowID` (or `workflowOwner`) field equal to the exact expected length in lowercase hex characters but missing the `"0x"` prefix. No rate limiting, authentication, or prior workflow registration is needed, since the panic occurs in `resolveWorkflowID`/`normalizeHex`, ahead of `authorizeRequest` and `checkRateLimit`.

### Recommendation
1. In `normalizeHex`, guard against a negative repeat count: `if n := expectedHexLength - len(hexStr); n > 0 { paddedHex = strings.Repeat("0", n) + hexStr } else { paddedHex = hexStr }` (or return an error/reject the input if `len(hexStr) > expectedHexLength`).
2. In `validateHexInput`, validate the length of the hex payload *after* stripping the optional `"0x"` prefix, and require the exact expected length (not just "at most"), so oversized or prefix-omitted inputs are rejected before reaching `normalizeHex`.
3. Add a `recover()` wrapper around per-request handling in the gateway's JSON-RPC dispatch path so that any single malformed request cannot crash the whole gateway process, as defense-in-depth against similar future bugs.

### Proof of Concept
Send a `workflows.execute` request to the HTTP trigger gateway endpoint with a `workflowID` of exactly 66 lowercase hex characters and no `"0x"` prefix, e.g.:

```json
{
  "jsonrpc": "2.0",
  "id": "poc-1",
  "method": "workflows.execute",
  "params": {
    "workflow": {
      "workflowID": "abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd"
    },
    "params": {}
  }
}
```

This 66-character string passes `validateHexInput(workflowID, 66)` (length `<=66`, valid lowercase hex), then in `resolveWorkflowID` → `normalizeHex(workflowID, 66)`: `hexStr` remains 66 chars (no `"0x"` to strip), `expectedHexLength = 64`, so `strings.Repeat("0", 64-66)` is called with count `-2`, panicking with `strings: negative Repeat count`. [5](#0-4)

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L333-354)
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
```
