The claim accurately describes the code as it exists. Let me verify the check-then-act race is genuinely exploitable and not mitigated elsewhere (e.g., by JWT expiry/nonce checks, or by the caller serializing calls per-workflow).Audit Report

## Title
JWT Replay Check-Then-Act Race Allows Duplicate HTTP Trigger Requests to Bypass Replay Protection - (`core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

## Summary
`WorkflowMetadataHandler.Authorize` verifies a JWT-bound HTTP trigger request and is intended to enforce single-use of the JWT `jti` claim via a replay cache. The replay check (`isReplay`) and the replay record (`recordUsage`) are two separate lock-protected operations executed at different points in `Authorize`, with authorization-key lookups happening in between, so the whole sequence is not atomic and is vulnerable to a TOCTOU race under concurrent identical requests.

## Finding Description
`Authorize` calls `h.jwtCache.isReplay(claims.ID)` right after JWT verification, then performs unrelated authorized-key lookups, and only calls `h.jwtCache.recordUsage(claims.ID)` at the very end before returning success: [1](#0-0) 

`jwtReplayCache` uses a `sync.RWMutex`, but each method (`isReplay`, `recordUsage`) only holds the lock for the duration of its own call, not across the full check-then-record sequence in `Authorize`: [2](#0-1) 

Two concurrent calls to `Authorize` with the same signed JWT can both pass `isReplay` (since neither has called `recordUsage` yet at that point), both pass the authorized-key lookup, and both succeed — with `recordUsage` executed twice afterward. This is a textbook check-then-act race, and the code confirms the claim precisely.

The repo also contains a correctly-implemented atomic pattern elsewhere (`RequestReplayGuard.CheckAndRecord`, which holds a single lock across the existence-check and insert), demonstrating that the project is aware of this class of bug and has a working pattern that `jwtReplayCache` fails to follow.

## Impact Explanation
`Authorize` gates `HandleUserTriggerRequest` for the HTTP trigger path (called from `httpTriggerHandler` via `workflowMetadataHandler.Authorize` in `http_trigger_handler.go`), so a successful race lets the same signed JWT+request be accepted twice and forwarded to the workflow DON twice, instead of the intended "one JWT = one execution" guarantee. This maps to an in-scope impact of unauthorized/duplicate job execution via replay/race, which could translate to duplicate workflow triggers, fund movement, or side effects if workflow logic assumes idempotency per JWT.

## Likelihood Explanation
Exploitation requires only an unprivileged client capable of issuing two near-simultaneous requests carrying the same valid signed JWT/body — no special credentials beyond a legitimate signed trigger request are needed. The race window is narrow (a handful of in-process Go statements between `isReplay` and `recordUsage`), so successful exploitation is probabilistic and may require several attempts under real network/load conditions, but it is not a hypothetical race — the code path genuinely allows two goroutines to interleave between the check and the record.

## Recommendation
Replace the split `isReplay`/`recordUsage` calls with a single atomic method (e.g., `CheckAndRecord(jti)`) on `jwtReplayCache` that takes the write lock once, checks the map, and inserts the entry before releasing the lock — mirroring `RequestReplayGuard.CheckAndRecord`. Call this atomic check immediately after JWT verification in `Authorize`, before any authorized-key lookups, so no unrelated logic sits between the check and the record.

## Proof of Concept
1. Sign a valid JWT-bound HTTP trigger request using `utils.CreateRequestJWT` and `SignedString`, matching the existing test helper pattern in `workflow_metadata_handler_test.go`'s "JWT replay protection" subtest.
2. Launch two goroutines that concurrently call `handler.Authorize(workflowID, tokenString, req)` with the identical token/request.
3. With a `sync.WaitGroup` and a small artificial delay inserted between `isReplay` and `recordUsage` (or simply relying on goroutine scheduling), observe that both calls can return `nil` error, i.e., both succeed, instead of the second one returning `"JWT token has already been used"` as guaranteed in the strictly sequential existing test. A `go test -race -count=100` run with two concurrent goroutines calling `Authorize` demonstrates the double-success outcome, proving the replay cache does not provide the atomic single-use guarantee it claims to.

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L399-412)
```go
func (cache *jwtReplayCache) isReplay(jti string) bool {
	cache.mu.RLock()
	defer cache.mu.RUnlock()

	_, exists := cache.cache[jti]
	return exists
}

func (cache *jwtReplayCache) recordUsage(jti string) {
	cache.mu.Lock()
	defer cache.mu.Unlock()

	cache.cache[jti] = time.Now()
}
```
