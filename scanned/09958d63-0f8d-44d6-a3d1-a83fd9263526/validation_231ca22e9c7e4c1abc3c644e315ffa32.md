### Title
Delimiter-injection collision in `confidentialrelay` cache keys allows cross-execution response confusion - (File: `core/capabilities/confidentialrelay/response_cache.go`)

### Summary
The Fuel report shows that Sway's storage-slot derivation mixes multiple hashing/encoding schemes without domain separation, so an attacker can choose inputs whose serialized byte representation collides with another variable's slot, letting one storage write silently overwrite (or read) a different logical value. The same root cause — building a "unique" key by concatenating attacker-influenced fields without escaping a chosen delimiter — exists in the `confidentialrelay` handler's response-memoization and pending-request cache keys, which are built with a plain `strings.Join` over `WorkflowID`, `ExecutionID`, `ReferenceID`, and `CapabilityID` [1](#0-0) .

### Finding Description
`capExecKey` and `secretsKey` are the cache keys used to memoize signed relay/vault responses and to detect in-flight duplicate requests: [1](#0-0) 

The comment explicitly states the design rationale: *"Avoids hashing: the fields are required non-empty by Validate, so a plain join is stable and debuggable."* This only guarantees the fields are non-empty — it says nothing about excluding the `/` delimiter used to join them. Because `WorkflowID`, `ExecutionID`, `ReferenceID`, and `CapabilityID` are attacker-influenced strings (a workflow owner names/deploys their own workflow and controls capability call parameters bound into `CapabilityRequestParams`/`SecretsRequestParams`), a caller can construct field values containing embedded `/` characters so that the joined string for one logical request equals the joined string for a different logical request with different field boundaries — e.g. `WorkflowID="wf1/exec2", ExecutionID="ref3"` produces the same key as `WorkflowID="wf1", ExecutionID="exec2", ReferenceID="ref3"`.

This is exactly the class of bug in the Fuel report: allocating "unique" identifiers from unescaped concatenation of attacker-influenced values, where two semantically different inputs are guaranteed (not just probabilistically likely, as with hash collisions) to serialize to the same key.

These keys gate two security-relevant caches in `Handler`:
- `responseMemo`, which stores completed `*SignedSecretsResponseResult` / capability-exec results and is returned directly to any caller presenting a colliding key [2](#0-1) .
- `pendingRequests`, which causes a colliding request to be treated as a retry of another party's in-flight request and to receive that request's result once it completes [3](#0-2) .

### Impact Explanation
If a workflow/caller can craft `WorkflowID`/`ExecutionID`/`ReferenceID`/`CapabilityID` values containing `/`, it can force its own `MethodSecretsGet` or `MethodCapabilityExec` request to collide with another workflow's in-flight or memoized request. Since `handleSecretsGet` serves the memoized `SignedSecretsResponseResult` to any request presenting the same derived key [4](#0-3) , an attacker-controlled request could receive another party's signed secrets/vault response — a concrete cross-user response confusion and potential secret-disclosure vector, matching the accepted analog impacts.

### Likelihood Explanation
Exploitability depends on whether upstream `Validate()` calls for `CapabilityRequestParams`/`SecretsRequestParams` restrict these fields to a limited character set (e.g., alphanumeric identifiers). I could not fully confirm the content of that `Validate()` logic within the available index; the response_cache.go comment only claims non-emptiness is enforced, which is the concrete, code-backed basis for this finding. If `Validate()` elsewhere also excludes `/` or other structural characters, the collision described here would not be reachable — this caveat should be verified against the actual `Validate()` implementation for `confidentialrelaytypes.CapabilityRequestParams` and `SecretsRequestParams`.

### Recommendation
Use domain-separated, length-prefixed or hashed encoding for cache keys instead of a raw delimiter join, e.g. `sha256(len(workflowID) || workflowID || len(executionID) || executionID || ...)`, or escape/reject any delimiter characters in each field before joining, mirroring the EIP-1967-style domain separation recommended in the source report.

### Proof of Concept
Conceptual (would require confirming `Validate()` does not reject `/`):
1. Legitimate request A: `WorkflowID="wf1", ExecutionID="exec2", ReferenceID="ref3", CapabilityID="cap"` → key `get-secrets/wf1/exec2/ref3` (with CallbackID appended similarly for `secretsKey`, or `capExecKey` for the exec case).
2. Attacker crafts request B: `WorkflowID="wf1/exec2", ExecutionID="ref3", ReferenceID="cap", CapabilityID=...` such that `strings.Join` produces the identical string `get-secrets/wf1/exec2/ref3`.
3. If request A's result is memoized in `responseMemo` (or is in-flight in `pendingRequests`) when request B arrives, `handleSecretsGet` returns A's signed secrets result to B [5](#0-4) .

### Citations

**File:** core/capabilities/confidentialrelay/response_cache.go (L17-29)
```go
// capExecKey is the deterministic cache key for a capability-exec request,
// built from its logical identity: the (workflow, execution, step, capability)
// tuple the relay-DON signature binds to. Avoids hashing: the fields are
// required non-empty by Validate, so a plain join is stable and debuggable.
func capExecKey(p confidentialrelaytypes.CapabilityRequestParams) string {
	return strings.Join([]string{capabilityCallDomain, p.WorkflowID, p.ExecutionID, p.ReferenceID, p.CapabilityID}, "/")
}

// secretsKey is the deterministic cache key for a secrets-get request, built
// from its logical identity: workflow, execution, callback id.
func secretsKey(p confidentialrelaytypes.SecretsRequestParams) string {
	return strings.Join([]string{secretsGetDomain, p.WorkflowID, p.ExecutionID, strconv.Itoa(int(p.CallbackID))}, "/")
}
```

**File:** core/capabilities/confidentialrelay/handler.go (L386-397)
```go
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

**File:** core/capabilities/confidentialrelay/handler.go (L399-424)
```go
	// A retry that arrives while the original vault fetch is still in flight
	// waits on it and responds with the owner's result, same rationale as
	// handleCapabilityExecute.
	pending, err := h.checkOrCreatePendingRequest(key)
	if err != nil {
		h.pendingRequestsMu.Unlock()
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, err)
	}
	h.pendingRequestsMu.Unlock()
	if pending != nil {
		signed, ok, ownerErr := waitForPendingRequest(ctx, pending)
		switch {
		case !ok:
			l.Warnw("timed out waiting for in-flight secrets request", "err", ctx.Err())
			return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, errors.New("timed out waiting for in-flight secrets request"))
		case ownerErr != nil:
			ownerCode := relayErrorCode(ownerErr, jsonrpc.ErrInternal)
			l.Debugw("in-flight secrets request failed; relaying its error", "errorCode", ownerCode)
			return h.errorResponse(ctx, gatewayID, req, ownerCode, ownerErr)
		}
		if signed, ok := signed.(*confidentialrelaytypes.SignedSecretsResponseResult); ok {
			l.Debugw("served retried secrets request from in-flight owner")
			return h.jsonResponse(req, signed)
		}
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, errors.New("in-flight secrets request completed without a result"))
	}
```
