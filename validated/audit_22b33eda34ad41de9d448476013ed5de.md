Based on my investigation, I found a genuine TOCTOU race condition in the vault/gateway's JWT replay-guard logic, in the same "threshold/state gate checked separately from state gate updated" bug class as the reported issue (where the final decision depends on interleaving of concurrent operations rather than an atomic check-and-set).

### Title
JWT replay guard is check-then-act (non-atomic), allowing a captured JWT to be replayed via concurrent requests - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
`WorkflowMetadataHandler.Authorize` is the entry point used by the HTTP Trigger gateway handler to authenticate unprivileged, internet-facing workflow-execution requests via JWT. Replay protection relies on `isReplay(claims.ID)` being checked, followed later by `recordUsage(claims.ID)` after other work (key/authorized signer lookup) completes. These are two independent, non-atomic operations, so concurrent requests carrying the same JWT (same `jti`) can both pass the `isReplay` check before either calls `recordUsage`.

### Finding Description
`Authorize` performs the checks in this order: [1](#0-0) 

1. Verify JWT signature (`utils.VerifyRequestJWT`).
2. Check replay via `h.jwtCache.isReplay(claims.ID)` — a read against the cache.
3. Look up authorized keys for the workflow and validate the signer.
4. Only after all that succeeds, call `h.jwtCache.recordUsage(claims.ID)` to mark the `jti` as used.

Because step 2 (check) and step 4 (record) are separate calls under separate lock acquisitions (`jwtReplayCache` uses `sync.RWMutex` with distinct read/write critical sections) rather than a single atomic check-and-set, two goroutines handling two concurrent HTTP trigger requests carrying an identical, previously-unused JWT can both observe `isReplay == false` and proceed to `recordUsage` afterward. This is structurally analogous to the reported Solidity bug: the "final" outcome (whether the JWT is treated as fresh or replayed) is determined by a race between concurrent operations on shared state rather than a single atomic transition, instead of a strict single-use guarantee.

### Impact Explanation
An attacker (or a legitimate client with a leaked/intercepted JWT) who fires the same signed JWT request twice in parallel at the gateway can cause both to be treated as valid, non-replayed requests, resulting in the workflow being triggered twice from what was intended/authorized as a single-use, one-time signed request. This undermines the single-use guarantee the replay cache is meant to provide and can lead to duplicate unauthorized workflow executions/duplicate fund-moving or state-changing actions triggered by a workflow, using only a single captured token.

### Likelihood Explanation
Exploitability requires only the ability to send two near-simultaneous HTTP requests with the same JWT to the gateway's HTTP trigger endpoint — this is entirely within reach of an unprivileged client and does not require any special network position, malicious peer, or operator access. The race window is small but real, and given automated/scripted concurrent request generation, this is reliably triggerable.

### Recommendation
Make the check-and-record operation atomic: acquire the write lock once and, in a single critical section, check whether `jti` already exists in the cache; if not, insert/record it immediately, returning "replay detected" if it was already present. Only proceed to signer/key validation after the atomic reservation succeeds (or perform the reservation immediately after JWT signature verification, before further authorization steps, and roll it back only if the request is otherwise invalid).

### Proof of Concept
1. Client signs a valid HTTP trigger JWT with `jti = X` for a valid, authorized workflow key.
2. Client sends two requests to the gateway HTTP trigger endpoint concurrently (e.g., via two parallel HTTP connections), each carrying the same JWT with `jti = X`.
3. Both requests reach `WorkflowMetadataHandler.Authorize` concurrently on the gateway.
4. Goroutine A calls `isReplay(X)` → `false` (not yet recorded). Before A calls `recordUsage(X)`, goroutine B also calls `isReplay(X)` → still `false`.
5. Both A and B pass authorization, and both proceed to trigger the workflow execution — the single JWT is effectively used twice, defeating the intended replay protection. [2](#0-1)

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
