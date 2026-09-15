Confirmed: `verifyWorkflowAuthorization` (the PRIV-433 check) is defined to take `confidentialrelaytypes.SecretsRequestParams` and is only invoked from `handleSecretsGet`. `handleCapabilityExecute` never calls it, even though it uses the exact same untrusted-owner-assertion pattern (`params.Owner`, `params.WorkflowID`, `params.OrgID` are attacker/enclave-supplied fields that are only checked for internal consistency via the attestation hash, not cross-checked against an independent Workflow-DON-signed quorum).

### Title
Missing PRIV-433 Workflow-DON authorization check in `handleCapabilityExecute` allows a compromised enclave to assert an arbitrary owner/workflow tenant context - (File: `core/capabilities/confidentialrelay/handler.go`)

### Summary
`handleCapabilityExecute` seeds the CRE tenant context (`Org`, `Owner`, `Workflow`) directly from client-supplied `CapabilityRequestParams` and only validates that these fields are *internally consistent* with the attestation hash and enclave-config, but never validates that they were actually authorized by an independent, signed source (the Workflow DON quorum), unlike its sibling `handleSecretsGet`.

### Finding Description
`handleCapabilityExecute` unmarshals `CapabilityRequestParams` from the request and immediately seeds `contexts.WithCRE(ctx, contexts.CRE{Org: params.OrgID, Owner: params.Owner, Workflow: params.WorkflowID})` [1](#0-0) . It then runs `verifyAttestationHash` (binding the hash to the TEE attestation) and `verifyEnclaveConfigMatchesDON` (binding the reported DON config to on-chain state) [2](#0-1) , but it does **not** call `verifyWorkflowAuthorization`.

Compare this to `handleSecretsGet`, which performs the identical attestation and enclave-config checks and then adds an explicit third check:
```go
// Beyond attestation, verify the Workflow DON authorized this request: ...
// A TEE breach passes attestation but cannot forge a Workflow
// DON quorum over a different owner (PRIV-433).
if err = h.verifyWorkflowAuthorization(localNode.WorkflowDON, params); err != nil {
``` [3](#0-2) 

`verifyWorkflowAuthorization` independently verifies a 2*F+1 (or F+1) quorum of ed25519 signatures from the on-chain Workflow DON member set over a `ComputeRequest` whose `PublicData` names the actually-authorized `Owner`/`WorkflowId`, and rejects the request if `params.Owner`/`params.WorkflowID` don't match that independently-signed identity [4](#0-3) . The code comment makes explicit why this check exists: *"Attestation only proves the request came from genuine enclave code; it does not prove the Workflow DON authorized fetching this owner's secrets. A compromised TEE would still pass attestation while self-asserting a victim's owner."*

`handleCapabilityExecute` has no equivalent binding. `verifyAttestationHash` only proves the params were produced by *some* genuinely-attested enclave process — it does not prove the enclave (if compromised) is executing on behalf of the owner/workflow it claims. `CapabilityRequestParams` carries no `SignedComputeRequests` field to bind `Owner`/`WorkflowID` to an independent DON-signed source (confirmed by the test fixture `validCapParams`, which populates only `WorkflowID`, `Owner`, `ExecutionID`, `ReferenceID`, `CapabilityID`, `Payload` — no signed-quorum field) [5](#0-4) .

This is the direct structural analog of the external report: a field (`payload_type` in the Cairo case; `Owner`/`OrgID`/`WorkflowID` here) that is accepted as part of the message and used to drive downstream behavior (tenant context seeding for capability execution, response signing) without being bound to an independently-verified authorization source, even though a sibling code path in the very same file demonstrates the correct pattern and explicitly documents the threat model this omission reintroduces.

### Impact Explanation
If the enclave process is compromised (the exact threat model the PRIV-433 comment defends against for `handleSecretsGet`), the missing check in `handleCapabilityExecute` lets it self-assert any `Owner`/`OrgID`/`WorkflowID`, causing this relay node to execute a capability and sign a response under an incorrect/attacker-chosen tenant identity. Because `CapabilityRequestParams` provides no signed-quorum binding mechanism at all for this path, there is no way for the relay to detect the forged tenant assertion — unlike secrets retrieval, which is explicitly hardened against this exact scenario.

### Likelihood Explanation
This requires the TEE/enclave to be compromised (matching the same "breached enclave" precondition explicitly called out and defended against in `handleSecretsGet`'s own code comments) — it is not exploitable by a fully external, unauthenticated actor without a valid attestation. However, since the codebase itself treats "compromised enclave passes attestation" as a live threat worth defending in the sibling function, the absence of the same defense here is a genuine inconsistency/regression rather than a hypothetical.

### Recommendation
Add an equivalent Workflow-DON-signed authorization check to `handleCapabilityExecute`, analogous to `verifyWorkflowAuthorization` used in `handleSecretsGet`: extend `CapabilityRequestParams` (or reuse `SignedComputeRequests`) so `Owner`/`WorkflowID`/`OrgID` are bound to an independently-signed Workflow DON quorum before being used to seed the CRE context or execute the capability.

### Proof of Concept
Conceptual (cannot be executed without the enclave compromise precondition, but structurally demonstrable via the code paths):
1. Compromise or otherwise control the enclave process such that it can produce a genuinely-attested `MethodCapabilityExec` request (attestation covers only the JSON of `CapabilityRequestParams` itself, not any external authorization source).
2. Set `params.Owner`, `params.OrgID`, `params.WorkflowID` to an arbitrary victim tenant's identifiers while keeping `EnclaveConfig`/attestation internally self-consistent.
3. Call `handleCapabilityExecute`; `verifyAttestationHash` and `verifyEnclaveConfigMatchesDON` pass because they only check internal consistency of the attested params/config, not against the true authorized tenant [2](#0-1) .
4. No `verifyWorkflowAuthorization`-equivalent call exists to reject the forged `Owner`/`WorkflowID`, so `executeCapability` runs with the CRE tenant context set to the attacker-chosen identity and produces a signed response as if it were legitimately authorized [6](#0-5) .

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

**File:** core/capabilities/confidentialrelay/handler.go (L573-583)
```go
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

**File:** core/capabilities/confidentialrelay/handler.go (L655-672)
```go
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
```

**File:** core/capabilities/confidentialrelay/handler.go (L885-934)
```go
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
