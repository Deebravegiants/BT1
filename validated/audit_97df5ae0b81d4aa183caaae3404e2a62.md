## Analysis: Lax Hex-Length Validation Silently Left-Pads Short `workflowOwner`/`workflowID` in HTTP Trigger Handler

### Title
Silent Zero-Padding of Short `workflowOwner`/`workflowID` Inputs Allows Cross-Owner Workflow Trigger Confusion - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The gateway's HTTP trigger handler validates `workflowOwner` and `workflowID` inputs from unprivileged external callers with `validateHexInput`, which only rejects inputs *longer* than the expected length — it never enforces the *exact* length. After this lax check passes, `normalizeHex` silently left-pads the value with zeros to reach the expected length before it is used to resolve a workflow. This is the exact bug class described in the external report: a caller-supplied address/ID that is too short is silently zero-padded into a full-length value, which can resolve to a different, unintended workflow/owner without any indication to the caller.

### Finding Description
`validateHexInput` only checks the lowercase requirement, an upper bound on length, and hex-decodability — it never checks that the input equals `expectedLength`: [1](#0-0) 

This is invoked by `validateWorkflowOwner`/`validateWorkflowID`, which are the only structural checks performed on these fields before resolution: [2](#0-1) 

Once validation passes, `resolveWorkflowID` calls `normalizeHex`, which strips the `0x` prefix and left-pads with zeros up to the expected length, then re-adds `0x` — silently transforming a too-short caller-supplied owner/ID into a completely different, full-length value used to look up a workflow: [3](#0-2) 

For example, a caller intending to target `workflowOwner = "0xdeadbeef"` (a short/malformed value, e.g. due to truncation, a client bug, or a typo) passes `validateHexInput` because `len("0xdeadbeef") = 10 <= 42`, and is then silently rewritten by `normalizeHex` to `0x00000000000000000000000000000000deadbeef`. If that zero-padded value happens to match a real, registered workflow owner in `workflowMetadataHandler.GetWorkflowID`, the request is resolved against that other owner's workflow — a value the original caller never entered and cannot recognize from their own truncated input.

### Impact Explanation
This directly matches the reported bug class: a caller cannot tell from their own (short) input that it will be silently coerced into a materially different, full-length identifier. In the gateway `HandleUserTriggerRequest` flow, this coerced `workflowOwner`/`workflowID` is used to resolve `workflowID` (`resolveWorkflowID`), which subsequently drives authorization (`authorizeRequest`), rate limiting (`checkRateLimit`), and shard dispatch (`sendWithRetries`) — i.e., the padded value becomes the real target of the trigger request: [4](#0-3) 

While actual capability authorization (`Authorize`) still gates execution, the confusion occurs *before* authorization: a caller who intends to reference their own (mistyped, too-short) owner/ID can be silently redirected to attempt actions against a different party's workflow reference, producing misleading error/success behavior and log entries that reference the wrong owner — the same "acting on the wrong address without recognizing it" risk flagged in the source report, applied to workflow owner/ID resolution instead of an on-chain transfer target.

### Likelihood Explanation
Any external, unauthenticated caller of the gateway's HTTP trigger endpoint can trigger this by supplying a `workflowOwner` or `workflowID` shorter than the expected length (10, 20, etc. hex chars instead of 40/64) — no privileged access is required, and the validation gap is on the primary, internet-facing request path (`HandleUserTriggerRequest` → `validatedTriggerRequest` → `resolveWorkflowID`).

### Recommendation
Change `validateHexInput` to enforce the *exact* expected length (reject shorter inputs) rather than only an upper bound, so `normalizeHex` is never reached with a value that requires padding. If canonical shorter representations must be supported, require the caller to submit the value in fully-padded canonical form and reject anything else, consistent with the remediation applied in the reported Starknet Snap fix (wrap the parser with an explicit length check rather than relying on implicit padding).

### Proof of Concept
1. Send an HTTP trigger request to the gateway with `params.workflow.workflowOwner = "0xdeadbeef"` (10 hex chars) and no `workflowID`.
2. `validateWorkflowOwner` → `validateHexInput("0xdeadbeef", 42)` passes because `len("0xdeadbeef") = 10 <= 42` and it is valid lowercase hex.
3. `resolveWorkflowID` calls `normalizeHex("0xdeadbeef", 42)`, producing `"0x00000000000000000000000000000000deadbeef"`.
4. This padded value is passed to `workflowMetadataHandler.GetWorkflowID(workflowOwner, workflowName, workflowTag)`; if it coincidentally (or via crafted probing) matches a real registered owner, the request is authorized/dispatched against that owner's workflow instead of failing with "invalid workflowOwner format."

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-146)
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

	strippedWorkflowID := strings.TrimPrefix(workflowID, "0x")
	legacyExecutionID, err := workflows.EncodeExecutionID(strippedWorkflowID, req.ID) //nolint:staticcheck // legacy ID kept for observability comparison
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID: " + err.Error())
	}
	// Workflows shouldn't use more than one HTTP trigger. If we ever need to support multiple triggers, we'd need to pass
	// trigger index to the Gateway handler and somehow allow senders to pick. For now, we use trigger index 0.
	// Execution IDs here are used only for logging.
	executionIDWithTriggerIndex, err := workflows.GenerateExecutionIDWithTriggerIndex(strippedWorkflowID, req.ID, 0)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID with trigger index: " + err.Error())
	}
	h.lggr.Debugw("processing request",
		"legacyExecutionID", legacyExecutionID,
		"executionIDWithTriggerIndex", executionIDWithTriggerIndex,
		"requestID", req.ID,
		"workflowID", workflowID)

	reqWithKey, err := reqWithAuthorizedKey(triggerReq, *key)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error marshaling trigger request: " + err.Error())
	}

	doneCh, err := h.setupCallback(ctx, req.ID, callback, requestStartTime, workflowID)
	if err != nil {
		return err
	}

	return h.sendWithRetries(ctx, legacyExecutionID, executionIDWithTriggerIndex, reqWithKey, workflowID, doneCh)
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
