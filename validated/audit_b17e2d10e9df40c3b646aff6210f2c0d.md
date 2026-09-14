### Title
`handleCapabilityExecute` skips the Workflow-DON owner-authorization check that `handleSecretsGet` enforces, allowing an unverified `Owner`/`WorkflowID` to be stamped onto the request context - ([File: core/capabilities/confidentialrelay/handler.go])

### Summary
In the enclave relay gateway handler, `handleSecretsGet` requires the enclave-forwarded request to carry a quorum of Workflow-DON signatures over a `ComputeRequest` whose `PublicData` names the authorized `Owner`/`WorkflowID`, and it explicitly rejects the request if `params.Owner` doesn't match that signed owner (`verifyWorkflowAuthorization`, called at [1](#0-0) ). `handleCapabilityExecute` receives an analogous `Owner` field and immediately seeds it into the request context via `contexts.WithCRE` before any such quorum check is performed [2](#0-1) , and never calls `verifyWorkflowAuthorization` or any equivalent check anywhere in `handleCapabilityExecute`/`executeCapability` [3](#0-2) .

### Finding Description
This maps to the same bug class as the Astaria "buyout paid by liquidity providers, not by a borrower" report: an action is executed and its effects/attribution are billed/scoped to an identity (`Owner`) taken from unverified request data, instead of the identity actually cryptographically authorized to perform (and pay/be charged for) the action. In Astaria, `VaultImplementation.buyoutLien` let the vault (a shared pool) pay for what should have been an individually-authorized borrower action because the code never validated that the payer matched the intended actor. Here, `handleCapabilityExecute` takes `params.Owner` directly off the wire and stamps it into `contexts.WithCRE(ctx, contexts.CRE{Owner: params.Owner, ...})` (line 579-583) — which is then used downstream (via `handler.CallCapability`) to scope capability execution, metering, and access to the named owner's context/resources — without first confirming, as the sibling `handleSecretsGet` path does, that a quorum of Workflow-DON signers actually signed a `ComputeRequest` for that same `Owner`/`WorkflowID` (`verifyWorkflowAuthorization`, lines 871-935).

