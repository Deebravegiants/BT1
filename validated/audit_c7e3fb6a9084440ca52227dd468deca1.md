### Title
Cache-Key Collision via Unescaped Separator-Joined Identity Fields Causes Cross-Request Response Confusion in Confidential Relay Handler - (File: core/capabilities/confidentialrelay/response_cache.go)

### Summary
The Ekubo `Oracle` bug arises because two logically distinct identities (`token`'s `Counts` slot and `(token, index)`'s `Snapshot` slot) are packed into the same storage key space via bit arithmetic (`(token << 32) | index`) instead of an unambiguous, collision-resistant derivation (e.g. `keccak256`), so one entity's data can silently overwrite/alias another's. The same root-cause pattern — building a request-identity cache key by naively joining variable-length, attacker-influenced string fields with a plain separator instead of hashing/length-prefixing them — exists in the Confidential Relay handler's dedup/pending-request cache key derivation.

### Finding Description
`capExecKey` and `secretsKey` build cache keys by `strings.Join`-ing multiple identity fields with a bare `"/"` separator, with no escaping and no guarantee that the individual fields themselves cannot contain `"/"`: [1](#0-0) 

`WorkflowID`, `ExecutionID`, `ReferenceID`, and `CapabilityID` in `CapabilityRequestParams` come from the enclave-forwarded, gateway-relayed JSON-RPC request and are used verbatim to build the key that is used both to look up the response memo and to register/find in-flight ("pending") requests: [2](#0-1) 

Because these are joined without a delimiter-safe encoding (unlike, say, `keccak256(abi.encode(...))` in the recommended Oracle fix), two structurally different tuples can serialize to an identical string. For example:
- Request A: `WorkflowID="wf", ExecutionID="1/x", ReferenceID="cap", CapabilityID="v1"` → key `"call-capability/wf/1/x/cap/v1"`
- Request B: `WorkflowID="wf", ExecutionID="1", ReferenceID="x/cap", CapabilityID="v1"` → key `"call-capability/wf/1/x/cap/v1"`

Both produce the identical cache key despite representing distinct logical executions. This is the same "distinct identity → identical derived key" class as the Oracle report's `(tokenA)` vs `(tokenB<<32|index)` collision — the fix recommended there (hash the composite identity instead of packing/joining it) applies here too.

### Impact Explanation
When two colliding requests are in flight or one has already completed, `handleCapabilityExecute` will serve the first request's memoized/pending **signed** result to the second, colliding request via `h.jsonResponse(req, signed)`: [3](#0-2) 

Because the response is only re-wrapped with the caller's own `req.ID` and is not re-validated against the caller's actual `WorkflowID`/`ExecutionID`/`ReferenceID`/`CapabilityID`, this causes cross-request/cross-execution response confusion: a caller receives a validly-signed capability response payload that was computed and signed for a different (colliding) execution/capability/reference than the one it asked for. Downstream, this is the same category of "wrong data returned as authoritative" failure the Oracle report flags — the enclave-side consumer trusts the relay's cached/pending response as bound to its own request's tuple, but it may not be.

### Likelihood Explanation
The attacker-controlled surface is the enclave/gateway-forwarded `CapabilityRequestParams`/`SecretsRequestParams`. The exact character-set constraints on `WorkflowID`, `ReferenceID`, and `CapabilityID` are enforced by `Validate()` in the external `chainlink-common` package (`confidentialrelaytypes`), which is outside this repository's index and could not be inspected here to confirm whether `"/"` is disallowed in these fields. If `Validate()` does not restrict these fields to a `"/"`-free character set (test fixtures show free-form values like `"my-cap@1.0.0"` and `"wf-1"`, with no visible charset restriction), the collision is directly constructible by any caller able to submit capability-exec/secrets-get requests through the relay/gateway path. This uncertainty about the exact field format enforced in the external dependency is a real gap in this analysis and should be verified directly against `chainlink-common`'s `Validate()` before treating this as fully confirmed.

### Recommendation
Replace the naive `strings.Join` key construction in `capExecKey` and `secretsKey` with a collision-resistant, unambiguous encoding of the identity tuple — e.g., hash each field (or length-prefix each field) before concatenation, analogous to the Oracle report's recommendation to use `keccak256(abi.encode(...))` instead of bit-packing:

```go
func capExecKey(p confidentialrelaytypes.CapabilityRequestParams) string {
    h := sha256.New()
    for _, f := range []string{capabilityCallDomain, p.WorkflowID, p.ExecutionID, p.ReferenceID, p.CapabilityID} {
        binary.Write(h, binary.BigEndian, uint32(len(f)))
        h.Write([]byte(f))
    }
    return hex.EncodeToString(h.Sum(nil))
}
```
Apply the same fix to `secretsKey`. Additionally, `handleCapabilityExecute`/`handleSecretsGet` should defensively re-verify that a memoized/pending response's bound identity fields match the incoming request's fields before returning it, rather than trusting key equality alone.

### Proof of Concept
Using the existing key-derivation function directly (no relay/network access needed):

```go
package confidentialrelay

import (
    "testing"
    confidentialrelaytypes "github.com/smartcontractkit/chainlink-common/pkg/capabilities/v2/actions/confidentialrelay"
)

func TestCapExecKeyCollision(t *testing.T) {
    a := confidentialrelaytypes.CapabilityRequestParams{
        WorkflowID: "wf", ExecutionID: "1/x", ReferenceID: "cap", CapabilityID: "v1",
    }
    b := confidentialrelaytypes.CapabilityRequestParams{
        WorkflowID: "wf", ExecutionID: "1", ReferenceID: "x/cap", CapabilityID: "v1",
    }
    if capExecKey(a) != capExecKey(b) {
        t.Fatal("expected collision was not reproduced")
    }
    // capExecKey(a) == capExecKey(b) == "call-capability/wf/1/x/cap/v1"
}
```
If `Validate()` in `chainlink-common` permits `/` (or any separator character) in `WorkflowID`, `ExecutionID`, `ReferenceID`, or `CapabilityID`, request B — a genuinely distinct execution — will hit `h.responseMemo.Get(key)` / `h.checkOrCreatePendingRequest(key)` under the exact same key as A in `handleCapabilityExecute`, and will be served A's signed result instead of executing its own capability call.

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

**File:** core/capabilities/confidentialrelay/handler.go (L564-655)
```go
func (h *Handler) handleCapabilityExecute(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	if req.Params == nil {
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInvalidParams, errors.New("missing params"))
	}
	var params confidentialrelaytypes.CapabilityRequestParams
	if err := json.Unmarshal(*req.Params, &params); err != nil {
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInvalidParams, err)
	}

	// The enclave's capability calls arrive as fresh gateway messages rather than
	// through the workflow engine, so ctx carries none of the CRE tenants the engine
	// seeds.
	//
	// Seeded as soon as the params are parsed so every ctx use below carries the
	// tenant.
	ctx = contexts.WithCRE(ctx, contexts.CRE{
		Org:      params.OrgID,
		Owner:    params.Owner,
		Workflow: params.WorkflowID,
	})

	// See handleSecretsGet: the gateway request id plus the workflow/execution
	// identity on every line, so logs correlate across the gateway, this node
	// and the enclave for one execution.
	l := logger.With(h.lggr,
		"requestID", req.ID,
		"workflowID", params.WorkflowID,
		"executionID", params.ExecutionID,
	)

	att := params.Attestation
	params.Attestation = ""
	if err := h.verifyAttestationHash(ctx, att, params, confidentialrelaytypes.DomainCapabilityExec); err != nil {
		l.Warnw("rejecting capability request: attestation validation failed", "err", err)
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, err)
	}

	// Verify the enclave's reported config matches the onchain DON state, same as
	// handleSecretsGet (PRIV-458): the Nitro attestation binds the request hash but
	// not the config value, so a malicious host could otherwise produce a
	// genuinely-attested request over a forged enclave config.
	localNode, err := h.capRegistry.LocalNode(ctx)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, fmt.Errorf("failed to get local node: %w", err))
	}
	if err = h.verifyEnclaveConfigMatchesDON(localNode, params.EnclaveConfig); err != nil {
		l.Warnw("rejecting capability request: enclave config does not match DON", "err", err)
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInternal, err)
	}

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
