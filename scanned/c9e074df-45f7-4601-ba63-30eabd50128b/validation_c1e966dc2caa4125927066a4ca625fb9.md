Confirmed reachable path: `HandleUserTriggerRequest` → `validatedTriggerRequest` → `validateTriggerParams` → `validateWorkflowFields` → `validateWorkflowID`/`validateHexInput` (validation), then `resolveWorkflowID` → `normalizeHex` (usage), all directly from an unprivileged HTTP trigger request handled by the gateway. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Unvalidated hex-prefix length assumption in `normalizeHex` causes daemon-crashing panic via crafted `workflowID` - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The gateway's HTTP-trigger execution path validates `workflowID` length assuming an optional `"0x"` prefix, but the padding function `normalizeHex` computes the number of zero characters to prepend using a length arithmetic that assumes the `"0x"` prefix is always present. A crafted `workflowID` that passes the length check but omits the `"0x"` prefix, or is truncated after stripping, results in a negative count being passed to `strings.Repeat`, which panics at runtime and crashes the node process — the same bug class as the Incus `TransferManager.UploadAllFiles` slice-bounds panic (unchecked prefix-length assumption before a string operation).

### Finding Description
`validateHexInput` (used by `validateWorkflowID`) only rejects a `workflowID` whose length exceeds `workflowIDLength` (66, i.e. `"0x"` + 64 hex chars); it does not require the `"0x"` prefix to actually be present, nor does it require an exact/minimum length: [4](#0-3) 

A `workflowID` consisting of exactly 66 lowercase hex characters with no `"0x"` prefix passes this check (length ≤ 66, valid hex after `hex.DecodeString`).

Later, `resolveWorkflowID` calls `normalizeHex(workflowID, workflowIDLength)`: [5](#0-4) 

`normalizeHex` strips an optional `"0x"` prefix, then computes `expectedHexLength := length - 2` (64) and calls `strings.Repeat("0", expectedHexLength-len(hexStr))`. Because the input never had a `"0x"` prefix to strip, `hexStr` retains its full 66-character length, making `expectedHexLength-len(hexStr) = 64-66 = -2`. In Go, `strings.Repeat` panics with `"strings: negative Repeat count"` when given a negative count — this is directly analogous to the Incus bug where an unvalidated header length caused a negative slice index and a runtime panic.

This is reachable directly from an unprivileged HTTP trigger client: `HandleUserTriggerRequest` calls `validatedTriggerRequest` (which performs the length-only validation) and then `resolveWorkflowID` (which performs the flawed padding), with no additional gate in between: [1](#0-0) 

### Impact Explanation
A panic inside `normalizeHex`/`strings.Repeat`, if not recovered by an intervening handler/goroutine recover, crashes the gateway's node process, denying the `workflows.execute` HTTP-trigger API to all clients until the process restarts. This matches the Incus CVSS vector (availability impact only, no confidentiality/integrity loss): an unprivileged, unauthenticated-at-this-layer client (any caller able to reach the gateway's user-facing JSON-RPC HTTP trigger endpoint) can repeatedly submit malformed `workflowID` values to keep the service down, causing denial of service of the control-plane/trigger API without affecting already-running workflow executions.

### Likelihood Explanation
Likelihood is high for reachability (no authentication is required to hit `validatedTriggerRequest`/`resolveWorkflowID`— authorization (`authorizeRequest`) happens only after `resolveWorkflowID`), and the crafted input (a 66-char lowercase hex string without `"0x"` prefix) is trivial to construct. The main uncertainty is whether Go's panic is caught by a `recover()` somewhere in the request-handling goroutine (e.g., a generic panic-recovery middleware around `HandleUserTriggerRequest`), which was not confirmed in the code explored; if such recovery exists, impact would be limited to a failed single request rather than a full daemon crash. This should be verified before treating this as a confirmed full-DoS instead of a per-request failure.

### Recommendation
In `normalizeHex`, validate that `len(hexStr) <= expectedHexLength` before calling `strings.Repeat`, returning an error (propagated as a user error) instead of silently padding when the computed pad count would be negative. Additionally, tighten `validateHexInput` to require the `"0x"` prefix explicitly (or normalize/strip it prior to length validation) so the length check and the later padding logic operate on consistent assumptions.

### Proof of Concept
Send an HTTP trigger request (`workflows.execute`) to the gateway with:
```json
{
  "jsonrpc": "2.0",
  "id": "poc-1",
  "method": "workflows.execute",
  "params": {
    "workflow": {
      "workflowID": "00000000000000000000000000000000000000000000000000000000000001"
    },
    "input": {}
  }
}
```
Here `workflowID` is exactly 66 lowercase hex characters with no `"0x"` prefix. It passes `validateHexInput` (length ≤ 66, valid hex), but `normalizeHex` then computes `64 - 66 = -2` and calls `strings.Repeat("0", -2)`, panicking with `strings: negative Repeat count`.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-104)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L267-292)
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

func (h *httpTriggerHandler) validateWorkflowID(ctx context.Context, workflowID, requestID string, callback handlers.Callback) error {
	if err := validateHexInput(workflowID, workflowIDLength); err != nil {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "workflowID "+err.Error(), callback)
		return errors.New("workflowID " + err.Error())
	}

	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L333-352)
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
```
