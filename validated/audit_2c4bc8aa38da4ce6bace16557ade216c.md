### Title
Workflow name-based routing resolves to an ambiguous "winner" workflow when multiple workflows share the same (owner, name, tag) reference - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The HTTP Trigger Gateway resolves an unprivileged caller's workflow-execution request either by explicit `workflowID` or, when the caller omits it, by the tuple `(workflowOwner, workflowName, workflowTag)`. The mapping from that tuple to a concrete `workflowID` is built by `syncMetadata`, which deduplicates conflicting observations with a "first-wins" rule based on the non-deterministic order metadata is aggregated in, not on any authoritative uniqueness guarantee. This mirrors the Capgo bug class: multiple "public" (same-reference) entities are allowed to coexist, and an unnamed/implicit client request silently resolves to a single, non-deterministically chosen winner.

### Finding Description
`httpTriggerHandler.resolveWorkflowID` accepts requests that specify a workflow either by ID or by name/owner/tag: [1](#0-0) 

When no `workflowID` is given, resolution goes through `WorkflowMetadataHandler.workflowRefToID`, a map keyed by `workflowReference{workflowOwner, workflowName, workflowTag}`: [2](#0-1) 

That map is (re)built periodically in `syncMetadata` from BFT-aggregated per-shard observations. Critically, if two *different* `workflowID`s are observed with the *same* `workflowReference`, the code applies "first registered wins" purely based on iteration/aggregation order, dropping the other silently: [3](#0-2) 

This is confirmed by the test `TestSyncMetadataMultipleWorkflows`, whose own comments state the ambiguity explicitly: two workflow IDs share one reference, and whichever one is aggregated last/first "wins" the reference, with the loser silently dropped — an outcome driven by aggregation order rather than any owner/administrator intent: [4](#0-3) 

There is no code shown enforcing that `(workflowOwner, workflowName, workflowTag)` is globally unique before this point — the comment in the test says "the workflow reference is unique (enforced by the on-chain registry)", but the gateway code itself does not perform this validation; it defensively handles the case where the invariant is violated by picking an arbitrary winner instead of rejecting the ambiguous state or requiring the caller to disambiguate by ID.

This is structurally identical to the Capgo issue: an authorized entity (a workflow owner, analogous to the "channel manager") can end up with multiple live "public" identities that share the same client-facing selector (name/tag), and an unprivileged/"unnamed" request (one that specifies the tuple instead of the ID) is silently routed to whichever workflow won the internal resolution race — not necessarily the one the owner or the caller intended.

### Impact Explanation
An unprivileged HTTP-trigger caller who addresses a workflow by `(owner, name, tag)` instead of by explicit `workflowID` can have their request routed to the wrong workflow execution target if two workflow registrations end up sharing the same reference (e.g., during workflow updates/redeploys, races between old and new workflow versions, or reconciliation edge cases in the workflow registry syncer). Because routing determines which workflow's authorized keys (`authorizedKeys[workflowID]`), rate limits, and execution logic apply, this can result in:
- Requests being authorized/executed against an unintended workflow version (integrity/routing confusion),
- One workflow's registration silently "winning" and shadowing another with the same public name, undermining the predictability the workflow-name based addressing scheme is supposed to provide.

This does not directly leak secrets or bypass authentication (the JWT/authorized-key check for the *resolved* workflow ID still applies), so the impact is scoped to release/routing integrity rather than a full auth bypass — analogous to the "Medium" severity of the original Capgo finding, which is about integrity of routing, not confidentiality.

### Likelihood Explanation
Likelihood depends on how easily two workflow registrations can end up with an identical `(owner, name, tag)` reference simultaneously. The gateway code path does not itself prevent this; it assumes uniqueness is enforced elsewhere (per the test comment, "enforced by the on-chain registry"). If that upstream invariant is ever violated (e.g., a brief window during workflow redeploy/tag reuse, or a source-syncer state where two `WorkflowID`s transiently map to the same reference before the registry is fully reconciled), an unprivileged caller using name-based addressing during that window is silently routed based on message-arrival/aggregation order — not on any authorized decision. Since this only requires an ordinary HTTP-trigger request from any client that knows a workflow's owner/name/tag (all of which can be public/discoverable), triggering the ambiguity requires no privileged access, only that the ambiguous state exists upstream.

### Recommendation
- In `syncMetadata`, when a reference collision between two different `workflowID`s is detected, do not silently pick a winner: either reject name-based resolution for that reference entirely (return "workflow not found/ambiguous") until the collision is resolved, or require an explicit `workflowID` for that reference until uniqueness is restored.
- Add defense-in-depth validation that a `(workflowOwner, workflowName, workflowTag)` reference is unique to a single active `workflowID` at the point the workflow registry syncer feeds this handler, rather than only relying on an assumed on-chain invariant.
- Log/alert (not just debug-log) when a reference collision occurs, since it indicates either a bug in the reconciliation logic or a registry invariant violation that should be investigated.
- Consider deprecating implicit name/tag-based resolution for security-sensitive execution paths in favor of requiring explicit `workflowID`, removing the ambiguity class entirely.

### Proof of Concept
1. Two workflow registrations (e.g., during a workflow redeploy, or via a race in reconciliation) end up producing metadata observations with the same `(workflowOwner, workflowName, workflowTag)` but different `workflowID`s (`wfA`, `wfB`).
2. `WorkflowMetadataHandler.syncMetadata` aggregates observations per shard; per the documented behavior, whichever `workflowID` is processed first in the "newest-first" aggregated order wins the reference-to-ID mapping (`workflowRefToID`), and the other is dropped (see `TestSyncMetadataMultipleWorkflows`).
3. An unprivileged client sends an HTTP trigger request specifying only `WorkflowOwner`, `WorkflowName`, `WorkflowTag` (no `WorkflowID`) via `httpTriggerHandler.HandleUserTriggerRequest` → `resolveWorkflowID`.
4. The gateway resolves the request to whichever of `wfA`/`wfB` won the aggregation race, and authorizes/executes against that workflow — a hidden, non-deterministic implementation detail — rather than the workflow the caller or the currently-intended owner state implies.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L23-27)
```go
type workflowReference struct {
	workflowOwner string
	workflowName  string
	workflowTag   string
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L120-162)
```go
	for _, shard := range h.shards {
		agg := h.aggs[shard.donID]
		metadata := agg.Aggregate()
		for _, data := range metadata {
			workflowID := data.WorkflowSelector.WorkflowID
			workflowRef := workflowReference{
				workflowOwner: data.WorkflowSelector.WorkflowOwner,
				workflowName:  data.WorkflowSelector.WorkflowName,
				workflowTag:   data.WorkflowSelector.WorkflowTag,
			}

			// Case 1: this workflow ID was already registered. If the reference
			// matches, this is the same workflow reported by another shard —
			// append the shard to its fan-out list. If the reference differs,
			// it's a conflicting observation; drop it.
			if existingRef, idExists := workflowIDToRef[workflowID]; idExists {
				if existingRef == workflowRef {
					workflowShards[workflowID] = append(workflowShards[workflowID], shard)
				} else {
					h.lggr.Debugw("Duplicate workflow ID with conflicting reference, dropping",
						"workflowID", workflowID, "existingRef", existingRef, "conflictingRef", workflowRef)
				}
				continue
			}

			// Case 2: this workflow reference was already registered under a
			// different workflow ID. First-wins by reference; drop the duplicate.
			if _, refExists := workflowRefToID[workflowRef]; refExists {
				h.lggr.Debugw("Duplicate workflow reference found, dropping",
					"workflowRef", workflowRef, "workflowID", workflowID)
				continue
			}

			// Case 3: new workflow ID and reference — register it.
			workflowIDToRef[workflowID] = workflowRef
			workflowRefToID[workflowRef] = workflowID
			authorizedKeys[workflowID] = make(map[gateway.AuthorizedKey]struct{})
			for _, key := range data.AuthorizedKeys {
				authorizedKeys[workflowID][key] = struct{}{}
			}
			workflowShards[workflowID] = append(workflowShards[workflowID], shard)
		}
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler_test.go (L160-185)
```go
	expectedRef := workflowReference{
		workflowName:  testWorkflowNameHex1,
		workflowOwner: testWorkflowOwner1,
		workflowTag:   testWorkflowTag1,
	}
	// Both "workflow1" and "workflow2" share the same workflow reference. The
	// workflow reference is unique (enforced by the on-chain registry), so
	// syncMetadata deduplicates by reference: only the first observed workflow ID
	// wins. Aggregate() returns observations newest-first, so "workflow2" (the
	// last collected, highest sequence number) is processed first and wins the
	// reference; "workflow1" is dropped as a duplicate reference.
	require.Len(t, handler.authorizedKeys, 1)
	require.Contains(t, handler.authorizedKeys, "workflow2")
	workflowKeys := handler.authorizedKeys["workflow2"]
	require.Len(t, workflowKeys, 1)

	ref, exists := handler.workflowIDToRef["workflow2"]
	require.True(t, exists)
	require.Equal(t, expectedRef, ref)
	winningWorkflowID, exists := handler.workflowRefToID[expectedRef]
	require.True(t, exists)
	require.Equal(t, "workflow2", winningWorkflowID)
	// "workflow1" must have been dropped by the reference dedup.
	_, exists = handler.workflowIDToRef["workflow1"]
	require.False(t, exists)
}
```
