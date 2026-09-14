Based on my investigation, I found a genuine analog: the gateway's `ProcessRequest` performs full JSON-RPC parsing before any rate limiting is applied, with only a global body-size cap and no per-sender/IP quota gating the parsing step.

### Title
JSON-RPC Gateway Parses Full Request Before Any Rate Limiting, Enabling Memory-Amplification DoS to Bypass Quota Controls - (File: core/services/gateway/gateway.go)

### Summary
### Finding Description
In the Chainlink Gateway, incoming HTTP requests are read up to a size limit and handed to `gateway.ProcessRequest`, which immediately performs JSON decoding via `jsonrpc2.DecodeRequest[json.RawMessage]` and `g.codec.DecodeJSONRequest(jsonRequest)` before any rate limiter, quota, or per-sender check is consulted [1](#0-0) . Only after this parsing does the code look up a handler and dispatch to `HandleLegacyUserMessage`/`HandleJSONRPCUserMessage`, where the *only* rate limiting present in the codebase (e.g. per-workflow-owner limits in the HTTP Trigger handler, or per-sender limits in the vault handler) is applied [2](#0-1) .

The HTTP layer (`httpServer.handleRequest`) only enforces a global `MaxRequestBytesLimiter` byte-size cap before reading the body — this is a size ceiling, not a per-IP/per-sender rate or quota control [3](#0-2) . There is no global parsing semaphore and no pre-parse per-IP limiting anywhere in this pipeline, matching the bug class in the report: unauthenticated JSON parsing work (with the inherent decode-to-`Value`/struct memory amplification of `encoding/json`) happens unconditionally for every request up to the size limit, before the quota mechanisms that are supposed to bound resource consumption ever run.

This means the actual rate/quota enforcement that exists in this codebase (workflow rate limiter, vault sender rate limiter) can be starved or bypassed at the resource level: an attacker can flood the endpoint with maximally-sized JSON bodies designed for parsing overhead (deeply nested arrays/objects, long strings) and consume CPU/memory on every single request, regardless of whether that request will ultimately be rejected by a downstream per-sender limiter, since the limiter is never reached until parsing completes.

### Impact Explanation
An unauthenticated/unprivileged actor can repeatedly send POST requests up to the configured `MaxRequestBytesLimiter` size with content engineered to maximize `encoding/json` allocation overhead. Because parsing occurs unconditionally before any quota check in `ProcessRequest`, the existing rate-limiting protections (workflow-owner or vault per-sender limits) provide no defense against this — the resource cost has already been paid by the time those checks would apply or reject the request. Repeated concurrent requests from one or many source IPs can drive sustained CPU and memory pressure on the gateway node, degrading service for legitimate DON/workflow traffic. This is a resource-exhaustion/quota-bypass class issue rather than a direct authentication or fund-movement bypass.

### Likelihood Explanation
The gateway HTTP endpoint accepting JSON-RPC bodies is internet-facing and reachable by any unauthenticated caller (JWT auth is optional per `authHeader` handling in `handleRequest`) [4](#0-3) . No CAPTCHA, connection throttling, or pre-parse quota exists in the reachable path, so exploitation only requires network access and the ability to send repeated POST requests — a low bar for likelihood.

### Recommendation
1. Apply a pre-parsing, per-IP (or per-connection) rate limiter in `httpServer.handleRequest` before reading/parsing the body, not just a size cap.
2. Introduce a global concurrency/semaphore limit specifically around the JSON decode path in `gateway.ProcessRequest` (both `jsonrpc2.DecodeRequest` and `codec.DecodeJSONRequest` calls) to cap concurrent parsing work independent of downstream handler-specific limiters.
3. Extend quota/rate-limiting coverage so it is enforced consistently across all message types dispatched from `ProcessRequest`, not only within specific handlers like the HTTP Trigger or vault handler.

### Proof of Concept
1. Send repeated POST requests to the gateway's configured HTTP path with a JSON-RPC body sized near the `MaxRequestBytesLimiter` limit, containing deeply nested/large arrays or long strings inside `params`.
2. Because `gateway.ProcessRequest` calls `jsonrpc2.DecodeRequest` and `codec.DecodeJSONRequest` unconditionally before any handler-level rate limiter runs [5](#0-4) , each request incurs full parsing/allocation cost regardless of whether it will later be quota-rejected.
3. Repeating this from a single or few IPs (no per-IP limiting exists in `httpServer.handleRequest`) accumulates memory/CPU load proportional to request count × payload amplification factor, degrading gateway availability.

### Citations

**File:** core/services/gateway/gateway.go (L221-234)
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
```

**File:** core/services/gateway/gateway.go (L267-276)
```go
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

**File:** core/services/gateway/network/httpserver.go (L211-224)
```go
	maxRequestBytes, err := s.config.MaxRequestBytesLimiter.Limit(r.Context())
	if err != nil {
		msg := "Failed to get request size limit"
		s.lggr.Errorw(msg, "err", err)
		http.Error(w, msg, http.StatusInternalServerError)
		return
	}
	source := http.MaxBytesReader(nil, r.Body, int64(maxRequestBytes))
	rawMessage, err := io.ReadAll(source)
	if err != nil {
		s.lggr.Error("error reading request", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}
```

**File:** core/services/gateway/network/httpserver.go (L226-234)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
```
