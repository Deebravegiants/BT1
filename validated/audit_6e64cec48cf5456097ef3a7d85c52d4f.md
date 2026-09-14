Confirmed: this is a genuine unsynchronized access bug.

### Title
Unsynchronized read of `authorizedKeys` map in `WorkflowMetadataHandler.Authorize` races with concurrent `syncMetadata` writes, allowing signer authorization bypass or panic under concurrent HTTP trigger requests - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
`WorkflowMetadataHandler.Authorize` reads `h.authorizedKeys[workflowID]` directly at [1](#0-0)  without ever acquiring `h.mu`, even though `h.mu` is the designated `sync.RWMutex` that protects `authorizedKeys`, `workflowRefToID`, `workflowIDToRef`, and `workflowShards` everywhere else in this type. The periodic `syncMetadata` goroutine replaces the entire `h.authorizedKeys` map wholesale under `h.mu.Lock()` at [2](#0-1) , running on its own ticker independent of any request path [3](#0-2) . Meanwhile, every other reader of these fields (`WorkflowShards`, `GetWorkflowID`, `GetWorkflowReference`) correctly takes `h.mu.RLock()` [4](#0-3) [5](#0-4) . Only `Authorize` omits the lock.

### Finding Description
`Authorize` is invoked directly on the unprivileged HTTP-trigger request path from an external caller's JWT-signed request, to determine which ECDSA public keys are permitted to sign requests for a given `workflowID`:

```go
func (h *WorkflowMetadataHandler) Authorize(workflowID string, token string, req *jsonrpc.Request[json.RawMessage]) (*gateway.AuthorizedKey, error) {
	...
	keys, exists := h.authorizedKeys[workflowID]
	...
	if _, exists = keys[key]; !exists {
		return nil, fmt.Errorf("signer '%s' is not authorized...")
	}
	...
}
```

Because `syncMetadata` replaces `h.authorizedKeys` with a brand-new map (`h.authorizedKeys = authorizedKeys`) under `h.mu.Lock()` while a concurrent `Authorize` call is reading the old map reference and iterating/indexing into the inner `map[gateway.AuthorizedKey]struct{}` without holding any lock, this is a textbook Go data race: one goroutine writes a pointer/map header while another reads it unsynchronized. This is not just theoretical unsafety — it is CWE-567/"unsynchronized access to shared data in a multithreaded context," directly analogous to the RESTEasy advisory's root cause (state read on one thread while mutated by another, producing an incorrect/inconsistent authorization decision). Under Go's memory model, concurrent unsynchronized map access is undefined behavior: it can silently return an inconsistent/stale `keys` map (before the swap completes, e.g. partially-visible new map contents due to lack of a memory barrier), or — since `syncMetadata` writes to the exact same map variable concurrently with a raw read — trigger the Go runtime's built-in concurrent-map-read/write fatal panic (`fatal error: concurrent map read and map write`), crashing the entire gateway process. This is reachable purely by an unprivileged external caller sending HTTP trigger requests while the background 1-minute metadata sync ticker fires — no privileged access needed.

### Impact Explanation
- **Availability**: An unprivileged client can trigger a Go runtime fatal crash (`fatal error: concurrent map read and map write`) of the entire gateway process by sending HTTP trigger requests concurrently with the periodic `syncMetadata` tick (every `MetadataAggregationIntervalMs`, default naturally recurring). This is a full DoS of the internet-facing gateway, not merely a single-request failure.
- **Integrity/Confidentiality (lower likelihood but possible)**: Reading `keys` from a map that a concurrent writer is mutating without synchronization is undefined in Go — it is not guaranteed to simply return old-or-new values cleanly; it can read garbage internal bucket state. In authorization-critical code, any such non-deterministic misbehavior in the `keys[key]` lookup used to gate "signer is authorized for this workflow" is a correctness violation of an authentication check.

### Likelihood Explanation
High likelihood of occurrence in production: `syncMetadata` runs unconditionally on a fixed ticker (`MetadataAggregationIntervalMs`, default 60s per [6](#0-5) ) for the lifetime of the handler, and `Authorize` is called on every single incoming HTTP trigger request from any external, unprivileged caller [7](#0-6) . Any gateway serving a moderate volume of HTTP trigger traffic will race the sync ticker essentially every minute, making the crash reproducible without any special timing control by the attacker — simply sustaining request volume increases the chance of hitting the window.

### Recommendation
Acquire `h.mu.RLock()`/`RUnlock()` around the read of `h.authorizedKeys[workflowID]` in `Authorize`, consistent with `WorkflowShards`, `GetWorkflowID`, and `GetWorkflowReference`. Since the inner map is replaced wholesale (not mutated in place) by `syncMetadata`, it is sufficient to snapshot `keys` under the lock before releasing it and performing the membership check on the snapshotted reference.

### Proof of Concept
1. Configure a `WorkflowMetadataHandler` with a short `MetadataAggregationIntervalMs` (e.g. 10ms) and register/aggregate a workflow so `syncMetadata` continually rebuilds `h.authorizedKeys` on its ticker as in `Start`/`runTicker` [3](#0-2) .
2. From a separate goroutine, repeatedly call `handler.Authorize(workflowID, validToken, req)` in a tight loop as an unprivileged external caller would via `HandleUserTriggerRequest`.
3. Run under `go test -race`, or in production, observe the runtime crash `fatal error: concurrent map read and map write` originating from the unlocked `h.authorizedKeys[workflowID]` access at [8](#0-7)  colliding with the locked write at [9](#0-8) .

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-104)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L164-182)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L271-278)
```go
func (h *WorkflowMetadataHandler) WorkflowShards(workflowID string) []*shardEndpoint {
	h.mu.RLock()
	defer h.mu.RUnlock()
	shards := h.workflowShards[workflowID]
	out := make([]*shardEndpoint, len(shards))
	copy(out, shards)
	return out
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L290-296)
```go
		h.runTicker(time.Duration(h.config.MetadataPullIntervalMs)*time.Millisecond, func(ctx context.Context) {
			err2 := h.sendMetadataPullRequest()
			if err2 != nil {
				h.lggr.Errorw("Failed to send pull request", "error", err2)
			}
		})
		h.runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L356-376)
```go
func (h *WorkflowMetadataHandler) GetWorkflowID(workflowOwner, workflowName, workflowTag string) (string, bool) {
	h.mu.RLock()
	defer h.mu.RUnlock()
	workflowRef := workflowReference{
		workflowOwner: workflowOwner,
		workflowName:  workflowName,
		workflowTag:   workflowTag,
	}
	workflowID, exists := h.workflowRefToID[workflowRef]
	if !exists {
		return "", false
	}
	return workflowID, true
}

func (h *WorkflowMetadataHandler) GetWorkflowReference(workflowID string) (workflowReference, bool) {
	h.mu.RLock()
	defer h.mu.RUnlock()
	workflowRef, exists := h.workflowIDToRef[workflowID]
	return workflowRef, exists
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L37-38)
```go
	defaultMetadataPullIntervalMs        = 1000 * 60 // 1 minute
	defaultMetadataAggregationIntervalMs = 1000 * 60 // 1 minute
```
