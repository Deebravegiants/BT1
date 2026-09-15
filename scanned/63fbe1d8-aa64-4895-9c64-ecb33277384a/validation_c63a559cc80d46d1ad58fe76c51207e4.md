### Title
Unrecovered panic (DoS) via crafted `workflowID` in gateway HTTP trigger handler - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

### Summary
The gpac CVE describes a crash from insufficiently validated input reaching a routine that dereferences data based on an unchecked length/track relationship. The chainlink analog is `normalizeHex`, which computes a padding count from two independently-validated length assumptions and can go negative, causing `strings.Repeat` to panic when given attacker-controlled `workflowID` input from an unprivileged gateway HTTP trigger request.

### Finding Description
`validateWorkflowID` only checks that the raw client-supplied string is `<= workflowIDLength` characters, lowercase, and decodable as hex after stripping an optional `"0x"` prefix: [1](#0-0) 

Crucially, the length bound (`workflowIDLength`, the expected total length including a `"0x"` prefix, e.g. 66 for 32-byte IDs) is checked against the raw `input` string, before any `"0x"` stripping. If the caller submits a `workflowID` **without** the `"0x"` prefix but with the full number of characters (e.g. 66 hex characters with no prefix instead of 64 hex characters plus `"0x"`), the check `len(input) > expectedLength` passes (since `len(input) == expectedLength`), and `hex.DecodeString` succeeds because 66 is an even-length hex string.

The value then flows into `resolveWorkflowID`, which calls `normalizeHex` on the same string: [2](#0-1) 

`normalizeHex` strips any `"0x"` prefix (a no-op here since there is none) and computes:
```
expectedHexLength := length - 2         // e.g. 64
paddedHex := strings.Repeat("0", expectedHexLength-len(hexStr)) + hexStr
```
Since `hexStr` has 66 characters (no prefix was present to strip) and `expectedHexLength` is 64, `expectedHexLength-len(hexStr)` evaluates to `-2`. `strings.Repeat` panics on a negative count: [3](#0-2) 

This mirrors the gpac root cause: a length/identity computed from one unchecked assumption (track/record boundary in gpac; prefix-presence assumption here) is later dereferenced/consumed without re-validation, producing an invalid operation from crafted, low-privilege input.

### Impact Explanation
An unrecovered Go panic in a request-handling goroutine will, absent a top-level `recover()` in the gateway's HTTP request path, crash the serving goroutine and potentially the entire gateway process, denying service to all workflows/nodes routed through that gateway instance — a direct analog to the CVSS `A:H` (availability-only) impact of the reference CVE. This is reachable by any unprivileged client capable of sending a `MethodWorkflowExecute`-style HTTP trigger request to the gateway; no authentication bypass or special privilege is required to reach `resolveWorkflowID` since `workflowID` parsing happens as part of standard request validation prior to authorization-specific checks in this handler chain.

### Likelihood Explanation
High: the only requirement is sending a JSON body with `Workflow.WorkflowID` set to a string of exactly `workflowIDLength` lowercase hex characters lacking the `"0x"` prefix. This is trivially constructed by any external actor without credentials, matching the "unprivileged-actor" and "internet-facing gateway" scope of this analysis.

### Recommendation
- Normalize/validate `workflowID` (and any other identifier passed through `normalizeHex`) using a single, length-agnostic validation pass that operates on the identifier **after** any prefix stripping, not before.
- In `normalizeHex`, guard against a negative pad count (`if expectedHexLength-len(hexStr) < 0 { return error }`) instead of assuming inputs are already conformant.
- Add/verify a top-level panic-recovery middleware around gateway HTTP request handling so a single malformed request cannot take down the process, as defense in depth.

### Proof of Concept
1. Send an HTTP trigger request to the gateway (`MethodWorkflowExecute`) with:
```json
{
  "workflow": { "workflowID": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" },
  "input": {}
}
```
   where the `workflowID` string is exactly `workflowIDLength` (e.g., 66) lowercase hex characters and does **not** start with `"0x"`.
2. `validateWorkflowID` passes (length check treats the raw, unprefixed string as within bounds; hex decode succeeds because the length is even).
3. `resolveWorkflowID` → `normalizeHex(workflowID, workflowIDLength)` computes a negative repeat count and panics, crashing the handling goroutine/process.

Note: I could not directly confirm the exact numeric value of `workflowIDLength` or definitively verify the presence/absence of a top-level panic-recovery wrapper around this handler's HTTP entry point within the indexed content; a Devin session with full repository access would be needed to confirm those two details and validate the exact crash trigger end-to-end.

### Citations

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
