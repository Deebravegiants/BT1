Based on my investigation, I found a concrete analog to the reported bug class (a privileged operation missing its required authorization check) in the gateway-facing enclave relay handler.

### Title
Missing Workflow-DON Authorization Check in `handleCapabilityExecute` Allows Unauthorized Capability Execution - (File: `core/capabilities/confidentialrelay/handler.go`)

### Summary
`Handler.handleSecretsGet` and `Handler.handleCapabilityExecute` are the two gateway-facing entry points of the `EnclaveRelayHandler`, both reachable from an external (potentially malicious/compromised) TEE host via `HandleGatewayMessage`. [1](#0-0)  While `handleSecretsGet` performs an explicit Workflow-DON authorization check (`verifyWorkflowAuthorization`) beyond attestation validation, `handleCapabilityExecute` omits this same check entirely.

### Finding Description
`handleSecretsGet` validates the attestation hash and enclave config, and then — critically — calls `h.verifyWorkflowAuthorization(localNode.WorkflowDON, params)` before fetching secrets, explicitly documented as closing a gap where "A TEE breach passes attestation but cannot forge a Workflow DON quorum over a different owner" (PRIV-433). [2](#0-1) 

`handleCapabilityExecute`, by contrast, only performs `verifyAttestationHash` and `verifyEnclaveConfigMatchesDON` before proceeding directly to `executeCapability` — it never calls `verifyWorkflowAuthorization`. [3](#0-2) [4](#0-3)  The comment on `verifyEnclaveConfigMatchesDON` in `executeCapability`'s sibling explicitly states this same PRIV-458/PRIV-433 rationale applies, yet the owner/workflow-quorum check itself is not invoked in this path. `ctx` is seeded with `params.OrgID`, `params.Owner`, and `params.WorkflowID` straight from the untrusted request params without any DON-signed proof binding them to the actual attested execution. [5](#0-4) 

This mirrors the reported bug class: a sensitive/privileged action (`collectPositionSwapFee` should only be callable by the fund manager) lacks the access-control gate that an equivalent sibling function correctly enforces.

### Impact Explanation
A compromised or malicious TEE host that can produce a validly-attested request (attestation only proves the enclave *code* is genuine, not that the Workflow DON authorized the specific owner/workflow) could invoke `MethodCapabilityExec` and execute a capability under an arbitrary `Owner`/`WorkflowID`/`OrgID` context, without the Workflow-DON quorum signature check that would otherwise reject a forged owner. This could allow cross-tenant capability execution or workflow-context confusion, potentially triggering fund-moving or state-changing operations under another owner's identity.

### Likelihood Explanation
The likelihood is tied to attacker ability to compromise or manipulate the enclave host underlying the "malicious-node" boundary; however, this is explicitly the threat model the sibling `verifyWorkflowAuthorization` check in `handleSecretsGet` was designed to defend against (per the PRIV-433 comment), so the check's absence in `handleCapabilityExecute` is a direct regression of that same protection for the capability-execution path, which is reachable via the same gateway/host interface as secrets retrieval.

### Recommendation
Add the same `h.verifyWorkflowAuthorization(localNode.WorkflowDON, params)` (or an equivalent check appropriate to `CapabilityRequestParams`, if it carries a `SignedComputeRequests`/owner field) to `handleCapabilityExecute`, mirroring `handleSecretsGet`, before resolving the execution handler or calling `executeCapability`.

### Proof of Concept
Not independently verified end-to-end because the `CapabilityRequestParams` struct definition lives in the external `chainlink-common` module and was not available in this repo's index to confirm whether it exposes a `SignedComputeRequests` field identical to `SecretsRequestParams`. This is a structural/code-review finding based on directly comparing the two handler functions' authorization call sequences within `core/capabilities/confidentialrelay/handler.go`; a Devin session with full filesystem/dependency access would be needed to confirm the exact param shape and construct a runnable PoC request.

### Citations

**File:** core/capabilities/confidentialrelay/handler.go (L304-312)
```go
	var response *jsonrpc.Response[json.RawMessage]
	switch req.Method {
	case confidentialrelaytypes.MethodSecretsGet:
		response = h.handleSecretsGet(ctx, gatewayID, req)
	case confidentialrelaytypes.MethodCapabilityExec:
		response = h.handleCapabilityExecute(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrMethodNotFound, errors.New("unsupported method: "+req.Method))
	}
```

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

**File:** core/capabilities/confidentialrelay/handler.go (L576-583)
```go
	//
	// Seeded as soon as the params are parsed so every ctx use below carries the
	// tenant.
	ctx = contexts.WithCRE(ctx, contexts.CRE{
		Org:      params.OrgID,
		Owner:    params.Owner,
		Workflow: params.WorkflowID,
	})
```

**File:** core/capabilities/confidentialrelay/handler.go (L594-612)
```go
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
```

**File:** core/capabilities/confidentialrelay/handler.go (L657-665)
```go
	// We own the pending entry: execute, then publish the outcome to any
	// waiters either way; see handleSecretsGet.
	signedResult, err := h.executeCapability(ctx, l, params)
	if err != nil {
		h.pendingRequestsMu.Lock()
		h.failPendingRequest(key, err)
		h.pendingRequestsMu.Unlock()
		return h.errorResponse(ctx, gatewayID, req, relayErrorCode(err, jsonrpc.ErrInternal), err)
	}
```
