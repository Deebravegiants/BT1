### Title
Unvalidated hex length in `normalizeHex` causes a negative-count panic (DoS) in the Gateway HTTP trigger handler - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The gateway's `normalizeHex` helper computes a padding count by subtracting the length of an attacker-supplied hex string from an expected fixed length, without checking that the result is non-negative, and passes it directly to `strings.Repeat`. `strings.Repeat` panics when given a negative count in Go. Since this function is invoked on `workflowID` and `workflowOwner` fields taken directly from an unauthenticated/unprivileged HTTP trigger request body, a single malicious request can trigger a panic in the gateway's request-processing path. [1](#0-0) 

### Finding Description
`normalizeHex` is defined as:
```go
func normalizeHex(input string, length int) string {
	hexStr := strings.TrimPrefix(input, "0x")
	// length-2 because we'll add "0x" prefix
	expectedHexLength := length - 2
	paddedHex := strings.Repeat("0", expectedHexLength-len(hexStr)) + hexStr
	return "0x" + paddedHex
}
``` [2](#0-1) 

It is called from `resolveWorkflowID`, which is reached while resolving an HTTP trigger request coming from an external, unprivileged client of the gateway:
```go
workflowID := triggerReq.Params.Workflow.WorkflowID
if workflowID != "" {
    workflowID = normalizeHex(workflowID, workflowIDLength)
    ...
}
workflowOwner := normalizeHex(triggerReq.Params.Workflow.WorkflowOwner, workflowOwnerLength)
``` [3](#0-2) 

`triggerReq.Params.Workflow.WorkflowID` / `WorkflowOwner` are user-supplied strings taken verbatim from the JSON-RPC HTTP trigger request that the gateway (an internet-facing component) accepts from callers. There is no validation that `len(hexStr) <= expectedHexLength` before the subtraction `expectedHexLength-len(hexStr)` is computed and handed to `strings.Repeat`. If the attacker supplies a `workflowID`/`workflowOwner` value whose hex-stripped length exceeds the expected fixed length (`workflowIDLength`/`workflowOwnerLength`), the subtraction becomes negative, and Go's `strings.Repeat` panics with `"strings: negative Repeat count"`.

This mirrors the root cause of the referenced Sherlock report: an unchecked subtraction (`_flow.totalSupply() - _ve.totalSupply()`) that can go negative and abort ("revert") a critical code path when invoked with unfavorable, attacker-influenceable inputs. Here the Go-level equivalent of "revert" is a runtime panic triggered by attacker-controlled length mismatch, occurring in the internet-facing gateway's message-handling path rather than in a periodic on-chain emission function.

### Impact Explanation
A panic raised while handling an inbound HTTP trigger request can disrupt request processing for the gateway. Depending on whether a top-level recovery middleware wraps this specific call path, the effect ranges from failing only the single offending request to crashing the goroutine/process handling gateway traffic for the DON, denying service to all legitimate users routed through that gateway instance — directly analogous to the systemic DoS described in the report (an unprivileged actor blocking a shared, periodically-invoked code path for everyone). I was not able to fully confirm from the available context whether a panic-recovery middleware exists around this specific handler invocation to bound the blast radius to a single request; this should be verified before treating impact as process-wide.

### Likelihood Explanation
This is trivially reachable by any unprivileged/unauthenticated caller of the gateway's HTTP trigger endpoint: they need only submit a `workflowID` or `workflowOwner` value in the request whose hex length exceeds the hardcoded `workflowIDLength`/`workflowOwnerLength` constants. No special role, node identity, or privileged access is required, matching the "unprivileged-actor" scope for the gateway message envelope/handler class.

### Recommendation
In `normalizeHex`, validate that `len(hexStr) <= expectedHexLength` before computing the padding count; return an error (or reject the request as invalid input) instead of calling `strings.Repeat` with a value that can be negative:
```go
func normalizeHex(input string, length int) (string, error) {
    hexStr := strings.TrimPrefix(input, "0x")
    expectedHexLength := length - 2
    if len(hexStr) > expectedHexLength {
        return "", fmt.Errorf("hex value %q exceeds expected length %d", input, expectedHexLength)
    }
    paddedHex := strings.Repeat("0", expectedHexLength-len(hexStr)) + hexStr
    return "0x" + paddedHex, nil
}
```
Propagate the error up through `resolveWorkflowID` as a user input error (e.g. via `handleUserError`) rather than allowing an unchecked call into `strings.Repeat`.

### Proof of Concept
1. Send an HTTP trigger JSON-RPC request to the gateway's workflow-execute/HTTP-action endpoint with `params.workflow.workflowOwner` (or `workflowID`) set to a hex string longer than the expected `workflowOwnerLength`/`workflowIDLength` (e.g., `"0x" + strings.Repeat("ab", 200)`).
2. `resolveWorkflowID` calls `normalizeHex(triggerReq.Params.Workflow.WorkflowOwner, workflowOwnerLength)`.
3. `expectedHexLength - len(hexStr)` evaluates to a negative number.
4. `strings.Repeat("0", negativeNumber)` panics with `"strings: negative Repeat count"`, unwinding the goroutine handling the request (severity depends on presence/absence of a recover wrapper around this call path).

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L342-354)
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
```
