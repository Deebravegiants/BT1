### Title
Stale cached `authorizedKeys` map allows use of revoked signer keys to authorize HTTP Trigger requests - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The `WorkflowMetadataHandler.Authorize` function checks an incoming JWT-signed request's signer against a locally cached `authorizedKeys` map that is only refreshed on a periodic pull/aggregation cycle, not read fresh at request time. This mirrors the reported `op-eco` `inflationMultiplier` bug class: a security-relevant value (there, an inflation multiplier; here, a workflow's authorized-signer allowlist) is fetched/refreshed asynchronously and cached, and requests are authorized against that stale cache rather than the current source of truth, allowing an unprivileged actor holding a since-revoked key to still pass authorization during the staleness window.

### Finding Description
`Authorize` validates a request's JWT signature and then checks the recovered signer against `h.authorizedKeys[workflowID]`: [1](#0-0) 

This map is populated exclusively by `syncMetadata`, which runs periodically and completely replaces `h.authorizedKeys` based on the aggregated results of the most recent metadata pull: [2](#0-1) 

The pull and aggregation cycles are driven by independent tickers configured via `MetadataPullIntervalMs` and `MetadataAggregationIntervalMs` (default 60 seconds each per the module README), meaning `h.authorizedKeys` can lag the true, current set of authorized signers by up to the sum of both intervals: [3](#0-2) [4](#0-3) 

If a workflow owner rotates/revokes a signing key (e.g., because it was compromised, or an employee/service lost access), the gateway continues to accept requests signed by the old key until the next successful pull+aggregate cycle updates the cache — exactly analogous to how the L1 bridge kept using the stale `inflationMultiplier` until an explicit `rebase()` call refreshed it. Additionally, unlike `GetWorkflowID`/`GetWorkflowReference` which correctly take `h.mu.RLock()`, `Authorize` reads `h.authorizedKeys` at line 92 without acquiring `h.mu`, while `syncMetadata` writes it under `h.mu.Lock()` — a concurrent read/write race on the same map that can also produce inconsistent/incorrect authorization decisions or a runtime panic.

### Impact Explanation
An unprivileged actor who once possessed a legitimate signer key for a workflow retains the ability to successfully call `Authorize` — and therefore trigger workflow execution via `HTTPTriggerHandler` — for up to `MetadataPullIntervalMs + MetadataAggregationIntervalMs` (up to ~2 minutes by default) after that key has been revoked/rotated by the workflow owner. This is a concrete authorization/allowlist bypass: it allows unauthorized triggering of workflow execution using credentials the legitimate owner believes are no longer valid, which can cause unintended job runs, unauthorized use of DON resources tied to that workflow, or unauthorized access when key rotation was performed specifically to lock out a compromised or offboarded party.

### Likelihood Explanation
Likelihood is moderate-to-high in any environment where workflow signer keys are rotated or revoked (e.g., incident response after key compromise, personnel offboarding, key hygiene rotation). The bypass requires no special access beyond already knowing the previously-valid private key and being able to construct a validly formatted JSON-RPC request/JWT — both are available to any client who was previously an authorized signer. The staleness window is deterministic and configuration-driven, not a rare race condition, so an attacker who is aware of the rotation timing can reliably exploit it.

### Recommendation
- Do not treat the periodically-synced `authorizedKeys` cache as authoritative for security decisions without an explicit "freshness" or invalidation mechanism. Consider forcing a synchronous re-pull/verification against the DON (or at minimum invalidating cached keys for a workflow) when a key-rotation event is detected, rather than waiting for the next scheduled tick.
- Reduce the effective staleness window (shorter `MetadataPullIntervalMs`/`MetadataAggregationIntervalMs`) for authorization-relevant data, or separate authorization-critical data from the general metadata caching pipeline.
- Fix the missing `h.mu.RLock()` around the `h.authorizedKeys` read in `Authorize` (line 92) to eliminate the concurrent map access race with `syncMetadata`.
- Consider adding explicit key-revocation propagation (push-based invalidation) instead of relying solely on periodic pull/aggregate refresh.

### Proof of Concept
1. Workflow owner registers workflow `WF1` with authorized signer key `K1`; gateway's `syncMetadata` populates `h.authorizedKeys[WF1] = {K1}`.
2. Workflow owner rotates keys, removing `K1` and adding `K2` (e.g., because `K1` was compromised or the holder was offboarded). The DON nodes now report only `K2` as authorized for `WF1`.
3. Before the gateway's next `MetadataPullIntervalMs` + `MetadataAggregationIntervalMs` cycle completes (default up to ~2 minutes), an actor still holding `K1` crafts a JWT-signed HTTP Trigger request for `WF1`, including a correctly computed `request_digest`.
4. `WorkflowMetadataHandler.Authorize` (`workflow_metadata_handler.go:80-107`) verifies the JWT signature, checks `h.authorizedKeys[WF1]`, finds `K1` still present (stale cache), and returns success — the request is dispatched to DON nodes and the workflow is triggered, despite `K1` having been revoked.

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

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L159-171)
```markdown
### 6.4 Default Values

| Configuration | Default Value | Description |
|---------------|---------------|-------------|
| `CleanUpPeriodMs` | 600000 (10 min) | Cache and callback cleanup interval |
| `MaxTriggerRequestDurationMs` | 60000 (1 min) | Maximum time for trigger request processing |
| `MetadataPullIntervalMs` | 60000 (1 min) | Interval for pulling metadata from nodes |
| `MetadataAggregationIntervalMs` | 60000 (1 min) | Interval for aggregating collected metadata |
| `InitialIntervalMs` | 100 | Initial retry interval |
| `MaxIntervalTimeMs` | 30000 (30 sec) | Maximum retry interval |
| `Multiplier` | 2.0 | Exponential backoff multiplier |
| `OutboundRequestCacheTTLMs` | 600000 (10 min) | HTTP response cache TTL |

```
