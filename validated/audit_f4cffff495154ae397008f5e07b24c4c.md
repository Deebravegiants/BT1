### Title
Pre-authentication workflow-existence oracle in HTTP Trigger Handler `resolveWorkflowID` — ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
`httpTriggerHandler.HandleUserTriggerRequest` resolves a workflow selector to a `workflowID` and confirms its existence *before* verifying the caller's JWT/signature, allowing an unauthenticated/unprivileged caller to enumerate valid `workflowID`s and valid `(workflowOwner, workflowName, workflowTag)` triples via a distinguishable error response. This mirrors the class of bug in CVE-2022-2761 (BIT-gitlab-2022-2761), where GFM reference resolution leaked existence of resources the caller could not access, prior to/independent of authorization.

### Finding Description
`HandleUserTriggerRequest` executes stages in this order: [1](#0-0) 

1. `validatedTriggerRequest` — only JSON/format validation, no auth.
2. `resolveWorkflowID` — looks up the workflow by ID or by owner/name/tag in `workflowMetadataHandler` and returns `"workflow not found"` if it doesn't exist: [2](#0-1) 
3. Only *after* that does `authorizeRequest` verify the JWT and check the signer against `authorizedKeys`: [3](#0-2) 

`WorkflowMetadataHandler.Authorize` itself distinguishes "workflow ID not found" from "signer not authorized" with different error text, and is only reached after existence is already confirmed by `resolveWorkflowID`: [4](#0-3) 

Because the request need not carry a valid `Auth` JWT to reach `resolveWorkflowID`, and the error message differs based on whether a `workflowID` (or owner/name/tag combination) exists at all ("Workflow not found..." vs. proceeding on to an authorization failure), a caller with no valid credentials can send crafted `HTTPTriggerRequest` payloads and learn:
- Whether a specific `workflowID` exists.
- Whether a specific `(workflowOwner, workflowName, workflowTag)` combination is a currently-registered, live workflow — i.e., confirming that a given owner address runs a workflow with a particular name/tag.

This is directly analogous to the GitLab bug class: use of a reference-resolution mechanism to disclose the existence of a resource the caller has no access to, without needing valid authorization first.

### Impact Explanation
An unauthenticated network caller of the gateway's HTTP trigger endpoint can enumerate valid workflow identifiers and owner/name/tag combinations. This discloses which workflows (and workflow owners) are active on the gateway, which is sensitive operational/business metadata (workflow existence, ownership, naming, versioning via tags) that should only be confirmable by parties holding a valid, authorized signing key for that workflow. This is an information-disclosure issue rather than a direct fund-movement or full auth-bypass; severity is Medium, consistent with the analog CVE's rating.

### Likelihood Explanation
High likelihood of exploitability: the check is unconditionally reachable by any client that can reach the gateway's JSON-RPC HTTP trigger endpoint, requires no valid signature, and the endpoint returns machine-distinguishable error strings ("Workflow not found..." vs. "auth failure: ...") for the two failure modes, as confirmed by the handler's test suite (`TestHttpTriggerHandler_HandleUserTriggerRequest_JWTAuthorization`, "workflow not found" test case) which shows the "workflow not found" path is reached and distinct from unauthorized-signer failures: [5](#0-4) 

### Recommendation
Perform workflow-existence resolution and authorization in a way that does not leak existence to unauthenticated callers, e.g.:
- Return an identical, generic error (same code/message) for both "workflow not found" and "signer not authorized" cases when the request is unauthenticated or the signature check fails, so the responses are indistinguishable.
- Alternatively, verify the JWT signature (and rate-limit) before resolving/confirming workflow selector existence, only revealing "not found" after a valid signature has been checked against at least a global keyset, or after successful authentication.
- Ensure timing of the two failure branches is also similar to avoid timing-based oracles.

### Proof of Concept
1. Send a `workflows.execute` JSON-RPC request to the gateway's HTTP trigger endpoint with `Workflow.WorkflowID` set to a guessed/candidate 32-byte hex ID and no (or an invalid) `Auth` JWT.
2. If the response error is `"Workflow not found. 'workflowID' ... is not a valid workflow ID"`, the ID does not exist.
3. If instead the response is `"auth failure: ..."` (e.g., "invalid JWT format" propagated from `authorizeRequest`), the `workflowID` exists (or, for owner/name/tag lookups, that exact triple is registered), even though the caller supplied no valid credentials.
4. Repeat with different `WorkflowOwner`/`WorkflowName`/`WorkflowTag` combinations (per `resolveWorkflowID`'s fallback path) to enumerate registered workflows per owner without ever presenting a valid signed JWT.

**Note on scope/uncertainty:** I focused on the gateway-facing HTTP Trigger Handler and Vault Gateway Handler paths, which are the most plausible internet-facing analogs to the GitLab reference-disclosure CVE. I did not find a stronger "unauthorized job run/fund movement" or "secret disclosure" analog reachable from an unprivileged client — the Vault allowlist/JWT authorization paths (`core/capabilities/vault/allow_list_based_auth.go`, `gateway_vault_request_processor.go`) and the HTTP Action response cache (`response_cache.go`) appeared correctly scoped by owner/digest and did not show an unprivileged bypass. Due to index size limits, some files (e.g., full `http_handler.go`, `workflow_metadata_handler.go` middle sections) may not have been fully retrievable; a full Devin session could verify whether any additional guard exists upstream (e.g., at the JSON-RPC router level) that gates `resolveWorkflowID` behind authentication in a way not visible in the indexed snippets.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L1091-1149)
```go
	t.Run("unauthorized signer", func(t *testing.T) {
		callback := hc.NewCallback()
		unauthorizedKey := createTestPrivateKey(t)

		triggerReq := createTestTriggerRequest(workflowID)
		reqBytes, err2 := json.Marshal(triggerReq)
		require.NoError(t, err2)

		rawParams := json.RawMessage(reqBytes)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      "test-request-id-3",
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &rawParams,
		}

		jwtToken := createTestJWTToken(t, req, unauthorizedKey)
		req.Auth = jwtToken

		err = handler.HandleUserTriggerRequest(ctx, req, callback, time.Now())
		require.Error(t, err)
		require.Contains(t, err.Error(), "auth failure")

		r, err2 := callback.Wait(t.Context())
		require.NoError(t, err2)
		requireUserErrorSent(t, r, jsonrpc.ErrInvalidRequest)
	})

	t.Run("workflow not found", func(t *testing.T) {
		callback := hc.NewCallback()

		triggerReq := gateway_common.HTTPTriggerRequest{
			Workflow: gateway_common.WorkflowSelector{
				WorkflowID: "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
			},
			Input: []byte(`{"key": "value"}`),
		}
		reqBytes, err2 := json.Marshal(triggerReq)
		require.NoError(t, err2)

		rawParams := json.RawMessage(reqBytes)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      "test-request-id-4",
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &rawParams,
		}

		jwtToken := createTestJWTToken(t, req, privateKey)
		req.Auth = jwtToken

		err = handler.HandleUserTriggerRequest(ctx, req, callback, time.Now())
		require.Error(t, err)
		require.Contains(t, err.Error(), "workflow not found")

		r, err2 := callback.Wait(t.Context())
		require.NoError(t, err2)
		requireUserErrorSent(t, r, jsonrpc.ErrInvalidRequest)
	})
```
