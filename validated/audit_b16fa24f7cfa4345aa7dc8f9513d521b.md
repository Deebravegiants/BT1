Audit Report

## Title
Workflow existence oracle reachable before authentication in HTTP Trigger Handler - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

## Summary
`HandleUserTriggerRequest` calls `resolveWorkflowID` before `authorizeRequest`, so the gateway's HTTP trigger JSON-RPC endpoint executes a workflow existence/lookup step against unauthenticated input before any JWT/auth-key verification occurs. This lets an unauthenticated caller submit `workflowID` or `workflowOwner`/`workflowName`/`workflowTag` guesses and distinguish "workflow not found" from "auth failure" responses, enumerating valid workflow identifiers registered on the DON.

## Finding Description
In `HandleUserTriggerRequest`, after only basic payload/field-format validation via `validatedTriggerRequest`, the handler calls `h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)` and only afterward calls `h.authorizeRequest(ctx, workflowID, req, callback)`: [1](#0-0) 

`resolveWorkflowID` looks up the supplied `workflowID` (or `workflowOwner`+`workflowName`+`workflowTag`) against `h.workflowMetadataHandler`'s in-memory maps (populated purely from DON-reported metadata, with no requirement that the caller be authenticated) and returns a distinct "Workflow not found" error when no match exists: [2](#0-1) 

Only if a matching workflow is found does the handler proceed to `authorizeRequest`, which performs the actual JWT verification and per-workflow authorized-key check via `workflowMetadataHandler.Authorize`, returning a distinctly worded "Auth failure" error on failure: [3](#0-2) [4](#0-3) 

The gateway's public entry point (`gateway.ProcessRequest` → `gatewayHandler.HandleJSONRPCUserMessage` → `httpTriggerHandler.HandleUserTriggerRequest`) performs no authentication check ahead of this dispatch; `req.Auth` is only consumed and validated later inside `authorizeRequest`: [5](#0-4) [6](#0-5) 

This confirms the ordering flaw exactly as described: an unauthenticated request can reach the existence-check code path, and the two failure modes ("Workflow not found" vs "Auth failure") are observably different to the caller, as also demonstrated by the existing test suite exercising both paths independently (`TestHttpTriggerHandler_HandleUserTriggerRequest_WorkflowLookup`, `TestHttpTriggerHandler_HandleUserTriggerRequest_JWTAuthorization`).

## Impact Explanation
An unauthenticated caller can enumerate which `workflowID` / `workflowOwner`+`workflowName`+`workflowTag` combinations are registered and assigned to a DON by observing the differentiated error responses, without ever presenting a valid JWT or authorized key. This is a workflow-identifier/owner enumeration (information disclosure) issue rather than a direct authentication bypass, key exfiltration, or fund-movement impact — `authorizeRequest`'s JWT/signer checks remain intact and are not bypassed for actually triggering a workflow. The practical value to an attacker is reconnaissance: narrowing the search space of valid workflows/owners for follow-on targeted attacks.

## Likelihood Explanation
The lookup is on the direct path of every user trigger request and requires only a well-formed JSON-RPC `workflows.execute` request with syntactically valid `workflow` selector fields (validated by `validateWorkflowFields`/`validateHexInput`) — no valid `Auth` field is needed to reach `resolveWorkflowID`. This makes probing straightforward, repeatable, and low-cost for brute-forcing owner+name+tag combinations or workflowIDs.

## Recommendation
Reorder the pipeline in `HandleUserTriggerRequest` so `authorizeRequest` (or at minimum a coarse-grained authentication/signature check) runs before `resolveWorkflowID`, or make the "not found" response indistinguishable from an authorization failure when the caller has not presented valid credentials, so unauthenticated requests cannot be used as an existence oracle for workflow identifiers/owners.

## Proof of Concept
1. Send a JSON-RPC `workflows.execute` request to the gateway's HTTP trigger endpoint with no valid `Auth` field, varying `workflowOwner`/`workflowName`/`workflowTag` (or `workflowID`) guesses.
2. Observe that requests referencing non-existent workflows return `"Workflow not found. ..."` from `resolveWorkflowID`, while requests referencing real, registered workflows proceed further and instead return `"Auth failure: ..."` from `authorizeRequest`.
3. This response difference lets the caller determine which guessed workflow identifiers/owners exist on the DON without supplying valid credentials, as reproducible via a Go test analogous to `TestHttpTriggerHandler_HandleUserTriggerRequest_WorkflowLookup` (unregistered workflow, no `Auth`) compared against `TestHttpTriggerHandler_HandleUserTriggerRequest_JWTAuthorization`'s "invalid JWT token" case (registered workflow, invalid `Auth`).

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L342-365)
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

**File:** core/services/gateway/gateway.go (L267-279)
```go
	startTime := time.Now()
	var method string
	callback := handlerscommon.NewCallback()
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L392-402)
```go
func (h *gatewayHandler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback handlers.Callback) error {
	h.metrics.IncrementTriggerRequestCount(ctx, h.lggr)
	err := h.triggerHandler.HandleUserTriggerRequest(ctx, &req, callback, time.Now())
	if err != nil {
		h.lggr.Errorw("failed to handle user trigger request", "requestID",
			req.ID, "err", err)
		// error response is sent to the response channel by the trigger handler
		// so return nil after logging
	}
	return nil
}
```
