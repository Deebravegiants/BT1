Audit Report

## Title
Unbounded growth of the Vault gateway `activeRequests` map via unauthenticated `MethodPublicKeyGet` requests can DoS the handler - (File: core/services/gateway/handlers/vault/handler.go)

## Summary
The Vault gateway handler's `HandleJSONRPCUserMessage` routes `MethodPublicKeyGet` requests directly to `newActiveRequest` whenever the public key cache is empty, entirely bypassing `requestProcessor.ProcessRequest` authorization [1](#0-0) . `newActiveRequest` inserts unconditionally into `h.activeRequests` with only a duplicate-ID check and no maximum-size enforcement, unlike the generic `common.requestCache` which explicitly caps `maxCacheSize` [2](#0-1) .

## Finding Description
The gateway's HTTP entrypoint `gateway.ProcessRequest` decodes an incoming JSON-RPC request and forwards it straight to `h.HandleJSONRPCUserMessage` with no upstream authentication or rate limiting beyond a 200-character ID length check [3](#0-2) . Inside the vault handler, `MethodPublicKeyGet` requests skip `requestProcessor.ProcessRequest` and go straight to `newActiveRequest` on a cache miss [1](#0-0) . `newActiveRequest` only rejects duplicate request IDs and never checks total map size before inserting into `h.activeRequests` [2](#0-1) . Entries are only reclaimed by the periodic `removeExpiredRequests` sweep, which runs every `defaultCleanUpPeriod` (5s) and only removes entries older than `h.requestTimeout` [4](#0-3) [5](#0-4) . No rate limiter or admission-control mechanism exists in the vault handler to cap the rate or count of `MethodPublicKeyGet` requests reaching `newActiveRequest`.

## Impact Explanation
An attacker who sustains a flood of unique-ID `MethodPublicKeyGet` requests faster than the cleanup cadence can reclaim can cause `h.activeRequests` to grow without bound, consuming memory and increasing lock hold time (`h.mu`) during the periodic scan, degrading the vault gateway handler's ability to process legitimate secrets create/update/delete/list requests for all users of that DON. This maps to a protocol/service-availability DoS impact against the gateway node.

## Likelihood Explanation
This is reachable by any unprivileged network client capable of sending HTTP requests to the gateway's user-facing port; the request only needs a unique, non-empty ID ≤200 characters and `Method: vaulttypes.MethodPublicKeyGet`, and requires no credentials, keys, or prior authorized state, making it straightforward and repeatable to sustain.

## Recommendation
Enforce a maximum size on `h.activeRequests` (mirroring `common.requestCache.maxCacheSize`) and reject new entries once the limit is reached, or apply a per-caller/global rate limiter ahead of `newActiveRequest` for unauthenticated `MethodPublicKeyGet` traffic.

## Proof of Concept
1. Start a gateway configured with the Vault handler and an empty/expired public key cache.
2. Send many JSON-RPC requests to the gateway's user HTTP endpoint with `Method: vaulttypes.MethodPublicKeyGet` and distinct `ID` values, at a rate exceeding the 5s cleanup interval / 30s default `requestTimeout`.
3. Observe `h.activeRequests` growing unbounded via internal handler metrics/memory profiling, and measure increased latency/lock contention on subsequent legitimate `MethodSecretsCreate`/`Update`/`Delete`/`List` requests handled by the same handler instance.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L279-299)
```go
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

**File:** core/services/gateway/handlers/vault/handler.go (L404-417)
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

**File:** core/services/gateway/gateway.go (L221-276)
```go
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
	} else {
		// Legacy request with DON ID - validate and fetch handler
		isLegacyRequest = true
		if err = msg.Validate(); err != nil {
			return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
		}
		handlerKey = msg.Body.DonID
		var ok bool
		h, ok = g.handlers[handlerKey]
		if !ok {
			return newError(jsonRequest.ID, api.UnsupportedDONIdError, "Unsupported DON ID: "+handlerKey)
		}
	}

	startTime := time.Now()
	var method string
	callback := handlerscommon.NewCallback()
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
```
