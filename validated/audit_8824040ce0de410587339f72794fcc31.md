### Title
NULL pointer dereference in vault gateway's public-key cache getter due to mismatched nil-checks - (File: `core/services/gateway/handlers/vault/handler.go`)

### Summary
The gateway-side vault handler's public-key cache getter, `getCachedPublicKey`, checks one cached field (`h.cachedPublicKeyGetResponse`) for `nil` but then unconditionally dereferences a *different* cached field (`h.cachedPublicKeyObject`) without checking it, mirroring the ALPINE-CVE-2026-33007 bug class: a caching code path that omits a null check on the object it actually uses, reachable by an unauthenticated remote caller.

### Finding Description
`getCachedPublicKey` is:
```go
func (h *handler) getCachedPublicKey() ([]byte, *tdh2easy.PublicKey) {
	h.mu.RLock()
	defer h.mu.RUnlock()
	if h.cachedPublicKeyGetResponse == nil {
		return nil, nil
	}
	copied := make([]byte, len(h.cachedPublicKeyGetResponse))
	copy(copied, h.cachedPublicKeyGetResponse)
	cachedPublicKeyCopy := *h.cachedPublicKeyObject
	return copied, &cachedPublicKeyCopy
}
``` [1](#0-0) 

The guard is on `cachedPublicKeyGetResponse` (a `[]byte`), but the value that is actually dereferenced is `cachedPublicKeyObject` (a `*tdh2easy.PublicKey`), via `*h.cachedPublicKeyObject`. These are two separate struct fields; the nil-check on one does not guarantee the other is non-nil. This function is invoked from `handlePublicKeyGet`:
```go
func (h *handler) handlePublicKeyGet(ctx context.Context, ar *activeRequest) error {
	...
	publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
	if cachedPublicKey != nil {
		...
	}
	...
	return h.fanOutToVaultNodes(ctx, l, ar)
}
``` [2](#0-1) 

`handlePublicKeyGet` is dispatched for `vaulttypes.MethodPublicKeyGet`, and the vault gateway handler is the internet-facing component that serves JSON-RPC requests originating from workflow/vault clients through the gateway before any node-side authorization is applied — the public-key-get path in particular is explicitly unauthenticated/unauthorized by design (it precedes `AuthorizeRequest` in the node-side flow) [3](#0-2) .

### Impact Explanation
If any code path (partial/failed cache refresh, initialization ordering, a future refactor that updates one field without the other under the same lock) leaves `cachedPublicKeyGetResponse` non-nil while `cachedPublicKeyObject` is nil, every subsequent `PublicKeyGet` request from any unauthenticated client hitting this gateway process will dereference a nil pointer via `*h.cachedPublicKeyObject`, crashing the gateway process (denial of service), directly analogous to the Apache `mod_authn_socache` NULL pointer dereference crashing a caching worker on an unauthenticated request.

### Likelihood Explanation
I was not able to locate and fully verify the setter that populates `cachedPublicKeyGetResponse` and `cachedPublicKeyObject` together (the write path was not found within available search iterations), so I cannot conclusively prove there exists a reachable state where the two fields diverge. The getter code itself, however, is unambiguously mismatched — the nil-check protects the wrong field — which is a code defect regardless of whether current setter logic happens to keep the two fields in lockstep. Because I could not confirm the setter's atomicity guarantees, likelihood is assessed as **uncertain/medium** rather than confirmed-high.

### Recommendation
Change the guard in `getCachedPublicKey` to check `h.cachedPublicKeyObject == nil` (the value actually dereferenced) instead of `h.cachedPublicKeyGetResponse == nil`, or check both fields explicitly before use. Additionally, audit and confirm that every write path setting these two cache fields does so atomically under `h.mu.Lock()` so they can never observe a partially-updated state.

### Proof of Concept
Not independently reproducible from the index alone — reproduction requires confirming the write path that populates `cachedPublicKeyObject`/`cachedPublicKeyGetResponse` and identifying a state transition (e.g., a failed/partial cache refresh) that sets one field without the other, then sending an unauthenticated `vaulttypes.MethodPublicKeyGet` JSON-RPC request to the gateway to trigger `getCachedPublicKey`'s dereference of the nil `cachedPublicKeyObject`.

**Note on completeness:** due to running out of investigation iterations, I could not read the struct definition and setter logic for `cachedPublicKeyGetResponse`/`cachedPublicKeyObject` in `core/services/gateway/handlers/vault/handler.go`, so the exploitability (whether the divergence is actually reachable) is unverified. A Devin session with full file access would be needed to confirm or rule this out definitively.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L680-690)
```go
func (h *handler) getCachedPublicKey() ([]byte, *tdh2easy.PublicKey) {
	h.mu.RLock()
	defer h.mu.RUnlock()
	if h.cachedPublicKeyGetResponse == nil {
		return nil, nil
	}
	copied := make([]byte, len(h.cachedPublicKeyGetResponse))
	copy(copied, h.cachedPublicKeyGetResponse)
	cachedPublicKeyCopy := *h.cachedPublicKeyObject
	return copied, &cachedPublicKeyCopy
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L692-708)
```go
func (h *handler) handlePublicKeyGet(ctx context.Context, ar *activeRequest) error {
	l := logger.With(h.lggr, "method", ar.req.Method, "requestID", ar.req.ID)

	publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
	if cachedPublicKey != nil {
		l.Debugw("returning cached public key response")
		return h.sendSuccessResponse(ctx, l, ar, &jsonrpc.Response[json.RawMessage]{
			Version: jsonrpc.JsonRpcVersion,
			ID:      ar.req.ID,
			Method:  ar.req.Method,
			Result:  (*json.RawMessage)(&publicKeyResponseBytes),
		})
	}

	l.Debugw("cache stale: forwarding request to nodes", "now", h.clock.Now())
	return h.fanOutToVaultNodes(ctx, l, ar)
}
```

**File:** core/capabilities/vault/gw_handler.go (L207-209)
```go
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
```
