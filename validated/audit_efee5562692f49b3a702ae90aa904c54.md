## Analog Found: Cache-key collision via unescaped field concatenation in `confidentialrelay` handler

### Title
Unescaped delimiter-joined cache keys in `capExecKey`/`secretsKey` allow cross-request response/authorization confusion - (File: `core/capabilities/confidentialrelay/response_cache.go`)

### Summary
The Sherlock report describes a Merkle-leaf collision in `FootiumPrizeDistributor` caused by hashing multiple logical fields together (`abi.encode(_token, _to, _amount)`) without a domain separator that prevents different field combinations from producing an identical leaf. The equivalent bug class in this repository is not a Merkle tree, but the gateway-facing `confidentialrelay` handler's request-deduplication/response-memo cache, which derives its cache key by joining several attacker-influenced string fields with a plain `"/"` separator, with no escaping of the separator itself.

### Finding Description
`capExecKey` and `secretsKey` build the cache/dedup key for capability-execute and secrets-get gateway requests by naively joining logical-identity fields with `/`: [1](#0-0) 

```go
func capExecKey(p confidentialrelaytypes.CapabilityRequestParams) string {
	return strings.Join([]string{capabilityCallDomain, p.WorkflowID, p.ExecutionID, p.ReferenceID, p.CapabilityID}, "/")
}

func secretsKey(p confidentialrelaytypes.SecretsRequestParams) string {
	return strings.Join([]string{secretsGetDomain, p.WorkflowID, p.ExecutionID, strconv.Itoa(int(p.CallbackID))}, "/")
}
```

The comment explicitly rationalizes skipping a hash: *"Avoids hashing: the fields are required non-empty by Validate, so a plain join is stable and debuggable"* [2](#0-1) . However, "non-empty" does not mean "delimiter-free." `ReferenceID` and `CapabilityID` (and, depending on caller, `WorkflowID`) are free-form strings that are not restricted to characters excluding `/`, e.g. `CapabilityID` values like `"my-cap@1.0.0"` [3](#0-2) . This means two logically distinct tuples can serialize to the identical string, e.g.:

- `(WorkflowID="wf", ExecutionID="1/x", ReferenceID="y", CapabilityID="c")` → `"call-capability/wf/1/x/y/c"`
- `(WorkflowID="wf", ExecutionID="1", ReferenceID="x/y", CapabilityID="c")` → `"call-capability/wf/1/x/y/c"`

This is the direct analog of the Merkle-leaf collision: multiple distinct logical inputs collapse to the same identifier used to gate access to cached/pending state.

This key is used both to serve a previously-computed **signed response from the memo cache**: [4](#0-3) 

and to detect/merge **in-flight duplicate requests**, where a second colliding request "waits on" the first and is answered with the first request's owner-computed, already-signed result: [5](#0-4) 

The same pattern applies to `handleSecretsGet`, which serves cached/in-flight secrets responses keyed the same way: [6](#0-5) 

### Impact Explanation
If an attacker (or a compromised/malicious confidential-compute host relaying gateway requests — a threat this code already treats as adversarial, see its own comments about "a malicious host can produce a genuinely-attested request over a forged enclave config" [7](#0-6) ) can craft `ReferenceID`/`CapabilityID`/`ExecutionID` values containing `/`, they can construct a request whose derived cache key collides with another workflow's/owner's in-flight or already-completed request. The colliding request would then be served the **other party's already-computed signed capability response or signed secrets response** — a cross-user response confusion where sensitive signed payloads (potentially derived from vault secrets) are returned to the wrong requester. It could also allow a request to be silently treated as a duplicate of, or merged into, another party's pending execution, bypassing separate re-validation.

### Likelihood Explanation
The requests reach this code over the gateway from the confidential-compute host, which the code itself does not fully trust (PRIV-433/PRIV-458 checks are present precisely because the host is considered capable of forging or replaying values). `ReferenceID` and `CapabilityID` are not shown anywhere to be restricted against containing `/`; only `WorkflowID`/`ExecutionID` have a separate hex-length validator (`ValidateWorkflowOrExecutionID`) used elsewhere in the codebase [8](#0-7) , but it is unclear from available context whether this validator is enforced on the `confidentialrelay` params path before `capExecKey`/`secretsKey` is computed. Given the uncertainty, likelihood is Medium — exploitability depends on whether upstream `Validate()` (in the external `chainlink-common` package, not visible in this repo's index) restricts `/` in these fields; if it does not, the collision is straightforward to construct.

### Recommendation
Replace the plain `strings.Join` with a length-prefixed or otherwise unambiguous encoding of each field (e.g., include each field's length before its value, or hash each field individually with a fixed-size digest before joining) so that no two distinct field tuples can produce the same key, mirroring the standard fix for the Merkle leaf collision (double-hashing or padding leaves to make them structurally distinguishable from internal nodes/other leaves).

### Proof of Concept
Not independently confirmed against live code because the upstream `confidentialrelaytypes.Validate()` implementation (in the `chainlink-common` dependency) that authorizes field contents is outside this repo's index and could not be inspected to confirm whether it restricts `/` characters in `ReferenceID`/`CapabilityID`. Conceptually:
1. Victim sends a capability-exec request with `WorkflowID="wf"`, `ExecutionID="1"`, `ReferenceID="x/y"`, `CapabilityID="c"`.
2. The relay signs and memoizes the response under key `"call-capability/wf/1/x/y/c"` [9](#0-8) .
3. Attacker sends a second, differently-scoped request with `WorkflowID="wf"`, `ExecutionID="1/x"`, `ReferenceID="y"`, `CapabilityID="c"`, producing the identical joined key.
4. `handleCapabilityExecute` finds the memoized entry for that key and returns the victim's already-signed response to the attacker [10](#0-9) .

This PoC path is plausible from the code structure but not confirmed end-to-end due to the missing validation source; a Devin session with full repo/dependency access would be needed to verify whether `Validate()` blocks `/` in these fields before relying on this as a confirmed exploit.

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

**File:** core/capabilities/confidentialrelay/handler_test.go (L425-435)
```go
				return makeRequest(t, confidentialrelaytypes.MethodCapabilityExec, confidentialrelaytypes.CapabilityRequestParams{
					WorkflowID:    "wf-1",
					Owner:         testOwner, // chainlink-common#2032 requires 0x-prefixed 20-byte hex
					ExecutionID:   capExecExecutionID,
					OrgID:         "org-1",
					ReferenceID:   "17",
					CapabilityID:  "my-cap@1.0.0",
					Payload:       makeCapabilityPayload(t, map[string]any{"key": "val"}),
					EnclaveConfig: testEnclaveConfigPtr(),
					Attestation:   testAttestationB64,
				})
```

**File:** core/capabilities/confidentialrelay/handler.go (L364-372)
```go
	// Verify the enclave's reported config matches the onchain DON state
	// before treating the attested request as trusted: the Nitro attestation
	// binds the request hash, but a malicious host can produce a
	// genuinely-attested request over a forged enclave config unless we
	// compare the config value against the DON reference.
	if err = h.verifyEnclaveConfigMatchesDON(localNode, params.EnclaveConfig); err != nil {
		l.Warnw("rejecting secrets request: enclave config does not match DON", "err", err)
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, err)
	}
```

**File:** core/capabilities/confidentialrelay/handler.go (L383-424)
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

**File:** core/capabilities/confidentialrelay/handler.go (L614-628)
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
```

**File:** core/capabilities/confidentialrelay/handler.go (L630-655)
```go
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

**File:** core/capabilities/validation/validation.go (L14-25)
```go
// Workflow IDs and Execution IDs are 32-byte hex-encoded strings
func ValidateWorkflowOrExecutionID(id string) error {
	if len(id) != validWorkflowIDLen {
		return errors.New("must be 32 bytes long")
	}
	_, err := hex.DecodeString(id)
	if err != nil {
		return errors.New("must be a hex-encoded string")
	}

	return nil
}
```
