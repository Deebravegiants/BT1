### Title
Revoked/rotated workflow signer keys remain authorized to trigger workflow execution for up to the full metadata sync window - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The Unlock refund bug (calculating refunds off the *current* key price instead of the price actually paid) is a stale-state-used-for-a-financial/authorization-decision bug class. The Chainlink HTTP-trigger gateway has the same class of bug in JWT signer authorization: `WorkflowMetadataHandler.Authorize` checks a signer's ECDSA key against a locally cached `authorizedKeys` map that is refreshed only periodically (via node metadata pull + BFT aggregation), not against the current on-chain/authoritative state at request time.

### Finding Description
`WorkflowMetadataHandler.Authorize` validates an inbound HTTP-trigger JWT and then authorizes the signer purely by looking it up in the in-memory `h.authorizedKeys[workflowID]` map: [1](#0-0) 

That map is populated by `syncMetadata`, which overwrites the handler's view of authorized keys wholesale from the latest BFT-aggregated observations pulled from workflow-capability nodes: [2](#0-1) 

The pull/aggregation cadence is periodic and coarse-grained by default (1 minute for metadata pull, 1 minute for aggregation): [3](#0-2) 

There is no mechanism in `Authorize` to detect or reject a key that has since been revoked/rotated at the source of truth (workflow registration/metadata) but has not yet propagated through the pull → aggregate → `syncMetadata` pipeline. This is structurally identical to the Unlock bug: an authorization-relevant value (key price / authorized signer set) can change at the source of truth, but the enforcement code path (`refund()` / `Authorize()`) consults a stale snapshot instead of the current state, producing a decision that no longer matches reality.

### Impact Explanation
If a workflow owner rotates out a compromised or departing signer's key (updating the workflow's authorized-signer metadata), the old key remains valid for gateway-side JWT authorization until the next successful metadata pull + aggregation cycle completes for every gateway node. During that window (up to ~2 default cycles, i.e., minutes), an unprivileged holder of the old/revoked key can still forge a valid, digest-bound JWT (`utils.VerifyRequestJWT`) and successfully call `MethodWorkflowExecute` against the workflow, since `Authorize` only checks the stale local map, not the authoritative current authorized-key set. This is a concrete authentication/authorization-bypass window that can result in unauthorized workflow-trigger execution using credentials the owner believed were revoked.

### Likelihood Explanation
This is reachable by any unprivileged external client that possesses (or previously possessed) a signer's private key material and can reach the gateway's HTTP-trigger endpoint — no special network position or node compromise is required. The bug is deterministic (not probabilistic): it manifests every time a key is revoked, for the duration of the sync window, which is a fixed, non-trivial amount of time by default configuration.

### Recommendation
- When authorizing a request, avoid decisions purely against a periodically-refreshed local snapshot; either shorten and enforce a strict staleness bound with revocation-aware invalidation, or require a fresh confirmation for authorization changes (e.g., a monotonically increasing revocation/version counter per workflow that must be observed before honoring older authorizations).
- Consider pushing revocation events immediately (out-of-band from the periodic pull) so that key removal takes effect immediately gateway-wide rather than waiting for the next scheduled sync.
- At minimum, document and bound the maximum "authorization staleness window" and make it configurable to a much smaller value for security-sensitive deployments, and add metrics/alerts for gateways whose metadata sync is falling behind (which would silently widen the exposure window).

### Proof of Concept
1. Register a workflow with authorized signer key `K1` (owner uses `K1` to sign trigger JWTs). `syncMetadata` populates `authorizedKeys[workflowID] = {K1}`. [4](#0-3) 
2. Workflow owner rotates the signer to `K2` and removes `K1`, updating the authoritative workflow registry/metadata source.
3. Because gateway-side propagation depends on the periodic pull (`defaultMetadataPullIntervalMs = 60000`) and aggregation (`defaultMetadataAggregationIntervalMs = 60000`) cycle: [3](#0-2) 
   the gateway's `h.authorizedKeys[workflowID]` still contains `K1` until the next successful `syncMetadata` call.
4. During this window, an attacker holding `K1` signs a `MethodWorkflowExecute` JWT for the workflow; `Authorize` finds `K1` still present in the stale map and returns success, allowing the (supposedly revoked) key to trigger workflow execution: [5](#0-4) 

Note: I could not fully verify the JWT's own `exp` (expiry) claim lifetime and whether any additional short-TTL constraint independently narrows this window, since the exact `utils.CreateRequestJWT`/`VerifyRequestJWT` claim-expiry logic in `core/utils/jwt.go` was not retrievable in full detail from the indexed context. If those JWTs are extremely short-lived (seconds) and bound to a fresh nonce/timestamp requirement enforced elsewhere, the practical exploitation window could be smaller than the full metadata-sync interval; this should be confirmed by reviewing `core/utils/jwt.go` directly in a full checkout.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-107)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L36-39)
```go
	defaultMultiplier                    = 2.0
	defaultMetadataPullIntervalMs        = 1000 * 60 // 1 minute
	defaultMetadataAggregationIntervalMs = 1000 * 60 // 1 minute
	defaultMetadataPullRequestTimeoutMs  = 1000 * 30 // 30 seconds
```
