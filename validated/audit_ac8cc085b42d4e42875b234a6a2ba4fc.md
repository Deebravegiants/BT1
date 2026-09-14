## Analog Found

### Title
Stale authorized-key cache allows revoked workflow signers to authenticate HTTP trigger requests during the metadata resync window - (File: `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

### Summary
The `WorkflowMetadataHandler` authorizes incoming HTTP-trigger JSON-RPC requests against an in-memory snapshot of `authorizedKeys` that is only refreshed on a periodic pull/aggregation cycle, not synchronously with on-chain/registry state changes. Just like the bribe/emissions desync in the report — where a voter's influence is locked in at a snapshot while later actions (bribe claim vs. emission distribution) reference different points in time — a workflow key that has been revoked or rotated remains valid for authenticating and triggering executions until the next metadata sync completes, up to roughly the combined pull + aggregation interval.

### Finding Description
`Authorize` checks the caller's recovered signer against the cached `h.authorizedKeys[workflowID]` map: [1](#0-0) 

This cache is only replaced by `syncMetadata`, which runs on a periodic ticker driven by `MetadataAggregationIntervalMs`, itself fed by periodic pull requests on `MetadataPullIntervalMs`: [2](#0-1) [3](#0-2) 

Both intervals default to 1 minute: [4](#0-3) 

The gateway's `httpTriggerHandler.authorizeRequest` calls this stale-tolerant `Authorize` directly on the unprivileged, internet-facing path for every incoming user trigger request: [5](#0-4) 

So if a workflow owner rotates or revokes a signing key (e.g., because it was compromised) via the on-chain `WorkflowRegistry`, any node's gateway will continue accepting JWTs signed by the old key for up to `MetadataPullIntervalMs + MetadataAggregationIntervalMs` (≈2 minutes by default) — a real "distribution happens on stale snapshot" desync, mirroring the report's root cause.

### Impact Explanation
An attacker holding a previously-authorized (now revoked/rotated) private key can continue to submit `workflows.execute` HTTP-trigger requests through the public gateway and have them accepted and dispatched to the DON, triggering workflow executions the legitimate owner believed were blocked. This is a concrete authentication/authorization bypass window on the unprivileged, internet-facing gateway path.

### Likelihood Explanation
Medium: it requires the attacker to already possess a key that was valid at some prior point and is now revoked (e.g. leaked key, employee offboarding, security rotation) and to act within the up-to-2-minute resync window after revocation. This is a realistic and commonly anticipated threat model for key rotation/revocation.

### Recommendation
Do not rely solely on a periodically-refreshed local cache for authorization decisions tied to security-sensitive state changes like key revocation. Options:
- Trigger an immediate out-of-band metadata refresh/invalidation when a revocation event is observed (e.g., via event subscription rather than polling), instead of waiting for the next tick.
- Shorten the aggregation/pull intervals specifically for revocation-sensitive paths, or add a "negative cache"/revocation list that is checked with lower latency than the full metadata sync.
- Document and bound the maximum staleness window explicitly, and consider treating `Authorize` failures as fail-closed if the cache age exceeds a safety threshold.

### Proof of Concept
1. Register a workflow with signer key `K1` as an authorized key; wait for `syncMetadata` to pick it up.
2. Rotate the workflow's authorized keys on-chain/registry to remove `K1` (e.g., simulate via whatever mechanism populates `OnMetadataPush`/`OnMetadataPullResponse`, replacing `K1` with `K2`).
3. Before the next `syncMetadata` tick completes (i.e., within `MetadataPullIntervalMs + MetadataAggregationIntervalMs`), send a `workflows.execute` request signed with `K1` through `HandleJSONRPCUserMessage` → `HandleUserTriggerRequest` → `authorizeRequest` → `WorkflowMetadataHandler.Authorize`.
4. Observe the request is accepted and dispatched to the DON despite `K1` no longer being authorized in the source of truth, because `h.authorizedKeys` still reflects the pre-rotation snapshot.

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L110-183)
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
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L280-307)
```go
// Start begins the periodic pull loop.
func (h *WorkflowMetadataHandler) Start(ctx context.Context) error {
	return h.StartOnce("WorkflowMetadataHandler", func() error {
		h.lggr.Info("Starting HTTP Trigger Metadata Handler")
		h.startTime = time.Now()
		for _, shard := range h.shards {
			if err := h.aggs[shard.donID].Start(ctx); err != nil {
				return fmt.Errorf("failed to start aggregator for shard %s: %w", shard.donID, err)
			}
		}
		h.runTicker(time.Duration(h.config.MetadataPullIntervalMs)*time.Millisecond, func(ctx context.Context) {
			err2 := h.sendMetadataPullRequest()
			if err2 != nil {
				h.lggr.Errorw("Failed to send pull request", "error", err2)
			}
		})
		h.runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)

		h.runTicker(h.jwtCache.cleanupPeriod, func(ctx context.Context) {
			now := time.Now()
			expiredCount := h.jwtCache.cleanupOldEntries(now.Add(-h.jwtCache.cleanupPeriod))
			h.metrics.IncrementJwtCacheCleanUpCount(ctx, int64(expiredCount), h.lggr)
			h.metrics.RecordJwtCacheSize(ctx, int64(len(h.jwtCache.cache)), h.lggr)
			h.lggr.Debugw("Workflow execution cache cleanup completed", "expired_entries", expiredCount, "remaining_entries", len(h.jwtCache.cache))
		})
		return nil
	})
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L37-39)
```go
	defaultMetadataPullIntervalMs        = 1000 * 60 // 1 minute
	defaultMetadataAggregationIntervalMs = 1000 * 60 // 1 minute
	defaultMetadataPullRequestTimeoutMs  = 1000 * 30 // 30 seconds
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-376)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
}
```
