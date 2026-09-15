### Title
Missing ownership check on `TriggerID` allows any workflow to hijack or permanently break another workflow's web-api trigger registration - (File: core/capabilities/webapi/trigger/trigger.go)

### Summary
The `webapi` trigger capability's `triggerConnectorHandler` stores all trigger registrations in a single global map keyed only by the caller-supplied `TriggerID` string, with no binding to the workflow (owner) that registered it. `RegisterTrigger` rejects a request if that key already exists, and `UnregisterTrigger` deletes/tears down an entry looked up solely by `TriggerID`, without ever checking that `req.Metadata.WorkflowID` matches the workflow that originally created the registration. This mirrors the audited `MeritDutchAuction` bug class: a shared, sequentially/globally-namespaced identifier with no per-owner exclusivity check lets any equally-unprivileged actor pre-empt or destroy another party's use of that identifier, producing a permanent denial of service.

### Finding Description
`triggerConnectorHandler.RegisterTrigger` keys registrations purely by `req.TriggerID`: [1](#0-0) 
If any workflow (run on the node's capability engine, submitted by any workflow owner) registers first with a given `TriggerID`, every subsequent `RegisterTrigger` call using that same `TriggerID` — even from an entirely different, legitimate workflow owner — permanently fails with `"triggerId %s already registered"`.

Worse, `UnregisterTrigger` performs the same unscoped lookup and then closes/deletes the entry without verifying the caller's `WorkflowID`/owner against the stored `webapiTrigger.workflowID`: [2](#0-1) 
Because the only state kept for the owning workflow is `workflowID` on the struct, and it is never compared to `req.Metadata.WorkflowID`, any workflow that knows (or predictably guesses) another workflow's `TriggerID` can call `UnregisterTrigger` for it, closing the victim's trigger event channel (`webapiTrigger.ch`) and removing the map entry entirely.

This is directly analogous to the reported issue: the Merit NFT auction assumed exclusive control over sequential IDs by relying on a shared minter role without enforcing single-owner exclusivity, allowing any other privilege-holder to permanently break the intended flow by claiming the resource first. Here, the trigger connector assumes exclusive per-workflow ownership of a `TriggerID` namespace but never enforces it, allowing any other workflow with equal capability access to claim or tear down the same identifier.

### Impact Explanation
- Denial of service: a colliding `RegisterTrigger` call from an unrelated workflow permanently prevents the victim workflow's web-api trigger from ever registering (no retry path clears the stale/foreign entry).
- Cross-workflow disruption: `UnregisterTrigger` lets any workflow silently terminate another workflow's live trigger channel and remove its registration, stopping delivery of trigger events to the victim without the victim's consent or knowledge, matching the "permanently broken" impact class from the source report.

### Likelihood Explanation
Exploitation requires only that an attacker's workflow be executed by the capability engine (the same precondition needed for any workflow to use the `webapi` trigger) and that the attacker knows or predicts the victim's `TriggerID` (which may be visible in shared/public workflow definitions or follow a predictable convention). No elevated privileges beyond "submit a workflow" are required, matching the "unprivileged but role-shared" precondition of the original finding (multiple MINTER holders).

### Recommendation
Bind `TriggerID` registrations to the requesting `WorkflowID`/owner: store and check `req.Metadata.WorkflowID` (or a full owner+ID composite key) in both `RegisterTrigger` and `UnregisterTrigger`, and reject `UnregisterTrigger` calls whose `WorkflowID` does not match the stored owner of that `TriggerID`.

### Proof of Concept
1. Workflow A registers a web-api trigger with `TriggerID = "shared-id"` via `RegisterTrigger`, populating `h.registeredWorkflows["shared-id"]`. [3](#0-2) 
2. Workflow B (any other, unrelated workflow) calls `UnregisterTrigger` with the same `TriggerID = "shared-id"` and its own, unrelated `Metadata.WorkflowID`. Because no ownership check exists, the call succeeds, closing Workflow A's channel and deleting the registration. [2](#0-1) 
3. Workflow A stops receiving trigger events permanently, and any attempt by Workflow A to re-register can itself be pre-empted again by Workflow B repeating step 1, since `RegisterTrigger` also has no ownership check.

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L227-232)
```go
	h.mu.Lock()
	defer h.mu.Unlock()
	_, errBool := h.registeredWorkflows[req.TriggerID]
	if errBool {
		return nil, fmt.Errorf("triggerId %s already registered", req.TriggerID)
	}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L259-268)
```go
	h.registeredWorkflows[req.TriggerID] = &webapiTrigger{
		workflowID:     req.Metadata.WorkflowID,
		allowedTopics:  allowedTopicsMap,
		allowedSenders: allowedSendersMap,
		ch:             ch,
		config:         *reqConfig,
		rateLimiter:    rateLimiter,
	}

	return ch, nil
```

**File:** core/capabilities/webapi/trigger/trigger.go (L271-285)
```go
func (h *triggerConnectorHandler) UnregisterTrigger(ctx context.Context, req capabilities.TriggerRegistrationRequest) error {
	h.mu.Lock()
	defer h.mu.Unlock()
	workflow, ok := h.registeredWorkflows[req.TriggerID]
	if !ok {
		return fmt.Errorf("triggerId %s not registered", req.TriggerID)
	}

	workflow.chWriteMu.Lock()
	close(workflow.ch)
	workflow.ch = nil
	workflow.chWriteMu.Unlock()
	delete(h.registeredWorkflows, req.TriggerID)
	return nil
}
```
