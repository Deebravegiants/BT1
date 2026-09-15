Audit Report

## Title
Missing PRIV-433 Workflow-DON authorization check in `handleCapabilityExecute` allows a compromised enclave to assert an arbitrary owner/workflow tenant context - (File: `core/capabilities/confidentialrelay/handler.go`)

## Summary
`handleCapabilityExecute` seeds the CRE tenant context and the signed response's `Owner`/`OrgID`/`WorkflowID` fields directly from client-supplied `CapabilityRequestParams` [1](#0-0) , and only checks internal consistency via attestation and enclave-config comparisons [2](#0-1) , unlike its sibling `handleSecretsGet`, which additionally calls `verifyWorkflowAuthorization` to bind these fields to an independently Workflow-DON-signed quorum [3](#0-2) .

## Finding Description
`verifyWorkflowAuthorization` is defined to accept `SecretsRequestParams` and reconstructs a Workflow-DON-signed quorum hash, verifying `2*F+1`/`F+1` signatures and cross-checking `params.Owner`/`params.WorkflowID` against the independently signed `PublicData` [4](#0-3) . This function is invoked only from `handleSecretsGet` and never from `handleCapabilityExecute`. `CapabilityRequestParams` carries no `SignedComputeRequests` field, confirmed by the test fixture that only sets `WorkflowID`, `Owner`, `ExecutionID`, `ReferenceID`, `CapabilityID`, `Payload` [5](#0-4) .

However, tracing the actual exploit path further changes the practical impact from what the claim asserts. The execution handler that `executeCapability` looks up is keyed only by `(workflowID, executionID)`, not owner [6](#0-5) , and that handler is registered by the node's own trusted workflow engine (`ConfidentialModule.Execute`) with the real, engine-known `workflowOwner`/`workflowID` [7](#0-6) . Critically, when the resolved handler actually invokes downstream capabilities via `ExecutionHelper.callCapability`, the `RequestMetadata.WorkflowOwner`/`WorkflowID` sent to the real capability are built from `c.cfg.WorkflowOwner`/`c.cfg.WorkflowID` — trusted, engine-registered values — not from the forged `params.Owner`/`params.WorkflowID` seeded into `ctx` by `handleCapabilityExecute` [8](#0-7) . This means a forged `Owner`/`OrgID` cannot redirect which tenant's capability actually executes or cause the capability call itself to run under a forged identity — that binding is anchored elsewhere and unaffected by this gap.

What the forged `Owner`/`OrgID`/`Workflow` *does* affect is (a) tenant-scoped limiters/settings that read `contexts.CRE` from the seeded context — the handler test explicitly notes "every tenant-scoped limiter downstream fails closed rather than reading a limit" without the correct CRE tenant, implying downstream limiter lookups key off this (forgeable) context value [9](#0-8) , and (b) the signed response itself, which is hashed and signed over `params` (including the forged `Owner`) via `signCapabilityResponse` [10](#0-9) , meaning this node would produce a validly signed relay response asserting a false tenant identity for a real execution.

## Impact Explanation
Given a compromised enclave (the same precondition `handleSecretsGet`'s PRIV-433 comment defends against), the missing check lets the enclave misattribute tenant-scoped rate-limit/metering context and produce signed relay capability responses that assert an incorrect `Owner`/`OrgID`/`WorkflowID`. This is a real inconsistency with the sibling code path and could corrupt cross-user attribution of limiter consumption or signed audit/response data — an in-scope "cross-user response corruption" concern. It is narrower than the report's claim that the capability itself "executes... under the attacker-chosen identity," since the actual `CallCapability` invocation uses engine-trusted `WorkflowOwner`/`WorkflowID`, not the ctx-seeded values, so capability execution/fund-movement authorization for the downstream capability itself is not bypassed.

## Likelihood Explanation
Requires a compromised enclave process — matching the exact threat model the codebase's own `verifyWorkflowAuthorization` comment defends against for `handleSecretsGet`, and requires the enclave to hold a genuine, already-registered `(workflowID, executionID)` pair on this node (i.e., it can only misattribute tenant context for an execution actually running, not arbitrary workflows). Not exploitable by a fully external unauthenticated actor without both a valid attestation and a real in-flight execution.

## Recommendation
Add a Workflow-DON-signed authorization check to `handleCapabilityExecute` analogous to `verifyWorkflowAuthorization`, binding `params.Owner`/`params.OrgID`/`params.WorkflowID` to an independently signed source before seeding `contexts.WithCRE` or including them in the signed response, closing the same class of gap that `handleSecretsGet` already closes.

## Proof of Concept
1. Compromise the enclave process so it can produce a genuinely-attested `MethodCapabilityExec` request for a `(workflowID, executionID)` pair that is legitimately registered on the target node via `ConfidentialModule.Execute`.
2. Set `params.Owner`/`params.OrgID` to a victim tenant's identifiers while keeping attestation and `EnclaveConfig` internally self-consistent.
3. Observe that `verifyAttestationHash` and `verifyEnclaveConfigMatchesDON` pass (they only check internal consistency), and no equivalent of `verifyWorkflowAuthorization` runs.
4. Confirm the resulting `contexts.CRE` seeded for downstream limiter lookups, and the `SignedCapabilityResponseResult` produced by `signCapabilityResponse`, carry the forged `Owner`/`OrgID`, while the actual `CallCapability` invocation to the downstream capability still uses the real, engine-trusted `WorkflowOwner` (verifiable via a unit test on `capability_executor.go`'s `callCapability` comparing `RequestMetadata.WorkflowOwner` against `c.cfg.WorkflowOwner`, independent of the forged ctx CRE).

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

**File:** core/capabilities/confidentialrelay/handler.go (L579-583)
```go
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

**File:** core/capabilities/confidentialrelay/handler.go (L991-1000)
```go
func (h *Handler) signCapabilityResponse(
	params confidentialrelaytypes.CapabilityRequestParams,
	result confidentialrelaytypes.CapabilityResponseResult,
) (*confidentialrelaytypes.SignedCapabilityResponseResult, error) {
	if h.responseSigner == nil {
		return nil, errors.New("response signer not configured")
	}

	hash, err := result.Hash(params)
	if err != nil {
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

**File:** core/capabilities/confidentialrelay/execution_handlers.go (L53-61)
```go
// GetExecution returns the registered handler for (workflowID, execID) without
// waiting. Prefer GetExecutionWithWait on the relay callback path.
func (e *ExecutionHandlers) GetExecution(workflowID, execID string) (host.ExecutionHelperWithRawSecrets, bool) {
	key := wfexecID(workflowID, execID)
	e.mu.Lock()
	defer e.mu.Unlock()
	helper, ok := e.handlers[key]
	return helper, ok
}
```

**File:** core/services/workflows/v2/confidential_module.go (L155-156)
```go
	m.executionHandlers.AddExecution(m.workflowID, workflowExecutionID, rawSecretsHelper)
	defer m.executionHandlers.RemoveExecution(m.workflowID, workflowExecutionID)
```

**File:** core/services/workflows/v2/capability_executor.go (L212-228)
```go
	capReq := capabilities.CapabilityRequest{
		Payload:      request.Payload,
		Method:       request.Method,
		CapabilityId: request.Id,
		Metadata: capabilities.RequestMetadata{
			WorkflowOwner:            c.cfg.WorkflowOwner,
			WorkflowID:               c.cfg.WorkflowID,
			WorkflowExecutionID:      c.WorkflowExecutionID,
			WorkflowName:             c.cfg.WorkflowName.Hex(),
			WorkflowDonID:            localNode.WorkflowDON.ID,
			WorkflowDonConfigVersion: pinnedWorkflowDonConfigVersion,
			ReferenceID:              strconv.Itoa(int(request.CallbackId)),
			DecodedWorkflowName:      c.cfg.WorkflowName.String(),
			SpendLimits:              spendLimits,
			WorkflowTag:              c.cfg.WorkflowTag,
			ExecutionTimestamp:       c.ExecutionTimestamp,
		},
```

**File:** core/capabilities/confidentialrelay/handler_test.go (L466-474)
```go
				// Without the CRE tenants on the context, every tenant-scoped
				// limiter downstream fails closed rather than reading a limit.
				// Normalized(): WithCRE strips the owner's 0x prefix and lowercases
				// it, so the tenant key matches the one the engine path produces.
				assert.Equal(t, contexts.CRE{
					Org:      "org-1",
					Owner:    testOwner,
					Workflow: "wf-1",
				}.Normalized(), helper.lastCapabilityCRE)
```