The design comment at line 373-381 (and the "PRIV-433" reference embedded in `verifyWorkflowAuthorization`'s doc comment at lines 871-882) shows the authors were specifically aware that TEE attestation alone "proves the request came from genuine enclave code" but "does not prove the Workflow DON authorized" acting on behalf of a given owner, and that "a compromised TEE would still pass attestation while self-asserting a victim's owner." That protection was added for the secrets-fetch path but not for the capability-execution path, leaving an asymmetric gap.

### Impact Explanation
If the `Owner` field on a `MethodCapabilityExec` gateway request is not otherwise constrained (e.g., it is not itself covered by the attestation-domain hash the same way `SignedComputeRequests` binds `handleSecretsGet`, or if the enclave computing the request can be influenced/compromised), a request can execute a capability while impersonating an owner other than the one actually authorized by Workflow-DON quorum. Depending on what `contexts.CRE.Owner` gates downstream in `handler.CallCapability` (billing/metering, per-owner resource limits, per-owner capability access), this is a cross-owner impersonation/authorization-bypass primitive — the same class of "unauthorized action performed/billed under the wrong identity" as the original report, just realized through capability execution rather than fund transfer.

### Likelihood Explanation
Exploitability depends on whether `params.Owner` is independently cryptographically bound elsewhere in the capability-exec flow (this could not be fully confirmed from the available index — `handleCapabilityExecute`'s attestation check at line 596 hashes `cleanParams`, which does include `Owner`, but attestation only proves the enclave itself produced this exact byte string; it does not prove the Workflow DON authorized *this* `Owner` value, which is exactly the gap `verifyWorkflowAuthorization` was built to close for secrets). Given the explicit PRIV-433 rationale documented for the secrets path, the absence of the equivalent check on the capability-exec path looks like a genuine, reachable asymmetry rather than an intentional design choice, but I could not fully verify inside this review whether some other layer (e.g., inside `handler.CallCapability` or the workflow engine itself) revalidates `Owner` against the signed `WorkflowExecution` before the capability actually runs. This uncertainty should be resolved by inspecting `core/services/workflows/v2/capability_executor.go` and `ExecutionHandlers.GetExecutionWithWait`, which I was not able to fully read given the remaining tool budget.

### Recommendation
Add an equivalent Workflow-DON quorum/owner-authorization check to `handleCapabilityExecute` (mirroring `verifyWorkflowAuthorization` in `handleSecretsGet`) before `params.Owner`/`params.WorkflowID` are used to seed `contexts.WithCRE` or passed to `handler.CallCapability`. At minimum, require the same `SignedComputeRequests` quorum-of-signers check over a `PublicData`-embedded `Owner`/`WorkflowID`, and reject the request if it doesn't match `params.Owner`/`params.WorkflowID`, exactly as is already done for the secrets-get path.

### Proof of Concept
Not directly executable from static review alone; the concrete PoC would require confirming (via `core/services/workflows/v2/capability_executor.go` and the `ExecutionHandlers`/`CallCapability` implementation) that no later stage revalidates `params.Owner` against a Workflow-DON-signed value before completing execution. Structurally: a gateway `MethodCapabilityExec` request with `params.Owner` set to a victim owner, and a valid attestation over that exact params blob (obtainable if the request-construction/enclave path can be influenced to set an arbitrary `Owner`), would reach `contexts.WithCRE(... Owner: <victim>)` and `handler.CallCapability` without ever passing through an owner-quorum check equivalent to `verifyWorkflowAuthorization`.

### Citations

**File:** core/capabilities/confidentialrelay/handler.go (L374-381)
```go
	// Beyond attestation, verify the Workflow DON authorized this request: the enclave
	// forwards the Workflow-DON-signed compute requests (a 2*F+1 quorum), whose PublicData
	// names the authorized owner. A TEE breach passes attestation but cannot forge a Workflow
	// DON quorum over a different owner (PRIV-433).
	if err = h.verifyWorkflowAuthorization(localNode.WorkflowDON, params); err != nil {
		l.Warnw("rejecting secrets request: workflow DON authorization failed", "err", err)
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInvalidParams, err)
	}
```

**File:** core/capabilities/confidentialrelay/handler.go (L564-736)
```go
func (h *Handler) handleCapabilityExecute(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	if req.Params == nil {
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInvalidParams, errors.New("missing params"))
	}
	var params confidentialrelaytypes.CapabilityRequestParams
	if err := json.Unmarshal(*req.Params, &params); err != nil {
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInvalidParams, err)
	}

	// The enclave's capability calls arrive as fresh gateway messages rather than
	// through the workflow engine, so ctx carries none of the CRE tenants the engine
	// seeds.
	//
	// Seeded as soon as the params are parsed so every ctx use below carries the
	// tenant.
	ctx = contexts.WithCRE(ctx, contexts.CRE{
		Org:      params.OrgID,
		Owner:    params.Owner,
		Workflow: params.WorkflowID,
	})

	// See handleSecretsGet: the gateway request id plus the workflow/execution
	// identity on every line, so logs correlate across the gateway, this node
	// and the enclave for one execution.
	l := logger.With(h.lggr,
		"requestID", req.ID,
		"workflowID", params.WorkflowID,
		"executionID", params.ExecutionID,
	)

	att := params.Attestation
	params.Attestation = ""
	if err := h.verifyAttestationHash(ctx, att, params, confidentialrelaytypes.DomainCapabilityExec); err != nil {
		l.Warnw("rejecting capability request: attestation validation failed", "err", err)
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, err)
	}

	// Verify the enclave's reported config matches the onchain DON state, same as
	// handleSecretsGet (PRIV-458): the Nitro attestation binds the request hash but
	// not the config value, so a malicious host could otherwise produce a
	// genuinely-attested request over a forged enclave config.
	localNode, err := h.capRegistry.LocalNode(ctx)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, fmt.Errorf("failed to get local node: %w", err))
	}
	if err = h.verifyEnclaveConfigMatchesDON(localNode, params.EnclaveConfig); err != nil {
		l.Warnw("rejecting capability request: enclave config does not match DON", "err", err)
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, err)
	}

	// A retry (same logical identity, new gateway request id) re-fans-out the
	// same request; return the already-computed signed result from the memo
	// instead of re-executing the capability. The signed result is params-bound,
	// not id-bound, so jsonResponse re-wraps it with this request's id.
	key := capExecKey(params)
	l = logger.With(l, "key", key)

	h.pendingRequestsMu.Lock()
	if cached, ok := h.responseMemo.Get(key); ok {
		if signed, ok := cached.(*confidentialrelaytypes.SignedCapabilityResponseResult); ok {
			h.pendingRequestsMu.Unlock()
			l.Debugw("serving capability request from memo")
			return h.jsonResponse(req, signed)
		}
	}

	// A retry that arrives while the original execution is still in flight
	// waits on it and responds with the owner's result rather than
	// re-executing.
	pending, err := h.checkOrCreatePendingRequest(key)
	if err != nil {
		h.pendingRequestsMu.Unlock()
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, err)
	}
	h.pendingRequestsMu.Unlock()
	if pending != nil {
		signed, ok, pendingReqErr := waitForPendingRequest(ctx, pending)
		switch {
		case !ok:
			l.Warnw("timed out waiting for in-flight capability request", "err", ctx.Err())
			return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, errors.New("timed out waiting for in-flight capability request"))
		case pendingReqErr != nil:
			errorCode := relayErrorCode(pendingReqErr, jsonrpc.ErrInternal)
			l.Debugw("in-flight capability request failed; relaying its error", "errorCode", errorCode)
			return h.errorResponse(ctx, gatewayID, req, errorCode, pendingReqErr)
		}
		if signed, ok := signed.(*confidentialrelaytypes.SignedCapabilityResponseResult); ok {
			l.Debugw("served retried capability request from in-flight owner")
			return h.jsonResponse(req, signed)
		}
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, errors.New("in-flight capability request completed without a result"))
	}

	// We own the pending entry: execute, then publish the outcome to any
	// waiters either way; see handleSecretsGet.
	signedResult, err := h.executeCapability(ctx, l, params)
	if err != nil {
		h.pendingRequestsMu.Lock()
		h.failPendingRequest(key, err)
		h.pendingRequestsMu.Unlock()
		return h.errorResponse(ctx, gatewayID, req, relayErrorCode(err, jsonrpc.ErrInternal), err)
	}

	h.pendingRequestsMu.Lock()
	h.responseMemo.SetDefault(key, signedResult)
	h.completePendingRequest(key, signedResult)
	h.pendingRequestsMu.Unlock()
	l.Infow("executed and signed capability response", "capability", params.CapabilityID)
	return h.jsonResponse(req, signedResult)
}

// executeCapability decodes the request payload, resolves the execution
// handler, runs the capability, and signs the result. Errors are relayErrors
// carrying the JSON-RPC code the request should be answered with, so the
// caller can both answer this request and publish the same failure to any
// waiters. A capability that itself returns an error is not an error here: it
// produces a signed error result the enclave's quorum logic handles.
func (h *Handler) executeCapability(
	ctx context.Context,
	l logger.Logger,
	params confidentialrelaytypes.CapabilityRequestParams,
) (*confidentialrelaytypes.SignedCapabilityResponseResult, error) {
	payloadBytes, err := base64.StdEncoding.DecodeString(params.Payload)
	if err != nil {
		return nil, &relayError{code: jsonrpc.ErrInvalidParams, err: fmt.Errorf("failed to decode payload: %w", err)}
	}

	sdkReq := &sdkpb.CapabilityRequest{}
	if err = proto.Unmarshal(payloadBytes, sdkReq); err != nil {
		return nil, &relayError{code: jsonrpc.ErrInvalidParams, err: fmt.Errorf("failed to unmarshal capability request: %w", err)}
	}

	// Resolve the execution handler only after attestation and enclave-config
	// verification, so an unverified callback cannot make the node park a waiter.
	// The enclave's callback can beat this node's own execution start (start-edge
	// race); a bounded wait lets a straggler register and sign instead of dropping
	// below relay quorum (see handleSecretsGet).
	waitCtx, cancel := context.WithTimeout(ctx, h.getExecutionWait)
	defer cancel()
	handler, ok := h.executionHandlers.GetExecutionWithWait(waitCtx, params.WorkflowID, params.ExecutionID)
	if !ok {
		return nil, &relayError{code: jsonrpc.ErrInternal, err: fmt.Errorf("execution handler for workflow %s execution %s not found", params.WorkflowID, params.ExecutionID)}
	}

	capResp, execErr := handler.CallCapability(ctx, sdkReq)

	var result confidentialrelaytypes.CapabilityResponseResult
	if execErr != nil {
		// Not an error from this node's perspective: the execution result is a
		// signed error response the enclave's quorum logic handles; log it so
		// the capability-side failure is attributable to this node.
		l.Infow("capability execution returned an error result", "capability", sdkReq.Id, "err", execErr)
		result.Error = execErr.Error()
	} else {
		// Deterministic marshal so every relay node emits byte-identical
		// response payloads; relay aggregation requires identical bytes to
		// reach quorum. [CL112-05]
		var respBytes []byte
		respBytes, err = proto.MarshalOptions{Deterministic: true}.Marshal(capResp)
		if err != nil {
			return nil, &relayError{code: jsonrpc.ErrInternal, err: fmt.Errorf("marshalling capability response: %w", err)}
		}
		result.Payload = base64.StdEncoding.EncodeToString(respBytes)
	}

	signedResult, err := h.signCapabilityResponse(params, result)
	if err != nil {
		l.Errorw("signing capability response failed", "err", err)
		return nil, &relayError{code: jsonrpc.ErrInternal, err: fmt.Errorf("failed to sign capability response: %w", err)}
	}

	return signedResult, nil
}
```
