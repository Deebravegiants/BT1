### Title
Ambiguous Delimiter in Confidential-Relay Cache-Key Construction Causes Capability Response Collisions - (File: core/capabilities/confidentialrelay/response_cache.go)

### Summary
`capExecKey` builds the deduplication/cache key for capability-execute requests in the Confidential Relay handler by joining variable-length, attacker-influenced strings with a `"/"` separator, with no escaping of the separator inside the individual fields. Because `WorkflowID`, `ReferenceID`, and `CapabilityID` are not restricted to a fixed-length/known-alphabet format (unlike `Owner` and `ExecutionID`, which are hex-encoded and length-checked), two logically distinct requests can be crafted to produce an identical cache key, exactly mirroring the "different `calldata`/different logical input → same hash" root cause described in the MiMC report.

### Finding Description
`capExecKey` is defined as: [1](#0-0) 

```go
func capExecKey(p confidentialrelaytypes.CapabilityRequestParams) string {
	return strings.Join([]string{capabilityCallDomain, p.WorkflowID, p.ExecutionID, p.ReferenceID, p.CapabilityID}, "/")
}
```

The comment claims the fields are "required non-empty by Validate, so a plain join is stable and debuggable" [2](#0-1) , but non-empty is not the same as delimiter-safe. The test helpers confirm only `Owner` and `ExecutionID` are format-constrained (0x-prefixed 20-byte hex / 32-byte hex), while `WorkflowID`, `ReferenceID`, and `CapabilityID` are free-form strings taken directly from workflow-author-controlled request params: [3](#0-2) 

This key is used in `handleCapabilityExecute` to (a) serve a memoized signed result for a "retry" without re-executing the capability, and (b) to detect/merge in-flight duplicate requests so a waiter is handed the owner's signed result: [4](#0-3) 

Because `strings.Join` provides no escaping, a workflow author can construct two different `(ReferenceID, CapabilityID)` pairs (or shift the boundary across `WorkflowID`/`ReferenceID`) that resolve to the identical joined string, e.g. for the same `WorkflowID`/`ExecutionID`:
- Params A: `ReferenceID = "a/b"`, `CapabilityID = "c"`
- Params B: `ReferenceID = "a"`, `CapabilityID = "b/c"`

Both produce `"call-capability/<wf>/<exec>/a/b/c"`.

### Impact Explanation
When two distinct capability-execute requests collide on the same key, the handler will:
- Return the signed result of request A to a caller that submitted request B (`h.responseMemo.Get(key)` returns the wrong entry) [5](#0-4) , or
- Treat B as a duplicate/retry of A while it is still in-flight, causing B's caller to receive A's signed capability response instead of executing its own capability call [6](#0-5) .

Since the response is cryptographically signed by the relay DON before being returned, a colliding step effectively yields a validly-signed response for the *wrong* capability/reference within the same execution — a cross-request response confusion (the same class of "different input, same identity" hazard described in the source report), which can corrupt subsequent workflow logic that consumes that step's result.

### Likelihood Explanation
`WorkflowID`, `ReferenceID`, and `CapabilityID` originate from workflow specifications that any unprivileged workflow author can define; no code path canonicalizes or rejects `/` in these fields before the join. Triggering the collision requires only crafting two steps within a workflow (or two requests with the boundary-shifting values shown above) whose fields align around the `/` separator — a low-effort, entirely client-side action once a workflow can be authored and executed against a Confidential Relay-enabled DON.

### Recommendation
Do not build the cache key by naively joining raw, unescaped strings. Either:
- length-prefix each field (as is already done correctly elsewhere in this codebase, see `appendLengthPrefixed` in `core/services/ocr/capregconfig/digest.go`) before hashing/joining, or
- percent-/URL-encode each component (escaping `/`) before joining, or
- hash each field independently and then hash the concatenation of the fixed-size digests (domain-separated), instead of joining variable-length raw strings with an escapable separator.

### Proof of Concept
1. Author a workflow (or forge two `CapabilityRequestParams` payloads with the same `WorkflowID`/`ExecutionID`) where:
   - Request A: `WorkflowID="wf-1"`, `ExecutionID=<32-byte-hex>`, `ReferenceID="a/b"`, `CapabilityID="c"`
   - Request B: `WorkflowID="wf-1"`, `ExecutionID=<32-byte-hex>` (same), `ReferenceID="a"`, `CapabilityID="b/c"`
2. Send request A through the gateway to `MethodCapabilityExec`; let it complete and populate `h.responseMemo` under key `"call-capability/wf-1/<hex>/a/b/c"` (see `capExecKey`, `core/capabilities/confidentialrelay/response_cache.go:21-23`).
3. Send request B with a fresh JSON-RPC id but the same params described above.
4. `capExecKey(paramsB)` computes the identical string as in step 2; `handleCapabilityExecute` finds the memo hit and returns A's signed result for B (`core/capabilities/confidentialrelay/handler.go:618-628`), instead of executing B's actual capability call.

### Citations

**File:** core/capabilities/confidentialrelay/response_cache.go (L17-23)
```go
// capExecKey is the deterministic cache key for a capability-exec request,
// built from its logical identity: the (workflow, execution, step, capability)
// tuple the relay-DON signature binds to. Avoids hashing: the fields are
// required non-empty by Validate, so a plain join is stable and debuggable.
func capExecKey(p confidentialrelaytypes.CapabilityRequestParams) string {
	return strings.Join([]string{capabilityCallDomain, p.WorkflowID, p.ExecutionID, p.ReferenceID, p.CapabilityID}, "/")
}
```

**File:** core/services/gateway/handlers/confidentialrelay/bundler_test.go (L16-34)
```go
// chainlink-common's confidentialrelay.Validate rejects request params missing any
// field the canonical hash binds to (Owner must be a 0x-prefixed 20-byte hex address;
// ExecutionID must be 32-byte hex with no prefix). Test params satisfy these formats.
const (
	testOwner       = "0x0000000000000000000000000000000000000001"
	testExecutionID = "0000000000000000000000000000000000000000000000000000000000000001"
	testEnclavePK   = "aabbcc"
)

func validCapParams(workflowID string) relaytypes.CapabilityRequestParams {
	return relaytypes.CapabilityRequestParams{
		WorkflowID:   workflowID,
		Owner:        testOwner,
		ExecutionID:  testExecutionID,
		ReferenceID:  "ref-1",
		CapabilityID: "cap-1",
		Payload:      "in",
	}
}
```

**File:** core/capabilities/confidentialrelay/handler.go (L614-655)
```go
	// A retry (same logical identity, new gateway request id) re-fans-out the
	// same request; return the already-computed signed result from the memo
	// instead of re-executing the capability. The signed result is params-bound,
	// not id-bound, so jsonResponse re-wraps it with this request's id.
	key := capExecKey(params)
	l = logger.With(l, "key", key)

	h.pendingRequestsMu.Lock()
	if cached, ok := h.responseMemo.Get(key); ok {
		if signed, ok := cached.(*confidentialrelaytypes.SignedCapabilityResponseResult); ok {
			h.pendingRequestsMu.Unlock()
			l.Debugw("serving capability request from memo")
			return h.jsonResponse(req, signed)
		}
	}

	// A retry that arrives while the original execution is still in flight
	// waits on it and responds with the owner's result rather than
	// re-executing.
	pending, err := h.checkOrCreatePendingRequest(key)
	if err != nil {
		h.pendingRequestsMu.Unlock()
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, err)
	}
	h.pendingRequestsMu.Unlock()
	if pending != nil {
		signed, ok, pendingReqErr := waitForPendingRequest(ctx, pending)
		switch {
		case !ok:
			l.Warnw("timed out waiting for in-flight capability request", "err", ctx.Err())
			return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, errors.New("timed out waiting for in-flight capability request"))
		case pendingReqErr != nil:
			errorCode := relayErrorCode(pendingReqErr, jsonrpc.ErrInternal)
			l.Debugw("in-flight capability request failed; relaying its error", "errorCode", errorCode)
			return h.errorResponse(ctx, gatewayID, req, errorCode, pendingReqErr)
		}
		if signed, ok := signed.(*confidentialrelaytypes.SignedCapabilityResponseResult); ok {
			l.Debugw("served retried capability request from in-flight owner")
			return h.jsonResponse(req, signed)
		}
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, errors.New("in-flight capability request completed without a result"))
	}
```
