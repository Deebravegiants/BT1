## Analog Found

The Argo CD bug (fetch-before-authorize → distinguishable error messages) has a direct analog in the CRE Gateway's HTTP trigger handler.

### Title
Unauthenticated workflow existence enumeration via distinguishable error messages in HTTP trigger handler - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
`HandleUserTriggerRequest` resolves a workflow's existence (`resolveWorkflowID`) **before** verifying the caller's cryptographic authorization (`authorizeRequest`). Because the two failure paths produce distinguishable JSON-RPC error messages ("workflow not found" vs. "Auth failure: ..."), any network caller to the gateway's internet-facing HTTP trigger endpoint can enumerate valid `workflowID` values or valid `(workflowOwner, workflowName, workflowTag)` tuples without presenting any valid signature/credential.

### Finding Description
`HandleUserTriggerRequest` executes these steps in order:
1. `validatedTriggerRequest` — parses/validates request shape only (no auth check).
2. `resolveWorkflowID` — looks up the workflow by ID or by owner/name/tag against `h.workflowMetadataHandler`, and returns a specific `"workflow not found"` error if the lookup fails.
3. `authorizeRequest` — only now verifies the request's signed JWT/authorization key against the workflow's authorized keys, returning `"Auth failure: ..."` on failure. [1](#0-0) 

The lookup step itself does not require any valid authentication — it happens purely on attacker-supplied `workflowID`/`workflowOwner`/`workflowName`/`workflowTag` fields: [2](#0-1) 

Because step 2 runs before step 3, an attacker who submits a syntactically valid but nonexistent workflow reference receives `"Workflow not found..."`, while an attacker who submits an existing workflow reference (guessed or brute-forced owner/name/tag or ID) proceeds to the authorization stage and instead receives `"Auth failure: ..."` (as also confirmed by the regression test expecting these two distinct messages) [3](#0-2) . This mirrors the Argo CD bug class exactly: the resource is fetched/looked up prior to the access-control decision, and the two failure modes are distinguishable to an untrusted caller.

### Impact Explanation
An unauthenticated party interacting with the internet-facing CRE Gateway HTTP trigger endpoint can enumerate:
- Valid `workflowID` values (by brute-forcing/guessing 32-byte hex IDs and observing which return "not found" vs proceed to auth failure), and
- Valid `(workflowOwner, workflowName, workflowTag)` combinations for a given owner address.

This discloses which workflows exist for a given owner, which — as in the Argo CD advisory — can be used as reconnaissance for follow-on social-engineering or targeted attacks (e.g., knowing a workflow name/owner exists to craft a more convincing phishing/authorization-key-planting attempt), and reveals operational metadata that should not be exposed to unauthenticated network callers.

### Likelihood Explanation
The HTTP trigger handler is explicitly designed to be reachable over the network without prior authentication (auth is verified via a request-embedded JWT, not a session or network-level gate), and the ordering bug requires no special conditions — any client with network access to the gateway's HTTP trigger listener can trigger it deterministically for every guessed identifier.

### Recommendation
Reorder the checks so that authorization/authentication failure and "not found" are collapsed into a single indistinguishable error response, or perform the authorization check (or at least basic request authentication) before revealing whether the referenced workflow exists — analogous to the Argo CD patch that unified "not found" and "unauthorized" into a single response for the affected API paths.

### Proof of Concept
1. Send a JSON-RPC `workflows.execute` request to the gateway's HTTP trigger endpoint with a guessed `workflowOwner`/`workflowName`/`workflowTag` (or raw `workflowID`) and an arbitrary/invalid `Auth` JWT.
2. Observe the response:
   - `"Workflow not found. Provide either a valid 'workflowID' or a valid combination of 'workflowOwner', 'workflowName', and 'workflowTag'"` → the tuple/ID does not correspond to a deployed workflow.
   - `"Auth failure: ..."` → the tuple/ID does correspond to a deployed workflow, but the supplied key is not authorized.
3. Repeat with different owner/name/tag guesses to enumerate which workflows are deployed for a given owner, with zero valid credentials required. [4](#0-3)

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-376)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
}
```

**File:** system-tests/tests/regression/cre/http_trigger_regression_test.go (L225-244)
```go
			if response.Error != nil {
				errorMsg := response.Error.Message
				testLogger.Info().Msgf("Received error in JSON-RPC response: %v", errorMsg)

				// Check if this is an auth failure (expected)
				if strings.Contains(errorMsg, "Auth failure") {
					testLogger.Info().Msg("Authorization properly rejected at gateway level")
					authFailureDetected = true
					return true
				}

				// If it's "workflow not found", continue retrying (workflow not loaded yet)
				if errorMsg == "workflow not found" {
					testLogger.Info().Msg("Workflow not found yet, retrying...")
					return false
				}

				// Any other error is unexpected for this test
				testLogger.Warn().Msgf("Unexpected error received: %v", errorMsg)
				return false
```
