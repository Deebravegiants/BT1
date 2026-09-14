### Title
Unauthenticated workflow-existence disclosure via distinct "workflow not found" vs "signer not authorized" errors in the HTTP Trigger gateway handler - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The gateway's HTTP trigger authorization path returns two different, attacker-observable error strings depending on whether a target `workflowID` is registered at all, versus whether it is registered but the caller's key is simply not authorized for it. Any client can self-sign a JWT with any keypair they control and probe arbitrary `workflowID`/owner+name+tag selectors; the response text reveals whether a given (potentially private/secret) workflow exists on the DON, even though the requester has no legitimate relationship to that workflow.

### Finding Description
`WorkflowMetadataHandler.Authorize` looks up `workflowID` in `h.authorizedKeys`. If the workflow is unknown it returns:
`fmt.Errorf("workflow ID %s not found", workflowID)` [1](#0-0) 

If the workflow exists but the caller's signer key is not one of its authorized keys, it returns a *different* message:
`fmt.Errorf("signer '%s' is not authorized for workflow '%s'. Ensure that the signer is registered in the workflow definition", signer.Hex(), workflowID)` [2](#0-1) 

`httpTriggerHandler.authorizeRequest` propagates this distinguishing error text verbatim to the calling client via the JSON-RPC error response:
```go
key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
if err != nil {
    h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
    return nil, errors.Join(errors.New("auth failure"), err)
}
``` [3](#0-2) 

Crucially, reaching this authorize step requires no pre-existing relationship with the target workflow. `HandleUserTriggerRequest` only validates the request shape and resolves the `workflowID` (either directly, or by hashing an owner+name+tag selector) before calling `authorizeRequest` with a JWT the attacker signs themselves: [4](#0-3)  Field validation only checks hex format/length of `workflowID`/`workflowOwner`, not ownership: [5](#0-4) 

This is structurally the same bug class as the Discourse advisory: a completely unprivileged actor can distinguish "resource exists but I can't access it" from "resource does not exist" through a response produced for an unauthenticated/unauthorized probe, disclosing the existence of something (here, a registered workflow and its ID/owner/name/tag mapping) that should not be revealed to arbitrary callers.

### Impact Explanation
An external, unauthenticated attacker can enumerate which `workflowID`s (or owner/name/tag combinations) are registered on a DON's gateway simply by observing whether the error is "workflow ID not found" or "signer is not authorized for workflow." This leaks:
- Existence of specific workflows belonging to other users/orgs.
- Confirmation of guessed/brute-forced owner+name+tag combinations (workflow names/tags are not secret-strength, so this materially aids reconnaissance).
This is an information-disclosure vulnerability (medium severity, consistent with the CVE analog) rather than direct fund loss or full auth bypass, but it does expose workflow topology to unauthorized parties and undermines the confidentiality assumption that unregistered signers should learn nothing about a workflow's presence.

### Likelihood Explanation
High likelihood of exploitability: no privileged credentials are required — an attacker only needs to generate an arbitrary ECDSA keypair, sign a well-formed request-JWT (self-signed, not needing to be "authorized"), and submit HTTP trigger requests with candidate `workflowID`s or owner/name/tag guesses to the public gateway endpoint. The distinguishing error text is returned directly in the JSON-RPC response.

### Recommendation
Return a single, generic authorization-failure message (e.g., "Auth failure: not authorized") for both the "workflow not found" and "signer not authorized" cases in `WorkflowMetadataHandler.Authorize`, and only log the detailed distinction server-side. Ensure `httpTriggerHandler.authorizeRequest` does not forward internal error detail (`err.Error()`) to the client in a way that discloses which branch was taken.

### Proof of Concept
1. Generate a local ECDSA keypair (attacker-controlled, unrelated to any workflow).
2. Craft an `HTTPTriggerRequest` with a guessed `Workflow.WorkflowID` (or owner+name+tag) belonging to a target you do not control.
3. Sign the JSON-RPC request with `utils.CreateRequestJWT` using the attacker's own key (as done in test helpers) and send it to the gateway's `workflows.execute` endpoint.
4. Observe the JSON-RPC error message:
   - `"Auth failure: workflow ID <id> not found"` → workflow does not exist.
   - `"Auth failure: signer '<addr>' is not authorized for workflow '<id>'..."` → workflow exists.
5. Repeat with different candidate IDs/owners/names/tags to enumerate existing workflows without any authorization. [6](#0-5) [3](#0-2)

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-108)
```go
func (h *WorkflowMetadataHandler) Authorize(workflowID string, token string, req *jsonrpc.Request[json.RawMessage]) (*gateway.AuthorizedKey, error) {
	claims, signer, err := utils.VerifyRequestJWT(token, *req)
	if err != nil {
		h.lggr.Errorw("Failed to verify JWT", "error", err)
		return nil, err
	}

	if h.jwtCache.isReplay(claims.ID) {
		h.lggr.Warnw("JWT token has already been used", "workflowID", workflowID, "signer", signer.Hex(), "jti", claims.ID)
		return nil, errors.New("JWT token has already been used. Please generate a new one with new id (jti)")
	}

	keys, exists := h.authorizedKeys[workflowID]
	if !exists {
		h.lggr.Errorw("Workflow ID not found in authorized keys", "workflowID", workflowID)
		return nil, fmt.Errorf("workflow ID %s not found", workflowID)
	}
	key := gateway.AuthorizedKey{
		KeyType:   gateway.KeyTypeECDSAEVM,
		PublicKey: strings.ToLower(signer.Hex()),
	}
	if _, exists = keys[key]; !exists {
		h.lggr.Errorw("Signer not found in authorized keys", "signer", signer.Hex())
		return nil, fmt.Errorf("signer '%s' is not authorized for workflow '%s'. Ensure that the signer is registered in the workflow definition", signer.Hex(), workflowID)
	}
	h.jwtCache.recordUsage(claims.ID)

	return &key, nil
}
```

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L221-265)
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
	if hasWorkflowOwner {
		if err := h.validateWorkflowOwner(ctx, workflow.WorkflowOwner, requestID, callback); err != nil {
			return err
		}
	}
	if hasWorkflowName {
		if err := h.validateWorkflowName(ctx, workflow.WorkflowName, requestID, callback); err != nil {
			return err
		}
	}

	if workflow.WorkflowTag != "" {
		if err := h.validateWorkflowTag(ctx, workflow.WorkflowTag, requestID, callback); err != nil {
			return err
		}
	}

	return nil
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
