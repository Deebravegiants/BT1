### Title
Stale/Rotated Workflow Signer Keys Remain Valid For HTTP Trigger Authentication Due To Cross-Shard "First-Writer-Wins" Metadata Merge - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The gateway's `WorkflowMetadataHandler.syncMetadata` rebuilds the `authorizedKeys` map used to authenticate HTTP-trigger JSON-RPC requests (`Authorize`) from per-shard aggregated observations. Within a single shard, observations are correctly ordered "newest wins" by sequence number, but across shards the merge logic uses "first-registered-wins": once a `workflowID` is registered from one shard's aggregate, a later shard reporting the same workflow reference with newer (rotated) `AuthorizedKeys` is silently dropped instead of overriding the stale entry.

### Finding Description
`WorkflowMetadataAggregator.Collect` keys observations by the digest of the full `WorkflowMetadata` object (including `AuthorizedKeys`), so a workflow-owner key rotation produces a *new* digest/observation while the old one remains in `agg.observations` until it is reaped after `cleanupInterval` (default `defaultCleanUpPeriodMs` = 10 minutes) has elapsed without renewed node observations: [1](#0-0) 

`Aggregate()` returns all observations meeting the F+1 threshold, sorted newest-first by `sequence`, specifically so "workflows that were registered most recently take precedence": [2](#0-1) 

However, `WorkflowMetadataHandler.syncMetadata` iterates `h.shards` sequentially, and for each shard iterates that shard's already-sorted `Aggregate()` output, writing directly into the shared `authorizedKeys`/`workflowIDToRef` maps. There is no global re-sort/re-merge across shards: [3](#0-2) 

If shard A processes first and still has the pre-rotation observation (old `AuthorizedKeys`) reaching threshold (because it hasn't yet expired within the 10-minute cleanup window, or its nodes haven't observed the new registration yet), `workflowIDToRef[workflowID]` is set with the OLD keys. When shard B is processed afterward and reports the SAME `workflowReference` (owner/name/tag unchanged, only keys rotated) with the NEW keys, the code hits "Case 1" (`idExists == true` and `existingRef == workflowRef`) and only appends the shard to the fan-out list — it does **not** overwrite `authorizedKeys[workflowID]` with the newer key set: [4](#0-3) 

The resulting `h.authorizedKeys` map is then consumed directly by `Authorize()`, which is the sole gate deciding whether a JWT-signed HTTP trigger request is accepted for a given `workflowID`: [5](#0-4) 

This mirrors the Axelar `AxelarAuthWeighted` bug class: after a legitimate "operatorship transfer" (key rotation intended to revoke a compromised or retired signer), the old, no-longer-authorized signer set can still be accepted by the verification path — here because the aggregation logic never actively invalidates/overwrites a stale-but-still-quorate observation with a newer one from another shard.

### Impact Explanation
An attacker holding a private key that a workflow owner has explicitly rotated out (e.g., because it was compromised, or because signer set membership changed) can still submit a validly signed JWT and have `WorkflowMetadataHandler.Authorize` accept it as long as the stale observation persists in any shard's aggregator — up to the full `cleanupInterval` (10 minutes by default), and potentially longer if propagation of the new metadata across shard/node quorums is delayed. This is a concrete authentication bypass on the internet-facing gateway's HTTP trigger path, allowing an unauthorized signer to initiate workflow executions on behalf of a workflow the caller no longer legitimately controls.

### Likelihood Explanation
This does not require a malicious node or peer — it can occur under entirely honest operation whenever key rotation propagates asynchronously across the DON's shards (a normal, expected timing condition given the periodic pull/aggregation design, `MetadataPullIntervalMs` and `MetadataAggregationIntervalMs`). The only prerequisite is that a caller retains the old private key and issues a request during the propagation/cleanup window, which is realistic in a key-compromise-response scenario — precisely the scenario key rotation is meant to protect against.

### Recommendation
In `syncMetadata`, when merging observations for the same `workflowID`/`workflowReference` across shards, compare `sequence` (or another recency indicator) and always keep the most recent `AuthorizedKeys` set globally rather than the first one encountered while iterating `h.shards`. Concretely: collect all per-shard aggregated observations for a workflow first, then pick the one with the highest global sequence number before writing to `authorizedKeys`, `workflowRefToID`, and `workflowIDToRef`. Additionally, consider shortening/aligning `cleanupInterval` with the metadata pull/aggregation cadence so stale key observations are reaped promptly after a rotation.

### Proof of Concept
1. Workflow `W` (owner/name/tag fixed) is registered with `AuthorizedKeys = [K_old]`; this reaches quorum on both shard A and shard B, with the observation's digest `D_old`.
2. The workflow owner rotates keys to `[K_new]`; nodes begin pushing/pulling the new metadata (`D_new`).
3. Due to network/propagation timing, shard A's aggregator still reports `D_old` (not yet reaped — within `cleanupInterval`) while shard B's aggregator has already converged on `D_new`.
4. `syncMetadata` runs: shard A is processed first (per `h.shards` order), registering `authorizedKeys[W] = {K_old}`. Shard B is then processed, sees the same `workflowReference`, hits "Case 1", and merely appends to `workflowShards[W]` without updating `authorizedKeys[W]`.
5. An attacker who still holds `K_old`'s private key signs a JWT and sends an HTTP trigger request for workflow `W`. `Authorize()` looks up `h.authorizedKeys[W]`, finds `K_old` still present, and accepts the request — despite the workflow owner having rotated it out.

### Citations

**File:** core/services/gateway/common/aggregation/workflow_metadata_aggregator.go (L50-79)
```go
func (agg *WorkflowMetadataAggregator) reapObservations(ctx context.Context) {
	agg.mu.Lock()
	defer agg.mu.Unlock()
	now := time.Now()
	var expiredCount int
	for node, digestObservedAt := range agg.observedAt {
		for digest, observedAt := range digestObservedAt {
			if now.Sub(observedAt) > agg.cleanupInterval {
				delete(agg.observedAt[node], digest)
				if len(agg.observedAt[node]) == 0 {
					delete(agg.observedAt, node)
				}
				_, ok := agg.observations[digest]
				if !ok {
					agg.lggr.Warnw("Observation digest not found in observations", "digest", digest, "node", node)
					continue
				}
				agg.observations[digest].nodes.Remove(node)
				if len(agg.observations[digest].nodes) == 0 {
					delete(agg.observations, digest)
				}
				expiredCount++
			}
		}
	}
	if expiredCount > 0 {
		agg.metrics.IncrementMetadataObservationsCleanUpCount(ctx, int64(expiredCount), agg.lggr)
		agg.lggr.Debugw("Removed expired callbacks", "count", expiredCount)
	}
	agg.metrics.RecordMetadataObservationsCount(ctx, int64(len(agg.observations)), agg.lggr)
```

**File:** core/services/gateway/common/aggregation/workflow_metadata_aggregator.go (L143-177)
```go
// Aggregate returns the aggregated workflow metadata for workflows that have reached the threshold.
// Results are sorted chronologically by sequence number (newest first, oldest last).
func (agg *WorkflowMetadataAggregator) Aggregate() []gateway_common.WorkflowMetadata {
	agg.mu.RLock()
	defer agg.mu.RUnlock()

	type aggregatedObs struct {
		metadata gateway_common.WorkflowMetadata
		sequence uint64
	}

	var toSort []aggregatedObs
	for _, nodeObs := range agg.observations {
		if len(nodeObs.nodes) >= agg.threshold {
			toSort = append(toSort, aggregatedObs{
				metadata: *nodeObs.observation,
				sequence: nodeObs.sequence,
			})
		}
	}

	// Sort chronologically (newest first) so that workflows that were registered most recently
	// takes precedence
	sort.Slice(toSort, func(i, j int) bool {
		return toSort[i].sequence > toSort[j].sequence
	})

	// Extract just the metadata
	aggregated := make([]gateway_common.WorkflowMetadata, len(toSort))
	for i, obs := range toSort {
		aggregated[i] = obs.metadata
	}

	return aggregated
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
