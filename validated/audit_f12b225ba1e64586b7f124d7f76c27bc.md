### Title
Missing allowlist/rate-limiting in Gateway's legacy WebAPI-trigger message path allows unauthenticated DoS amplification to all DON nodes - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The Gateway's public-facing HTTP endpoint accepts unauthenticated JSON-RPC "legacy" messages and routes `web_api_trigger` requests through `handler.HandleLegacyUserMessage`, which explicitly skips authorization/rate-limiting (`// TODO: apply allowlist and rate-limiting here`) and unconditionally broadcasts the request to every member of the DON. This mirrors the reported bug class ("attacker crafts many valid requests to overload downstream processing/gas"): here an unauthenticated client can cheaply cause 1:N amplified fan-out work on every capability node in a DON, and grow an in-memory callback map that is only pruned periodically.

### Finding Description
The gateway's HTTP server accepts any POST request without authentication and forwards raw bytes to `ProcessRequest`: [1](#0-0) 

`ProcessRequest` decodes the request and, for legacy (DonID-based) requests, calls `h.HandleLegacyUserMessage`: [2](#0-1) 

`HandleLegacyUserMessage` in the WebAPI capabilities handler validates payload shape/timestamp only, then — with an explicit unimplemented TODO for allowlisting/rate-limiting — stores a callback and fans the request out to **every** DON member: [3](#0-2) 

The only mitigations present are: request ID length cap (200 chars), a stale-timestamp check, and a bounded/periodically-pruned `savedCallbacks` map (`defaultMaxSavedCallbacks = 20000`, pruned every 30s): [4](#0-3) [5](#0-4) 

None of these prevent a high-volume unauthenticated request stream: each request is a single "valid-looking" HTTP POST but results in `len(donConfig.Members)` outbound `SendToNode` calls, and every DON node independently processes and acts on the forwarded trigger. This is structurally analogous to the reported issue where many individually-valid, cheaply-crafted inputs (signed orders) are used to amplify on-chain processing cost far beyond what a single request should cost — except here the amplification is against the DON member nodes' processing capacity and the gateway's own in-process memory (map growth) rather than gas.

### Impact Explanation
An unauthenticated client can flood the gateway's HTTP path with `web_api_trigger` requests. Each accepted request is broadcast to all DON member nodes, multiplying the load by the DON size, and each also occupies gateway memory in `savedCallbacks` until the 30s prune cycle runs (or up to `MaxSavedCallbacks`). Sustained flooding can degrade or deny the trigger-processing capability across an entire DON, and workflow legitimate triggers may be starved or delayed since there's no per-sender/global quota preventing an unlimited stream of syntactically-valid requests from being accepted and dispatched.

### Likelihood Explanation
The endpoint is internet-facing and unauthenticated for the legacy path; the only gating factors are payload well-formedness and a non-zero/non-stale timestamp, both trivially satisfiable by any caller. The code contains an explicit, unresolved `TODO: apply allowlist and rate-limiting here` comment confirming this control is known-missing rather than intentionally omitted for a trusted-only path.

### Recommendation
Implement sender allowlisting and per-sender/global rate limiting before accepting and fanning out legacy `web_api_trigger` messages, consistent with what is already done for the newer JSON-RPC vault/HTTP-trigger-v2 paths (which use JWT-based authentication and multi-dimensional rate limiting, e.g. `core/services/gateway/handlers/capabilities/v2`). At minimum, bound the rate of accepted legacy triggers per source and reduce `savedCallbacks` prune interval / cap under load, and consider requiring the newer authenticated JSON-RPC handler path exclusively, deprecating the unauthenticated legacy route.

### Proof of Concept
1. Send repeated POST requests to the gateway's configured HTTP path with a well-formed legacy `api.Message` body: `Body.DonID` set to a valid DON ID, `Body.Method = "web_api_trigger"`, `Body.MessageID` unique per request, and `Payload.Timestamp` set to `time.Now().Unix()`.
2. Observe that `gateway.ProcessRequest` → `handler.HandleLegacyUserMessage` accepts each request without any allowlist/auth/rate-limit check (per the code cited above) and calls `don.SendToNode` for every member in `donConfig.Members`.
3. Repeating this at volume from a single unauthenticated client multiplies load across all DON nodes and grows `h.savedCallbacks` until the next prune cycle, demonstrating unauthenticated DoS amplification.

### Citations

**File:** core/services/gateway/network/httpserver.go (L226-241)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
	duration := time.Since(startTime)
	s.hMetrics.RecordRequestDuration(r.Context(), httpStatusCode, duration)
	s.hMetrics.RecordRequestCount(r.Context(), httpStatusCode)

	w.Header().Set("Content-Type", s.config.ContentTypeHeader)
	w.WriteHeader(httpStatusCode)
	_, err = w.Write(rawResponse) //nolint:gosec // G705: response body is written with an explicit Content-Type, not rendered as HTML
```

**File:** core/services/gateway/gateway.go (L253-279)
```go
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
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-45)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-334)
```go
func (h *handler) pruneCallbacks() {
	h.mu.Lock()
	defer h.mu.Unlock()

	// First, remove expired callbacks.
	maxAge := time.Duration(h.config.CallbackMaxAgeSec) * time.Second
	now := time.Now()
	var expired int
	for id, cb := range h.savedCallbacks {
		if now.Sub(cb.createdAt) > maxAge {
			delete(h.savedCallbacks, id)
			expired++
		}
	}

	// If there are still too many callbacks, sort them by creation time and remove the oldest ones.
	maxSize := h.config.MaxSavedCallbacks
	var evicted int
	if len(h.savedCallbacks) > maxSize {
		type entry struct {
			id        string
			createdAt time.Time
		}
		entries := make([]entry, 0, len(h.savedCallbacks))
		for id, cb := range h.savedCallbacks {
			entries = append(entries, entry{id, cb.createdAt})
		}
		sort.Slice(entries, func(i, j int) bool {
			return entries[i].createdAt.Before(entries[j].createdAt)
		})
		// Trim to maxSize/2 to avoid sorting the list too frequently.
		for _, e := range entries[:len(entries)-maxSize/2] {
			delete(h.savedCallbacks, e.id)
			evicted++
		}
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-420)
```go
	// TODO: apply allowlist and rate-limiting here
	if msg.Body.Method != MethodWebAPITrigger {
		h.lggr.Errorw("unsupported method", "method", body.Method)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UnsupportedMethodError),
				"invalid method "+msg.Body.Method,
				nil,
			),
			ErrorCode: api.UnsupportedMethodError,
		})
	}
	req, err := common.ValidatedRequestFromMessage(msg)
	if err != nil {
		h.lggr.Errorw(ErrTransformingMessageToRequest)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrTransformingMessageToRequest,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```
