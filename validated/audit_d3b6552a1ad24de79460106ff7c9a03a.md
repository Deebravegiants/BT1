### Title
Unauthenticated remote crash (panic) in HTTP trigger gateway workflow-ID resolution via negative `strings.Repeat` count - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
`normalizeHex` in the gateway's HTTP trigger handler can be called with a hex identifier whose trimmed length exceeds the target length, causing `strings.Repeat` to be invoked with a negative count, which panics. This is reachable pre-authentication from any unauthenticated user request that reaches `HandleUserTriggerRequest`, mirroring the CVE-2020-10967 bug class: a malformed-but-format-valid field (empty/short local part in Dovecot vs. a same-length-but-unprefixed hex string here) that passes the "cheap" validation step but crashes the deeper processing logic, causing a remote unauthenticated DoS.

### Finding Description
User-supplied `workflowID`/`workflowOwner` fields go through `validateHexInput` ( [1](#0-0) ), which only enforces: lowercase, `len(input) <= expectedLength`, and that the string (after optionally trimming a `0x` prefix) decodes as hex. Critically, the `0x` prefix is **not required** — an input consisting purely of hex digits (no `0x`) of the maximum allowed length passes this check, because `hex.DecodeString` only needs an even-length string.

That same unprefixed, max-length string is then passed to `normalizeHex`: [2](#0-1) 

`normalizeHex` strips a `0x` prefix that isn't there, so `hexStr` retains its full length (e.g. 42 chars for `workflowOwnerLength`, or 66 for `workflowIDLength`), while `expectedHexLength` is `length-2` (40 or 64). `strings.Repeat("0", expectedHexLength-len(hexStr))` then receives a **negative** count (`40-42 = -2`), which panics at runtime (`strings: negative Repeat count`).

This is called from `resolveWorkflowID`: [3](#0-2) 

which is invoked from `HandleUserTriggerRequest` **before** `authorizeRequest`: [4](#0-3) 

meaning the panic is reachable by any caller before any authentication/authorization check runs — an exact unprivileged-actor analog to the Dovecot crash-before-auth pattern in the CVE.

### Impact Explanation
A panic in this code path (invoked synchronously from the per-request handling goroutine) will crash the goroutine handling the request; if not recovered by an outer wrapper, it can bring down the gateway process, denying service to all DONs/users routed through that gateway node — matching the CVSS 3.1 `A:L` (availability-only) impact of the original CVE. I could not confirm within index limits whether `HandleJSONRPCUserMessage`/the gateway's request dispatch loop wraps handler calls in a `recover()`; this should be verified, as it changes the blast radius from "single failed request" to "full process crash."

### Likelihood Explanation
High: this requires only a single unauthenticated JSON-RPC request with a `workflowOwner` or `workflowID` value that is exactly the maximum allowed length and lacks the `0x` prefix (e.g., 42 lowercase hex characters for owner, 66 for ID) — no valid credentials, signature, or prior state are needed since the crash occurs before `authorizeRequest`.

### Recommendation
- In `validateHexInput`, require inputs to always start with `0x` (or normalize/strip the prefix consistently before length validation), and validate the length of the value *after* stripping the prefix — comparing against `expectedLength-2` hex characters, not `expectedLength` total characters.
- In `normalizeHex`, guard against negative repeat counts (`if expectedHexLength < len(hexStr) { return error }`) instead of assuming `hexStr` is always shorter than `expectedHexLength`.
- Add a recover()-wrapped boundary around per-request gateway handler invocation if one does not already exist, so a single malformed request cannot crash the whole gateway process.

### Proof of Concept
Send an unauthenticated `workflows.execute` HTTP-trigger JSON-RPC request with:
```json
{
  "jsonrpc": "2.0",
  "id": "req-1",
  "method": "workflows.execute",
  "params": {
    "workflow": {
      "workflowOwner": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa11",
      "workflowName": "test",
      "workflowTag": "test"
    },
    "input": {}
  }
}
```
Use a 42-character all-lowercase-hex `workflowOwner` value with no `0x` prefix (even length, valid hex, exactly `workflowOwnerLength`). `validateHexInput` accepts it; `resolveWorkflowID` → `normalizeHex` then computes `strings.Repeat("0", 40-42)`, panicking the handling goroutine.

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
