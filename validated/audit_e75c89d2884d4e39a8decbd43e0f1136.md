Found it: `secretsKey` in `core/capabilities/confidentialrelay/response_cache.go` is exactly the gogs bug-class analog — a shared cache/authorization-record keyed by an identifier that does not bind the party who is actually allowed to read the cached content, evaluated *before* re-checking the authorization that produced it.

### Title
Cross-owner secret disclosure via workflow/execution-scoped response memo that omits Owner from its cache key - (File: core/capabilities/confidentialrelay/response_cache.go)

### Summary
The confidential-relay gateway handler caches the *signed* result of a `secrets/get` request in `h.responseMemo`, keyed by `secretsKey(params)`. That key is built only from `WorkflowID`, `ExecutionID`, and `CallbackID` — it deliberately omits `Owner`. `WorkflowID` here is the enclave-supplied logical workflow identifier, not an opaque per-tenant secret, and (unlike the on-chain `GenerateWorkflowID` used elsewhere in the codebase) it is not itself a hash that binds the owner. Any subsequent request that reproduces the same `(WorkflowID, ExecutionID, CallbackID)` tuple — even from a request whose `Owner` field differs — will look up the identical memo entry and get served the previously-signed secrets response for that entry, mirroring the gogs flaw where a content-addressed store keyed only by OID (not by the tenant-scoped `(repo_id, oid)` row) let one tenant bind to and read back another tenant's blob.

