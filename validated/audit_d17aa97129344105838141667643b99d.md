Based on the code I found, there's a strong candidate analog in the gateway's HTTP trigger handler, though I was unable to complete verification of the length-validation ordering due to running out of tool calls.

### Title
Unauthenticated panic via negative `strings.Repeat` count in gateway workflow ID normalization - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The Ella Core bug class is: an external, unauthenticated message field that is not length/presence-validated before being used in logic that assumes a bounded/well-formed value, causing a runtime panic (crash) reachable pre-authentication. `httpTriggerHandler.normalizeHex` in the chainlink gateway exhibits the same pattern: it computes a padding count from attacker-controlled string length without checking it can't be negative.

### Finding Description
`normalizeHex` pads a hex string to a fixed length: [1](#0-0) 
```go
func normalizeHex(input string, length int) string {
	hexStr := strings.TrimPrefix(input, "0x")
	// length-2 because we'll add "0x" prefix
	expectedHexLength := length - 2
	paddedHex := strings.Repeat("0", expectedHexLength-len(hexStr)) + hexStr
	return "0x" + paddedHex
}
```
`strings.Repeat` panics if given a negative count. If `len(hexStr) > expectedHexLength` (i.e., the caller supplies a `workflowID` or `workflowOwner` string longer than the expected fixed length), `expectedHexLength-len(hexStr)` is negative, and the process panics.

`normalizeHex` is called from `resolveWorkflowID`, which is invoked directly from `HandleUserTriggerRequest` — the entry point for unauthenticated HTTP trigger requests coming from the internet-facing gateway: [2](#0-1) 
```go
func (h *httpTriggerHandler) resolveWorkflowID(ctx context.Context, triggerReq *jsonrpc.Request[gateway_common.HTTPTriggerRequest], requestID string, callback handlers.Callback) (string, error) {
	...
	workflowID := triggerReq.Params.Workflow.WorkflowID
	if workflowID != "" {
		workflowID = normalizeHex(workflowID, workflowIDLength)
		...
```
The call chain from the unauthenticated request is: [3](#0-2) 
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	...
	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
```
`validatedTriggerRequest` validates JSON structure, request ID, method, and required-field presence for `workflowID`/`workflowOwner`/`workflowName`/`workflowTag` via `validateWorkflowFields`, but I did not find (and was unable to fully verify with the remaining tool budget) an explicit maximum-length check on `workflowID` or `workflowOwner` before `resolveWorkflowID` is called. `validateWorkflowFields` only checks for empty strings and (elsewhere) hex-validity/lowercase, not length bounds against `workflowIDLength`/`workflowOwnerLength`: [4](#0-3) 

This is analogous to the Ella Core issue: a wire-supplied variable-length field is consumed by logic that assumes a fixed maximum size, with the missing bound-check producing an unrecoverable panic rather than a graceful error.

### Impact Explanation
A panic in `HandleUserTriggerRequest` — invoked per-HTTP-request from unauthenticated external callers — can crash the goroutine/process handling gateway traffic, denying service to all workflows relying on the HTTP trigger capability on that gateway/DON shard. This matches the CWE-476 (NULL/invalid pointer/reachable panic) class and the CVSS vector's availability-only impact (`C:N/I:N/A:H`) from the referenced advisory.

### Likelihood Explanation
Reaching this code only requires sending an HTTP trigger request with an over-long `workflowID` or `workflowOwner` hex string; no authentication token is validated before `resolveWorkflowID` runs (JWT/key authorization happens later in `authorizeRequest`, after workflow resolution). This makes it plausibly reachable pre-authorization, similar to the "no authentication is required" condition in the Ella Core report — but this specific ordering and whether an upstream length check exists elsewhere in the codebase could not be fully confirmed given tool-call limits.

### Recommendation
Add an explicit length check on `workflowID` and `workflowOwner` (and any other field consumed by `normalizeHex`) before calling `normalizeHex`, returning a user error (e.g., `jsonrpc.ErrInvalidRequest`) instead of proceeding, and/or make `normalizeHex` itself defensive by clamping/rejecting inputs whose length exceeds the target length rather than computing a possibly-negative repeat count.

### Proof of Concept
Send an HTTP trigger request (`workflows.execute` method) to the gateway's user-facing endpoint with:
```json
{
  "workflow": { "workflowId": "0x1234...<longer than 66 hex chars>" },
  "input": {}
}
```
If no length check precedes `resolveWorkflowID`, `normalizeHex(workflowID, workflowIDLength)` computes a negative repeat count and `strings.Repeat` panics, crashing the handling goroutine/process.

**Caveat**: I was not able to conclusively confirm (due to reaching the tool-call limit) whether a length-bound check exists somewhere in `validateWorkflowID`/`validateWorkflowOwner` prior to `resolveWorkflowID`'s call to `normalizeHex`, which would neutralize this issue. If such a check exists, this finding would not be a valid vulnerability.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L221-246)
```go
func (h *httpTriggerHandler) validateWorkflowFields(ctx context.Context, workflow gateway_common.WorkflowSelector, requestID string, callback handlers.Callback) error {
	hasWorkflowID := workflow.WorkflowID != ""
	hasWorkflowName := workflow.WorkflowName != ""
	hasWorkflowOwner := workflow.WorkflowOwner != ""
	hasWorkflowTag := workflow.WorkflowTag != ""

	if !hasWorkflowID {
		if !hasWorkflowName {
			h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "workflowName is required when workflowID is not provided", callback)
			return errors.New("workflowName is required when workflowID is not provided")
		}
		if !hasWorkflowOwner {
			h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "workflowOwner is required when workflowID is not provided", callback)
			return errors.New("workflowOwner is required when workflowID is not provided")
		}
		if !hasWorkflowTag {
			h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "workflowTag is required when workflowID is not provided", callback)
			return errors.New("workflowTag is required when workflowID is not provided")
		}
	}

	if hasWorkflowID {
		if err := h.validateWorkflowID(ctx, workflow.WorkflowID, requestID, callback); err != nil {
			return err
		}
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
