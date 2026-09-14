## Finding

Chainlink's CRE Gateway HTTP-Trigger handler resolves a workflow's existence **before** verifying the caller's authorization (JWT signature/allowlist check), letting an unauthenticated caller enumerate which `workflowID` values (or `workflowOwner`/`workflowName`/`workflowTag` combinations) exist on the gateway.

### Title
Workflow existence enumeration via unauthenticated `resolveWorkflowID` check prior to JWT authorization - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
`httpTriggerHandler.HandleUserTriggerRequest` performs workflow ID/selector resolution and returns a distinct "workflow not found" error *before* it ever validates that the requester holds a signature from an authorized key for that workflow. This ordering allows any network caller reaching this gateway endpoint to enumerate valid `workflowID`s or `workflowOwner`/`workflowName`/`workflowTag` triples they are not authorized to trigger, learning about the existence of protected workflow metadata purely from the response, analogous to the Superset `/explore` datasource enumeration bug (CVE-2025-55675).

### Finding Description
In `HandleUserTriggerRequest`, the call order is: [1](#0-0) 

`resolveWorkflowID` is invoked at line 101, and `authorizeRequest` (which verifies the JWT signature against the workflow's authorized keys, see `WorkflowMetadataHandler.Authorize`) is only invoked afterward at line 106.

`resolveWorkflowID` itself performs a lookup keyed by attacker-supplied `workflowID` or `workflowOwner`+`workflowName`+`workflowTag`, and directly reports whether the workflow exists: [2](#0-1) 

No authentication or authorization of the caller occurs before this lookup — the request body is only parsed/validated for shape (`validatedTriggerRequest`), and the workflow-existence check runs unconditionally. Only after the workflow ID is confirmed to exist does the code proceed to `authorizeRequest`, which validates the JWT and returns a *different* error class ("auth failure") when the signer isn't authorized: [3](#0-2) 

This is the same bug class as the Superset advisory: a missing authorization check on a resource-existence lookup lets an unprivileged caller enumerate protected resource identifiers (here, `workflowID`s and owner/name/tag registrations) and confirm their existence, before/without ever proving authorization to interact with them.

### Impact Explanation
An attacker with network access to the gateway's HTTP trigger endpoint can brute-force or probe `workflowID` values (or owner/name/tag triples) and, from the distinct "Workflow not found" vs. "auth failure" responses, determine which workflows are registered on the DON/shard and which `workflowOwner` addresses have deployed named/tagged workflows — information that should only be available to holders of a signing key authorized for that specific workflow. This is a confidentiality-only information-disclosure issue (workflow existence/metadata), consistent with the CVSS `VC:L` rating of the original advisory; it does not by itself allow triggering, secret disclosure, or fund movement.

### Likelihood Explanation
The gateway's HTTP trigger endpoint is explicitly designed to be internet-facing and to accept unauthenticated requests up to the point of JWT validation (per the handler's own README describing "Inbound requests... JWT-based authentication" as a later step). Because `resolveWorkflowID` runs unconditionally before that JWT check, any unprivileged actor who can reach the gateway can trigger this enumeration with no prerequisites, making likelihood high for the information-disclosure primitive.

### Recommendation
Reorder validation so that workflow-existence disclosure is not distinguishable from authorization failure to an unauthenticated caller — e.g., perform JWT signature verification first (or fold the "not found" and "not authorized" paths into a single generic error/response) so that resolving a workflow ID/selector does not leak existence information independent of the caller's authorization.

### Proof of Concept
1. Send a `workflows.execute` JSON-RPC request to the gateway's HTTP trigger endpoint with a candidate `workflowID` (or `workflowOwner`/`workflowName`/`workflowTag`) and no/invalid `Auth` JWT.
2. Observe the response: if the workflow exists, the handler proceeds past `resolveWorkflowID` and returns an "auth failure" error from `authorizeRequest`; if it does not exist, it returns "Workflow not found" from `resolveWorkflowID` directly.
3. Repeat across a range of IDs/owner-name-tag combinations to enumerate which workflows are registered, without ever presenting a valid signature. [1](#0-0) [2](#0-1)

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-104)
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
```