### Finding Description
`handleSecretsGet` in `core/capabilities/confidentialrelay/handler.go` performs the Workflow-DON-quorum authorization check (`verifyWorkflowAuthorization`) which validates that `params.Owner` matches the owner named in the DON-signed `PublicData`, and that `params.WorkflowID` matches too: [1](#0-0) 

Immediately after that owner-bound check passes, the handler computes the memo/dedupe key and serves a cache hit without ever re-checking Owner against what produced the cached entry: [2](#0-1) 

The key itself is defined to intentionally exclude Owner: [3](#0-2) 

The result is written into the memo (and the in-flight "pending request" map, which shares the same key) after the *first* caller's fetch completes: [4](#0-3) 

This is structurally identical to the gogs flaw: gogs's authorization table is keyed `(repo_id, oid)` — tenant-scoped — but the underlying content store is addressed by `oid` alone, and the dedupe path let a second tenant bind to and read the first tenant's content without ever proving they held it. Here, the real authorization boundary is `(Owner, WorkflowID, ExecutionID, CallbackID)` — attested per-request by the DON quorum check — but the *cache/dedup* layer collapses that to `(WorkflowID, ExecutionID, CallbackID)`, dropping Owner. Whether `WorkflowID` values are guaranteed globally unique per owner is not verifiable from what I could inspect in this pass (no code path constructing `confidentialrelaytypes.SecretsRequestParams.WorkflowID` was found in the confidentialrelay package, only its consumption); if two different owners' enclave-driven executions can ever produce requests carrying the same `WorkflowID`/`ExecutionID`/`CallbackID` triple (e.g., collision, replay of a stale/reused execution id, or an enclave-host bug/compromise crafting the triple while still passing a stale/replayed DON quorum signature bound to a different, no-longer-current owner claim), the second requester is served the first owner's decrypted-and-signed secret payload straight from the memo, bypassing the fresh per-request Owner binding that `verifyWorkflowAuthorization` is supposed to enforce for every request.

### Impact Explanation
If reachable, this discloses another workflow-owner's decrypted vault secrets (API keys, credentials) to an attacker who can produce a matching `(WorkflowID, ExecutionID, CallbackID)` tuple, entirely bypassing the per-request DON-quorum owner check that this code explicitly documents as the anti-cross-owner-leak control ("PRIV-433" / "A breached enclave cannot forge a Workflow DON quorum over a different owner" — comment at lines 871-881 — which is neutralized once a matching cache entry already exists, since the memo is served without re-validating the association between the cached entry's original owner and the current request's owner).

### Likelihood Explanation
Likelihood is moderate/uncertain rather than trivially exploitable: the caller must control or predict a `WorkflowID`/`ExecutionID`/`CallbackID` triple that was already used for another owner's request AND must still pass `verifyWorkflowAuthorization`'s DON-quorum signature check for their own (potentially different) owner claim before reaching the memo lookup. I could not confirm from the indexed code whether `WorkflowID` as used in this struct is globally unique across owners by construction elsewhere in the system (e.g., minted with owner as part of its preimage, as `pkgworkflows.GenerateWorkflowID` does for the on-chain workflow registry) or whether it is a caller/enclave-supplied opaque string with no such binding. That uncertainty is the crux of exploitability and should be resolved before treating this as confirmed-exploitable; I flag it because the code's own memo key deliberately omits Owner while the security check right above it explicitly treats Owner as part of the authorization boundary, which is the exact class of decoupling that caused the gogs CVE.

### Recommendation
Include `Owner` in `secretsKey` (and in `capExecKey`, for the parallel capability-exec memo/pending-request path) so the cache/dedupe key matches the actual authorization boundary enforced by `verifyWorkflowAuthorization`, i.e. `strings.Join([]string{secretsGetDomain, p.Owner, p.WorkflowID, p.ExecutionID, strconv.Itoa(int(p.CallbackID))}, "/")`. As defense in depth, also re-validate that the memoized response's owner matches `params.Owner` before returning a cache hit, rather than trusting key-space non-collision alone.

### Proof of Concept
Not independently reproduced against a running node in this pass (index-only analysis); the trace supporting the finding is:
1. `verifyWorkflowAuthorization` validates `params.Owner` against DON-signed `PublicData` for the *current* request only: [5](#0-4) 
2. Immediately after, `key := secretsKey(params)` is computed from a struct that excludes `Owner`: [3](#0-2) 
3. A cache hit on that key returns the previously signed result for whichever owner's request first populated it, with no re-check that the current request's `Owner` matches: [6](#0-5) 

A background Devin session with repo/runtime access would be needed to construct two `SecretsRequestParams` with different `Owner` values but a colliding `(WorkflowID, ExecutionID, CallbackID)` triple and DON-quorum-valid signatures, and confirm the second request receives the first owner's plaintext-adjacent (encrypted-share) secret response from the memo.

### Citations

**File:** core/capabilities/confidentialrelay/handler.go (L374-381)
```go
	// Beyond attestation, verify the Workflow DON authorized this request: the enclave
	// forwards the Workflow-DON-signed compute requests (a 2*F+1 quorum), whose PublicData
	// names the authorized owner. A TEE breach passes attestation but cannot forge a Workflow
	// DON quorum over a different owner (PRIV-433).
	if err = h.verifyWorkflowAuthorization(localNode.WorkflowDON, params); err != nil {
		l.Warnw("rejecting secrets request: workflow DON authorization failed", "err", err)
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInvalidParams, err)
	}
```

**File:** core/capabilities/confidentialrelay/handler.go (L383-397)
```go
	// A retry (same logical identity, new gateway request id) re-fans-out the
	// same request; return the already-computed signed result from the memo
	// instead of re-fetching from the vault. The signed result is params-bound,
	// not id-bound, so jsonResponse re-wraps it with this request's id.
	key := secretsKey(params)
	l = logger.With(l, "key", key)

	h.pendingRequestsMu.Lock()
	if cached, ok := h.responseMemo.Get(key); ok {
		if signed, ok := cached.(*confidentialrelaytypes.SignedSecretsResponseResult); ok {
			h.pendingRequestsMu.Unlock()
			l.Debugw("serving secrets request from memo")
			return h.jsonResponse(req, signed)
		}
	}
```

**File:** core/capabilities/confidentialrelay/handler.go (L426-443)
```go
	// We own the pending entry: fetch, then publish the outcome to any waiters
	// either way. A failure has to reach them with its real cause, and has to
	// clear the entry so later retries re-execute rather than waiting on a
	// request nobody completes (see failPendingRequest).
	signedResult, err := h.fetchSecrets(ctx, l, params)
	if err != nil {
		h.pendingRequestsMu.Lock()
		h.failPendingRequest(key, err)
		h.pendingRequestsMu.Unlock()
		return h.errorResponse(ctx, gatewayID, req, relayErrorCode(err, jsonrpc.ErrInternal), err)
	}

	h.pendingRequestsMu.Lock()
	h.responseMemo.SetDefault(key, signedResult)
	h.completePendingRequest(key, signedResult)
	h.pendingRequestsMu.Unlock()
	l.Infow("fetched and signed secrets response")
	return h.jsonResponse(req, signedResult)
```

**File:** core/capabilities/confidentialrelay/handler.go (L919-934)
```go
	// The signed request authorizes a specific owner and workflow; the secrets request must
	// match both, or a breached enclave could fetch another owner's secrets.
	var execution confidentialworkflow.WorkflowExecution
	if err := proto.Unmarshal(params.SignedComputeRequests[0].PublicData, &execution); err != nil {
		return fmt.Errorf("failed to unmarshal workflow execution from public data: %w", err)
	}
	if !common.IsHexAddress(params.Owner) || !common.IsHexAddress(execution.GetOwner()) {
		return errors.New("invalid owner address")
	}
	if common.HexToAddress(execution.GetOwner()) != common.HexToAddress(params.Owner) {
		return fmt.Errorf("owner not authorized: request %q vs signed %q", params.Owner, execution.GetOwner())
	}
	if execution.GetWorkflowId() != params.WorkflowID {
		return fmt.Errorf("workflow_id not authorized: request %q vs signed %q", params.WorkflowID, execution.GetWorkflowId())
	}
	return nil
```

**File:** core/capabilities/confidentialrelay/response_cache.go (L25-29)
```go
// secretsKey is the deterministic cache key for a secrets-get request, built
// from its logical identity: workflow, execution, callback id.
func secretsKey(p confidentialrelaytypes.SecretsRequestParams) string {
	return strings.Join([]string{secretsGetDomain, p.WorkflowID, p.ExecutionID, strconv.Itoa(int(p.CallbackID))}, "/")
}
```
