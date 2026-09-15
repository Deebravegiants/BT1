Based on my investigation, the strongest candidate for a crosslinking-style analog is `capExecKey`/`secretsKey` in `core/capabilities/confidentialrelay/response_cache.go`, which build cache keys by joining attacker-influenced, variable-length string fields with an unescaped `/` delimiter. This is structurally the same bug class as the Fabric report: naive concatenation of variable-length fields without a length-prefix or escaping lets different logical inputs collide on the same serialized key.

### Title
Cache-key collision via unescaped delimiter concatenation in confidential relay response cache - (File: core/capabilities/confidentialrelay/response_cache.go)

### Summary
`capExecKey` and `secretsKey` build a `pendingRequests` deduplication key by `strings.Join`-ing `WorkflowID`, `ExecutionID`, `ReferenceID`/`CallbackID`, and `CapabilityID` with a literal `"/"` separator, without escaping or length-prefixing the fields. [1](#0-0)  If any of these identifier fields is attacker-influenced and may contain a `/` character, two logically distinct requests can be crafted to produce the identical joined key — the same "crosslinking" primitive as the Fabric bug, where variable-length fields concatenated without a delimiter/length-prefix allow one attacker-chosen split to collide with another's.

### Finding Description
The comment on `capExecKey` claims "the fields are required non-empty by Validate, so a plain join is stable and debuggable" [2](#0-1) , but non-emptiness does not prevent boundary-shifting collisions: e.g. `WorkflowID="A", ExecutionID="B/C", ReferenceID="D"` and `WorkflowID="A/B", ExecutionID="C", ReferenceID="D"` both join to `call-capability/A/B/C/D`. Whether this is exploitable depends on whether `Validate()` (referenced but not found in the indexed code) restricts these fields to a charset excluding `/`; I could not locate the `Validate` implementation for `CapabilityRequestParams`/`SecretsRequestParams` in `chainlink-common` to confirm this, since it lives in an external dependency package (`confidentialrelaytypes`) not present in this repo's index.

This key is used by `checkOrCreatePendingRequest`/`completePendingRequest`/`failPendingRequest` in the same file to deduplicate in-flight relay requests and to route a signed result to a waiter [3](#0-2) . If a collision were achievable, request B (from a different execution/workflow) could be treated as a duplicate of request A and would receive request A's `signed` result via `waitForPendingRequest` [4](#0-3)  — a cross-user/cross-execution response confusion.

### Impact Explanation
If reachable, this would let an unprivileged client whose request happens to collide with another in-flight request receive that other request's signed relay output (e.g. a decrypted-secrets response or capability-exec result) instead of its own — a cross-user response confusion matching the accepted impact classes. However, unlike the Fabric bug (which is unconditionally exploitable because blocks are raw concatenated bytes with no charset restriction), this requires the `WorkflowID`/`ExecutionID`/`ReferenceID`/`CapabilityID` fields to permit `/` characters, which is plausibly prevented by upstream validation I could not verify.

### Likelihood Explanation
Low-to-unknown. The gateway-side handler only uses these identifiers for logging correlation and explicitly defers all real validation to the relay nodes/enclave [5](#0-4) , so the gateway itself does not constrain the charset of `WorkflowID`/`ExecutionID` before they reach `capExecKey`/`secretsKey` in the capability-side cache. Whether the enclave/node-side `Validate()` (in `chainlink-common`, not in this repo) restricts these to identifiers such as UUIDs/hex strings that cannot contain `/` is unverified from the code available to me.

### Recommendation
Not providing an implementation plan per instructions, but conceptually: replace the unescaped `strings.Join` with a length-prefixed encoding (as done correctly elsewhere in this codebase, e.g. `appendLengthPrefixed` in `core/services/ocr/capregconfig/digest.go`) [6](#0-5) , or hash each field independently before concatenating, to remove any possibility of boundary-shifting collisions regardless of upstream validation guarantees.

### Proof of Concept
Not constructed — I could not confirm from the indexed code whether `WorkflowID`, `ExecutionID`, `ReferenceID`, or `CapabilityID` can contain `/` characters (the `Validate()` method for these types lives in the external `chainlink-common` package, outside this repo's index). Given this repository's size-limited indexing, a Devin session with full filesystem access could pull in `chainlink-common`'s `confidentialrelaytypes` package to confirm the exact validation constraints and build a concrete PoC.

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

**File:** core/capabilities/confidentialrelay/response_cache.go (L61-106)
```go
func (h *Handler) checkOrCreatePendingRequest(key string) (*pendingRequest, error) {
	mine := &pendingRequest{done: make(chan struct{})}
	if h.pendingRequests.Add(key, mine, cache.DefaultExpiration) == nil {
		h.lggr.Debugw("registered pending relay request, executing", "key", key)
		return nil, nil
	}
	if existing, ok := h.pendingRequests.Get(key); ok {
		if p, ok := existing.(*pendingRequest); ok {
			h.lggr.Debugw("relay request already in flight, waiting for its result", "key", key)
			return p, nil
		}
	}
	h.lggr.Errorw("pending request cache holds an entry of unexpected type", "key", key)
	return nil, fmt.Errorf("pending set holds an invalid entry for key %q", key)
}

// completePendingRequest publishes the owner's signed result and wakes any
// waiters. Called on the execution's success path, after the memo is set, so
// requests arriving later hit the memo instead. An owner that dies without
// completing never publishes; the TTL ages its entry out and waiters fail on
// their own deadlines, which is the "unknown failure" outcome.
func (h *Handler) completePendingRequest(key string, signed any) {
	if v, ok := h.pendingRequests.Get(key); ok {
		if pr, ok := v.(*pendingRequest); ok {
			pr.signed = signed
			close(pr.done)
		}
	}
	h.pendingRequests.Delete(key)
}

// failPendingRequest publishes the owner's failure to any waiters and clears
// the entry. err is the error the owner is answering with — a relayError, so
// it carries that answer's JSON-RPC code — which lets waiters report the real
// cause (vault failure, missing execution handler, ...) rather than a vague
// error of their own.
func (h *Handler) failPendingRequest(key string, err error) {
	h.lggr.Debugw("publishing pending relay request failure", "key", key, "err", err)
	if v, ok := h.pendingRequests.Get(key); ok {
		if pr, ok := v.(*pendingRequest); ok {
			pr.err = err
			close(pr.done)
		}
	}
	h.pendingRequests.Delete(key)
}
```

**File:** core/capabilities/confidentialrelay/response_cache.go (L113-119)
```go
func waitForPendingRequest(ctx context.Context, pr *pendingRequest) (signed any, ok bool, err error) {
	select {
	case <-pr.done:
		return pr.signed, true, pr.err
	case <-ctx.Done():
		return nil, false, nil
	}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L89-97)
```go
// extractRequestLabels best-effort decodes the logging identifiers from a
// request's params. Both relay methods' params carry these fields. A decode
// failure leaves them empty and is only logged: these labels are for
// correlation, and the params themselves are validated by the relay nodes,
// not here, so a request whose params do not decode is still fanned out and
// rejected there. ProcessRequest has already parsed the envelope as valid
// JSON by this point, so a failure here means params is not an object or
// carries non-string identifiers — malformed input rather than a gateway bug,
// hence debug level to avoid handing a caller a log-spam lever.
```

**File:** core/services/ocr/capregconfig/digest.go (L92-98)
```go
func appendLengthPrefixed(buf []byte, data []byte) []byte {
	var lenBytes [4]byte
	binary.BigEndian.PutUint32(lenBytes[:], uint32(len(data))) //#nosec G115 - data length will never exceed uint32 max in practice
	buf = append(buf, lenBytes[:]...)
	buf = append(buf, data...)
	return buf
}
```
