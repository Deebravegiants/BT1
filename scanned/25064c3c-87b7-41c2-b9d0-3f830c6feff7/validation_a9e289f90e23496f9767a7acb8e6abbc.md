### Title
Stale periodically-synced `authorizedKeys` cache lets a revoked/rotated signer continue to authorize HTTP-trigger workflow requests - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The Sherlock report describes a pattern where a privileged action (buying/renewing protection) is gated on a status value that is cached and only refreshed by a separate, out-of-band process (`assessStateBatch`), so a stale cached status lets an operation proceed when the live/on-chain state would have rejected it. The Chainlink gateway's `WorkflowMetadataHandler.Authorize` exhibits the same structural weakness: authorization of an unprivileged, internet-facing HTTP-trigger request is gated purely on an in-memory `authorizedKeys` map that is refreshed only periodically (`syncMetadata`), not re-validated against current node/on-chain state at request time.

### Finding Description
`Authorize` performs signer authorization for inbound HTTP trigger requests solely against the cached map `h.authorizedKeys[workflowID]`: [1](#0-0) 

This map is populated by `syncMetadata`, which aggregates metadata pulled/pushed from workflow nodes on a periodic timer (`MetadataPullIntervalMs`, default 60s, plus `MetadataAggregationIntervalMs` for BFT aggregation) and then wholesale-replaces `h.authorizedKeys`: [2](#0-1) 

The default sync cadence is documented as periodic (1-minute) pull with aggregation on top: [3](#0-2) 

Because `Authorize` only consults this locally cached snapshot (and the JWT replay cache, and digest matching) rather than the live authoritative state on the workflow nodes/registry at request time, any change to a workflow's authorized signer set (e.g., a compromised or intentionally rotated/removed signer key) is not enforced until the next successful `syncMetadata` cycle completes. Until then, a request signed with the stale, no-longer-authorized key is accepted and forwarded to the DON exactly like the Carapace report where `getLendingPoolStatus` returns a stale `currentStatus` because `_assessState`/`assessStateBatch` hadn't run yet for that pool.

### Impact Explanation
An unprivileged network caller who possesses (or has retained) a private key that was authorized at some point but has since been revoked/rotated by the legitimate workflow owner can continue to submit valid, digest-matching, non-replayed JWTs and have them accepted by `Authorize` for up to the full metadata sync interval (default up to ~1 minute, potentially longer under aggregation delay or if pull responses are slow/partial). This is a concrete authentication/authorization bypass window: `Authorize` grants access based on state it knows to be potentially stale, exactly analogous to the reported "stale status allows action that should not be allowed." The result is unauthorized triggering of a workflow execution using a key the owner believed had been revoked — i.e., request impersonation / unauthorized job run for a bounded but real time window.

### Likelihood Explanation
This is reachable directly from an unprivileged client: any caller submitting an HTTP trigger request through the gateway hits `HandleUserTriggerRequest` → `Authorize`, using only public-facing inputs (JWT signed by a key + JSON-RPC request). Exploitation only requires that the attacker already knows/held a previously-authorized private key and that a revocation/rotation happened recently; no elevated or node-level privileges are needed. Likelihood is moderate: it depends on timing (must act within the sync window after revocation) but the window is deterministic and configuration-controlled (`MetadataPullIntervalMs`/`MetadataAggregationIntervalMs`), so it is a real and easily reproducible race rather than a purely theoretical one.

### Recommendation
- Reduce and bound the staleness window: shorten `MetadataPullIntervalMs`/`MetadataAggregationIntervalMs`, and/or trigger an immediate out-of-band metadata refresh when a workflow update/removal event is observed (push-based invalidation), rather than relying solely on the periodic pull.
- Consider re-validating signer authorization against a freshness marker (e.g., include a metadata version/nonce known to be current, or a max-staleness bound) before treating `Authorize` results as final for high-value actions.
- Ensure that when a workflow is unregistered/updated, `authorizedKeys` for the old key is proactively invalidated (e.g., via the registration/removal push path) instead of only being replaced wholesale on the next full periodic sync.
- Add explicit tests asserting that revoked keys are rejected immediately after a push-based unregistration event, independent of the pull timer.

### Proof of Concept
1. Workflow owner registers workflow `W` with authorized signer key `K1`; gateway's `syncMetadata` populates `authorizedKeys[W] = {K1}`.
2. Owner detects `K1` is compromised and updates the workflow on-chain/on-node to authorize only `K2`, removing `K1`.
3. Before the next `syncMetadata` cycle completes (bounded by `MetadataPullIntervalMs`/`MetadataAggregationIntervalMs`, default up to ~60s+), an attacker who has `K1` submits an HTTP trigger request signed with `K1`.
4. `WorkflowMetadataHandler.Authorize` ( [4](#0-3) ) still finds `K1` in the stale `authorizedKeys[W]` map and returns success, so the gateway forwards the (now-unauthorized) trigger request to the DON for execution — reproducing the "acted on stale cached authorization state" bug class from the report.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L110-182)
```go
// syncMetadata aggregates the authorized keys and workflow selectors from each
// shard's WorkflowMetadataAggregator and updates the local cache. A workflow is
// considered assigned to a shard once that shard's aggregator reports it (i.e.
// F+1 of the shard's nodes observed it).
func (h *WorkflowMetadataHandler) syncMetadata(ctx context.Context) {
	authorizedKeys := make(map[string]map[gateway.AuthorizedKey]struct{})
	workflowRefToID := make(map[workflowReference]string)
	workflowIDToRef := make(map[string]workflowReference)
	workflowShards := make(map[string][]*shardEndpoint)

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

	h.mu.Lock()
	defer h.mu.Unlock()

	if len(h.workflowIDToRef) == 0 && len(workflowIDToRef) > 0 {
		latencyMs := time.Since(h.startTime).Milliseconds()
		h.metrics.RecordMetadataSyncStartupLatency(ctx, latencyMs, h.lggr)
	}
	// Log all registered workflow IDs
	workflowIDs := make([]string, 0, len(workflowIDToRef))
	for workflowID := range workflowIDToRef {
		workflowIDs = append(workflowIDs, workflowID)
	}
	h.lggr.Debugw("Synced workflow metadata", "workflowIDs", workflowIDs, "count", len(workflowIDs))

	h.authorizedKeys = authorizedKeys
	h.workflowRefToID = workflowRefToID
	h.workflowIDToRef = workflowIDToRef
	h.workflowShards = workflowShards
	h.metrics.RecordLoadedMetadataSize(ctx, int64(len(h.workflowIDToRef)), h.lggr)
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L96-118)
```markdown
#### 5.1.1 Metadata Push (Registration Events)
- **Trigger**: Workflow registration event
- **Process**: HTTP capability nodes push workflow metadata to gateway

#### 5.1.2 Metadata Pull (Periodic Sync)
- **Trigger**: Periodic timer (default 1 minute intervals)
- **Process**: Gateway requests metadata from all HTTP capability nodes, which respond with batches of workflow metadata.

### 5.2 Aggregation Logic

The aggregation system (located in `/core/services/gateway/common/aggregation/`) implements Byzantine fault-tolerant metadata collection:

1. **Observation Collection**: Each node's metadata is hashed and stored by digest
2. **Threshold Consensus**: Requires f+1 identical observations (where f is max faulty nodes)
3. **Duplicate Prevention**: Ensures unique workflow ID and reference mappings
4. **Periodic Cleanup**: Removes expired observations to prevent memory leaks

### 5.3 Synchronization Flow

1. **Collection**: Nodes submit metadata observations
2. **Aggregation**: Aggregator identifies consensus metadata (f+1 agreements)
3. **Sync**: Gateway updates local cache with aggregated metadata
4. **Cleanup**: Expired observations are removed periodically
```
