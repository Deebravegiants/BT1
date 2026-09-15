Audit Report

## Title
`handleCapabilityExecute` skips the Workflow-DON owner/workflow authorization check enforced on the sibling `handleSecretsGet` path - ([File: core/capabilities/confidentialrelay/handler.go])

## Summary
`handleSecretsGet` enforces `verifyWorkflowAuthorization`, which validates a Workflow-DON-signed quorum (`SignedComputeRequests`) naming the authorized `Owner`/`WorkflowID` before serving any secrets, explicitly documented as the PRIV-433 fix for the case where a compromised TEE host can produce a genuinely-attested request while self-asserting a victim's owner. `handleCapabilityExecute` performs only attestation and enclave-config-vs-DON validation and has no equivalent authorization step, and its request type, `confidentialrelaytypes.CapabilityRequestParams`, does not even carry a `SignedComputeRequests` field to check against — confirmed by the test fixtures constructing `CapabilityRequestParams` with only `WorkflowID`, `Owner`, `ExecutionID`, `ReferenceID`, `CapabilityID`, `Payload`, `EnclaveConfig`, and `Attestation`.

## Finding Description
`handleSecretsGet` calls, in order, attestation validation, `verifyEnclaveConfigMatchesDON`, then `verifyWorkflowAuthorization(localNode.WorkflowDON, params)`: [1](#0-0) . `verifyWorkflowAuthorization`'s own documentation states this closes the exact gap where "a compromised TEE would still pass attestation while self-asserting a victim's owner" (PRIV-433), by requiring a 2*F+1 (or F+1) Workflow-DON quorum over a `ComputeRequest` whose `PublicData` names the authorized `Owner`/`WorkflowID`, matched against the request: [2](#0-1) .

`handleCapabilityExecute`, in contrast, only performs attestation validation and `verifyEnclaveConfigMatchesDON` before proceeding directly into the memo/pending-request/execution flow — there is no call to `verifyWorkflowAuthorization` or any equivalent check: [3](#0-2) . The cache key, `capExecKey`, is derived purely from `WorkflowID`/`ExecutionID`/`ReferenceID`/`CapabilityID`, with no binding to an authorized owner: [4](#0-3) . `params.Owner` is used only to seed tracing context, not to gate execution: [5](#0-4) . `executeCapability` resolves the execution handler purely from `WorkflowID`/`ExecutionID`, calls the capability, and signs the result with no re-check of authorized ownership: [6](#0-5) . Confirming the structural gap, `CapabilityRequestParams` used throughout the tests carries no `SignedComputeRequests` field at all: [7](#0-6) , [8](#0-7) .

This is a genuine asymmetry between two sibling gateway entrypoints that share the exact same threat model (a compromised/malicious TEE host producing a genuinely-attested but falsely-attributed request) — one path fixes it (PRIV-433), the other does not.

## Impact Explanation
Under the codebase's own stated threat model, a compromised TEE host can produce an attested `MethodCapabilityExec` request while self-asserting an arbitrary `Owner`/`WorkflowID`. Because `handleCapabilityExecute` never validates a Workflow-DON quorum over that claim, such a request is executed, signed, and cached under the attacker-claimed identity — a capability-execution/response-impersonation issue in the gateway-facing relay handler, directly analogous to the already-fixed PRIV-433 secrets-get case.

## Likelihood Explanation
Exploitation requires the same actor capability the codebase itself already treats as a credible threat for `handleSecretsGet` (a compromised/malicious TEE-hosting enclave/host process that can still produce genuinely-attested requests). Since `handleCapabilityExecute` is reachable via the identical `HandleGatewayMessage`/`MethodCapabilityExec` gateway entrypoint with no additional authorization gate, and the codebase has already validated this actor model as worth defending against on the sibling path, the missing check here is directly and repeatably exploitable by that same actor.

## Recommendation
Add a `SignedComputeRequests`-equivalent field to `CapabilityRequestParams` (or otherwise thread the Workflow-DON-signed compute request through the capability-exec path) and enforce an owner/workflow authorization check in `handleCapabilityExecute`, mirroring `verifyWorkflowAuthorization`, before consulting the memo/pending-request cache or calling `executeCapability`.

## Proof of Concept
1. Compromise/control the TEE-hosting enclave/host process (the same precondition the code already accepts as the PRIV-433 threat for `handleSecretsGet`).
2. Craft a `CapabilityRequestParams` with an attacker-chosen `Owner`, an existing `WorkflowID`/`ExecutionID` matching a running execution on the target node, and a correctly attested request (attestation binds only the request hash, not authorization).
3. Submit via `MethodCapabilityExec` to the gateway; `handleCapabilityExecute` validates only attestation and enclave-config-vs-DON, then proceeds through `capExecKey` memo/pending logic and `executeCapability`, producing and caching a signed capability response attributed to the attacker-supplied `Owner`, whereas an equivalent `handleSecretsGet` request with a mismatched owner would be rejected by `verifyWorkflowAuthorization`. A Go unit test analogous to `TestVerifyWorkflowAuthorization` (`core/capabilities/confidentialrelay/handler_test.go:1009-1097`) that instead drives `handleCapabilityExecute` with a forged `Owner` and no possible authorization field demonstrates the gap.

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

**File:** core/capabilities/confidentialrelay/handler.go (L564-618)
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
```

**File:** core/capabilities/confidentialrelay/handler.go (L681-736)
```go
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

**File:** core/capabilities/confidentialrelay/handler.go (L871-934)
```go
// verifyWorkflowAuthorization is the PRIV-433 check beyond attestation. Attestation only
// proves the request came from genuine enclave code; it does not prove the Workflow DON
// authorized fetching this owner's secrets. A compromised TEE would still pass attestation
// while self-asserting a victim's owner.
//
// The enclave forwards the Workflow-DON-signed compute requests it executed (a 2*F+1 quorum,
// where F is the Workflow DON fault tolerance). Each node signs the same ComputeRequest.Hash();
// we reconstruct that hash, verify each signature against the onchain Workflow DON signer set,
// and require the quorum of unique signers. The signed PublicData names the authorized owner
// and workflow, which must match this request. A breached enclave cannot forge a Workflow DON
// quorum over a different owner.
//
// All failures here are client errors: the request is unauthorized. The caller fetches the
// Workflow DON (a server-side concern) and passes it in, so registry failures stay internal.
func (h *Handler) verifyWorkflowAuthorization(don capabilities.DON, params confidentialrelaytypes.SecretsRequestParams) error {
	if len(params.SignedComputeRequests) == 0 {
		return errors.New("missing signed compute requests")
	}

	// Match the enclave's own quorum. With requireBFTQuorum the relay demands a
	// Byzantine quorum of 2*F+1 unique signers; otherwise a crash-fault quorum of
	// F+1 suffices.
	threshold := int(don.F) + 1
	if h.requireBFTQuorum {
		threshold = 2*int(don.F) + 1
	}

	// The forwarded requests differ only in their signature; they all sign one shared
	// ComputeRequest hash. Reconstruct that hash once and verify each signature over it.
	hash := params.SignedComputeRequests[0].Hash()
	payload := confidentialrelaytypes.SignedComputeRequestSignaturePayload(hash)

	signers := make(map[string]struct{})
	for _, scr := range params.SignedComputeRequests {
		if scr.Hash() != hash {
			return errors.New("forwarded signed compute requests do not share one compute request")
		}
		for _, member := range don.Members {
			if ed25519.Verify(ed25519.PublicKey(member[:]), payload, scr.Signature) {
				signers[member.String()] = struct{}{}
				break
			}
		}
	}
	if len(signers) < threshold {
		return fmt.Errorf("insufficient Workflow DON signatures: %d unique signers, need %d", len(signers), threshold)
	}

	// The signed request authorizes a specific owner and workflow; the secrets request must
	// match both, or a breached enclave could fetch another owner's secrets.
	var execution confidentialworkflow.WorkflowExecution
	if err := proto.Unmarshal(params.SignedComputeRequests[0].PublicData, &execution); err != nil {
		return fmt.Errorf("failed to unmarshal workflow execution from public data: %w", err)
	}
	if !common.IsHexAddress(params.Owner) || !common.IsHexAddress(execution.GetOwner()) {
		return errors.New("invalid owner address")
	}
	if common.HexToAddress(execution.GetOwner()) != common.HexToAddress(params.Owner) {
		return fmt.Errorf("owner not authorized: request %q vs signed %q", params.Owner, execution.GetOwner())
	}
	if execution.GetWorkflowId() != params.WorkflowID {
		return fmt.Errorf("workflow_id not authorized: request %q vs signed %q", params.WorkflowID, execution.GetWorkflowId())
	}
	return nil
```

**File:** core/capabilities/confidentialrelay/response_cache.go (L17-23)
```go
// capExecKey is the deterministic cache key for a capability-exec request,
// built from its logical identity: the (workflow, execution, step, capability)
// tuple the relay-DON signature binds to. Avoids hashing: the fields are
// required non-empty by Validate, so a plain join is stable and debuggable.
func capExecKey(p confidentialrelaytypes.CapabilityRequestParams) string {
	return strings.Join([]string{capabilityCallDomain, p.WorkflowID, p.ExecutionID, p.ReferenceID, p.CapabilityID}, "/")
}
```

**File:** core/services/gateway/handlers/confidentialrelay/bundler_test.go (L25-34)
```go
func validCapParams(workflowID string) relaytypes.CapabilityRequestParams {
	return relaytypes.CapabilityRequestParams{
		WorkflowID:   workflowID,
		Owner:        testOwner,
		ExecutionID:  testExecutionID,
		ReferenceID:  "ref-1",
		CapabilityID: "cap-1",
		Payload:      "in",
	}
}
```

**File:** core/capabilities/confidentialrelay/handler_test.go (L535-544)
```go
				return makeRequest(t, confidentialrelaytypes.MethodCapabilityExec, confidentialrelaytypes.CapabilityRequestParams{
					WorkflowID:    "wf-1",
					Owner:         testOwner,
					ExecutionID:   capExecExecutionID,
					ReferenceID:   "17",
					CapabilityID:  "fail-cap@1.0.0",
					Payload:       base64.StdEncoding.EncodeToString(b),
					EnclaveConfig: testEnclaveConfigPtr(),
					Attestation:   testAttestationB64,
				})
```
