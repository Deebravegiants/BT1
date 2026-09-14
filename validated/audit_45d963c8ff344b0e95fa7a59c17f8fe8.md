### Title
Unbounded `activeRequests` map growth via unauthenticated `vault_public_key_get` requests can DOS the gateway's Vault handler - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
The Gnosis `RootManager` DOS report is about an unbounded, attacker-growable in-memory structure (`pendingInboundRoots`) fed by a permissionless entrypoint, with no per-item cap, causing later processing (`dequeueVerified`/loop) to fail or become prohibitively expensive. The closest analog in this codebase is the gateway-side Vault handler's `activeRequests` map: it is populated from a permissionless, internet-facing entrypoint (`HandleJSONRPCUserMessage` → `MethodPublicKeyGet`) with no upper bound on the number of concurrently tracked entries, unlike the sibling WebAPI capability handler which explicitly caps its equivalent cache (`defaultMaxSavedCallbacks = 20000`).

### Finding Description
`GatewayHandler`/vault `handler.HandleJSONRPCUserMessage` special-cases `vaulttypes.MethodPublicKeyGet` to skip authorization entirely: [1](#0-0) 

If the public key isn't already cached, it calls `h.newActiveRequest(req, callback)` unconditionally for any caller, regardless of authentication/authorization: [2](#0-1) 

`newActiveRequest` only rejects a duplicate request ID; it enforces no maximum size on `h.activeRequests`: [3](#0-2) 

Because the gateway's request ID length limit is only used to bound string size (200 chars), not counts: [4](#0-3) 

an unauthenticated caller can submit an unbounded number of `MethodPublicKeyGet` requests with distinct IDs, each of which is inserted into `h.activeRequests` and fanned out to all Vault DON members: [5](#0-4) 

Entries are only removed on completion/timeout via the periodic `removeExpiredRequests` sweep (every `defaultCleanUpPeriod` = 5s, expiring after `requestTimeout`, default 30s): [6](#0-5) [7](#0-6) 

This is structurally analogous to the RootManager bug: a permissionless entrypoint feeds an unbounded queue/map that is iterated by background processing (`removeExpiredRequests` iterates the entire map every 5 seconds, and every fan-out call iterates all DON members). By contrast, the sibling capability gateway handler explicitly bounds its analogous cache with `defaultMaxSavedCallbacks = 20000`: [8](#0-7) 

The Vault handler has no equivalent cap.

### Impact Explanation
An attacker who floods `MethodPublicKeyGet` requests with unique IDs before/during the (rare) cache-miss window can grow `h.activeRequests` without bound, consuming gateway memory, increasing lock contention on `h.mu` (a single mutex guarding the whole map, held during `newActiveRequest`, `getActiveRequest`, `sendResponse`, and the periodic sweep), and multiplying DON-node fan-out traffic (`fanOutToVaultNodes` loops over all DON members per request). This can degrade or crash the gateway process for all legitimate node/vault operations — a Denial of Service against the gateway, consistent in kind (unbounded attacker-controlled queue causing resource exhaustion) with the reported RootManager issue, though the practical severity depends heavily on how quickly/reliably the public key cache is populated (see Likelihood).

### Likelihood Explanation
The exploitable window is narrow by design: `fetchVaultPublicKey` is invoked proactively at handler `Start()` and refreshed every minute via `tickerVaultPublicKeyRefresh`, and once `h.cachedPublicKeyGetResponse`/`h.cachedPublicKeyObject` are populated, subsequent `MethodPublicKeyGet` calls are answered synchronously without touching `activeRequests`: [9](#0-8) [1](#0-0) 

So sustained exploitation requires either (a) hitting the handler during the brief startup window before the first fetch completes, (b) the vault DON being unavailable/slow to respond (keeping requests "active" for up to `requestTimeout`, default 30s, which widens the exploitable window considerably since each request stays in the map that long), or (c) a bug/race that never populates the cache. Because the cache is normally warm, likelihood of high-impact exploitation is Low-to-Medium; it is meaningfully higher if the Vault DON is degraded or slow (a state an attacker cannot directly control but that increases blast radius). I was not able to fully verify whether any upstream rate limiting exists at the HTTP/gateway-server layer (`core/services/gateway/network/httpserver.go`) that would further mitigate this before requests reach the handler — this should be checked as it materially affects severity.

### Recommendation
- Apply the same bounded-cache pattern used in `core/services/gateway/handlers/capabilities/handler.go` (`MaxSavedCallbacks`/pruning) to the Vault handler's `activeRequests` map: cap its size and reject/drop new requests (with an appropriate error response) once the cap is reached.
- Consider requiring at least a lightweight rate limit (per-IP or per-caller) on `MethodPublicKeyGet` specifically, since it is the only vault method that bypasses `requestProcessor.ProcessRequest`/authorization.
- Ensure the public-key cache-miss path cannot be repeatedly triggered by the same unauthenticated caller in rapid succession (e.g., coalesce concurrent in-flight public-key fetches into a single upstream request rather than one `activeRequest` entry per caller ID).

### Proof of Concept
1. Restart (or otherwise cause) the gateway's Vault handler such that `h.cachedPublicKeyGetResponse == nil` (startup, or Vault DON temporarily slow/unavailable so the periodic refresh never completes within `requestTimeout`).
2. As an unauthenticated client, send many concurrent JSON-RPC requests to the gateway with `method: "vault_public_key_get"`, each with a distinct `id` (up to the 200-character limit, so effectively unlimited unique IDs).
3. Each request bypasses `requestProcessor.ProcessRequest` and calls `newActiveRequest`, inserting an entry into `h.activeRequests`, then fans out to every Vault DON member via `fanOutToVaultNodes`.
4. Repeat at high volume; entries remain in `h.activeRequests` for up to `requestTimeout` (default 30s) before `removeExpiredRequests` clears them, allowing the map to grow far beyond any WebAPI-handler-equivalent bound during that window, exhausting gateway memory/CPU and node fan-out capacity.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L271-300)
```go
func (h *handler) Start(_ context.Context) error {
	return h.StartOnce("VaultHandler", func() error {
		h.lggr.Debug("starting vault handler")
		if h.jwtAuth != nil {
			if err := h.jwtAuth.Start(context.Background()); err != nil {
				return fmt.Errorf("failed to start JWTBasedAuth: %w", err)
			}
		}
		go func() {
			ctx, cancel := h.stopCh.NewCtx()
			defer cancel()
			ticker := h.clock.NewTicker(defaultCleanUpPeriod)
			tickerVaultPublicKeyRefresh := h.clock.NewTicker(1 * time.Minute)
			defer ticker.Stop()
			defer tickerVaultPublicKeyRefresh.Stop()
			for {
				select {
				case <-ticker.Chan():
					h.removeExpiredRequests(ctx)
				case <-tickerVaultPublicKeyRefresh.Chan():
					// periodically, fetch vault public key, so we can cache it
					h.fetchVaultPublicKey(ctx)
				case <-h.stopCh:
					return
				}
			}
		}()
		return nil
	})
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L360-384)
```go
// removeExpiredRequests removes expired requests from the pending requests map
func (h *handler) removeExpiredRequests(ctx context.Context) {
	h.mu.RLock()
	var expiredRequests []*activeRequest
	now := h.clock.Now()
	for _, userRequest := range h.activeRequests {
		if now.Sub(userRequest.createdAt) > h.requestTimeout {
			expiredRequests = append(expiredRequests, userRequest)
		}
	}
	h.mu.RUnlock()

	for _, er := range expiredRequests {
		responses := er.copiedResponses()
		var nodeResponses strings.Builder
		for nodeKey, nodeResponse := range responses {
			_, _ = fmt.Fprintf(&nodeResponses, "%s ---::: %v               ", nodeKey, nodeResponse)
		}
		nodeResponsesStr := nodeResponses.String()
		err := h.sendResponse(ctx, er, h.errorResponse(er.req, api.RequestTimeoutError, errors.New("request expired without getting quorum of responses from nodes. Available responses: "+nodeResponsesStr), []byte(nodeResponsesStr)))
		if err != nil {
			h.lggr.Errorw("error sending response to user", "requestID", er.req.ID, "error", err)
		}
	}
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L394-401)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L404-419)
```go
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
		if cachedPublicKey == nil {
			// Not found in cache. Fetch from nodes.
			ar, err := h.newActiveRequest(req, callback)
			if err != nil {
				h.lggr.Errorw("failed to create new activeRequest", "error", err)
				return err
			}
			return h.handlePublicKeyGet(ctx, ar)
		}
		h.lggr.Debugw("returning cached public key response")
		return h.handlePublicKeyGetSynchronously(ctx, req, publicKeyResponseBytes, callback)
```

**File:** core/services/gateway/handlers/vault/handler.go (L457-472)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L736-744)
```go
func (h *handler) fanOutToVaultNodes(ctx context.Context, l logger.Logger, ar *activeRequest) error {
	var nodeErrors []error
	for _, node := range h.donConfig.Members {
		err := h.don.SendToNode(ctx, node.Address, &ar.req)
		if err != nil {
			nodeErrors = append(nodeErrors, err)
			l.Errorw("error sending request to node", "node", node.Address, "error", err)
		}
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-45)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
```
