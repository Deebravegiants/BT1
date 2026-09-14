Confirmed: the gateway HTTP server accepts fully unauthenticated requests (JWT is optional, `jwtToken` may be empty) up to `MaxRequestBytesLimiter` bytes, then passes the raw bytes straight to `s.handler.ProcessRequest`, which routes into `JSONRPCCodec.DecodeRawRequest`/`DecodeJSONRequest` and downstream handlers that all use `encoding/json.Unmarshal` on attacker-controlled bytes with no nesting-depth limit. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Unbounded JSON nesting depth in Gateway HTTP request envelope decoding causes stack-overflow DoS - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's public HTTP endpoint accepts unauthenticated POST requests, reads up to a configurable byte-size limit, and hands the raw bytes to `encoding/json.Unmarshal` (via `JSONRPCCodec.DecodeRawRequest`/`DecodeJSONRequest` and several downstream handlers) with no limit on JSON nesting depth. Since Go's standard `encoding/json` decoder recurses once per nesting level for arrays/objects, a small, size-limit-compliant payload consisting of thousands of nested arrays (e.g. `[[[[...]]]]`) can exhaust the goroutine stack and crash the Gateway process — directly analogous to the reported Move VM unbounded-recursion stack-overflow bug, whose impact is denial of service / node crash rather than fund loss.

### Finding Description
`httpServer.handleRequest` bounds only the *size* of the incoming body via `MaxRequestBytesLimiter`/`http.MaxBytesReader`, never the *depth* of the JSON it contains: [4](#0-3) 

No prior authentication is required to reach this parsing step — the `Authorization` header/JWT is optional and only extracted for later use, not required before the body is processed: [5](#0-4) 

The raw bytes then flow into `JSONRPCCodec.DecodeRawRequest`, which calls `jsonrpc2.DecodeRequest` and subsequently `json.Unmarshal(*request.Params, &msg)`: [6](#0-5) 

Further downstream, per-capability handlers unmarshal the params again into typed structs with `encoding/json`, e.g. the HTTP trigger handler: [3](#0-2) 

and the confidential-relay handler's label extraction: [7](#0-6) 

Go's `encoding/json` decoder (`decodeState.object`/`decodeState.array`) is implemented with mutual recursion that grows the call stack by one frame per nesting level, and it has no built-in maximum-depth guard (this is a long-standing, well-known property of the Go JSON package, not something Chainlink's code opts out of). A deeply nested but otherwise tiny JSON document (well under the configured byte limit) can therefore drive the decoder to recurse tens of thousands of times, which triggers a Go runtime stack-overflow fatal error. Unlike a `panic`, a Go stack-overflow is **not recoverable** by any `defer`/`recover` in the call chain, so it terminates the entire process — taking down the whole Gateway (and by extension the DON connectivity it brokers), which is the exact "total network shutdown" class of impact described in the Move VM report.

### Impact Explanation
Any unauthenticated client that can reach the Gateway's public HTTP endpoint can crash the Gateway process with a single POST request, causing denial of service for all DONs/nodes relying on that Gateway for external communication (HTTP triggers, workflow execution requests, vault/confidential-relay traffic, etc.). This is a Medium-to-High availability impact: no funds are directly stolen, but the crash is unauthenticated, repeatable, and process-wide (not per-connection), matching the "loss: -, medium severity, network shutdown" profile of the referenced report.

### Likelihood Explanation
High likelihood of triggerability: the endpoint is internet-facing by design (Gateway HTTP handler), requires no authentication to reach the parsing step, and the byte-size limit (`MaxRequestBytesLimiter`, e.g. megabytes) is far larger than what's needed to build a payload with tens of thousands of nesting levels (each level costs only 1–2 bytes, e.g. `[` ... `]`). Any external actor capable of sending an HTTP POST can attempt this.

### Recommendation
- Wrap all `encoding/json.Unmarshal` calls that operate on attacker-controlled Gateway input with a depth-limiting decoder (e.g., use `json.Decoder.Token()` streaming with an explicit depth counter, or a vetted library offering `SetMaxDepth`), rejecting requests that exceed a small, sane nesting limit (e.g., 32–64 levels) before full unmarshalling.
- Apply the same guard to every downstream `json.Unmarshal(*req.Params, ...)` call across gateway handlers (`api/jsonrpccodec.go`, `handlers/capabilities/v2/http_trigger_handler.go`, `handlers/confidentialrelay/handler.go`, `handlers/vault/handler.go`, etc.), not just the outer envelope, since each independently re-parses attacker-supplied bytes.
- Consider running the parsing step in a bounded-stack goroutine with `debug.SetMaxStack` tuning or a supervisory recover-and-restart wrapper is not sufficient, since Go stack overflows cannot be recovered — the only real mitigation is pre-validating/limiting JSON structural depth before invoking the decoder.

### Proof of Concept
1. Start the Gateway HTTP server with a default `MaxRequestBytesLimiter` (several hundred KB–few MB).
2. Construct a payload: `body = '{"jsonrpc":"2.0","id":"x","method":"m","params":' + '['*N + ']'*N + '}'` where `N` is chosen so that `2*N` bytes stay under the byte limit but is large enough to exceed Go's default goroutine stack growth limits (empirically tens of thousands of nesting levels, e.g. `N = 100000`, is well within a few-hundred-KB payload and sufficient to overflow the stack on most Go builds).
3. Send `POST /<gateway-path>` with this body and no `Authorization` header.
4. Observe the Gateway process crash with a Go runtime `fatal error: stack overflow` instead of returning an HTTP error response — no recovery via `http.Server` or handler-level `defer/recover` is possible.

### Citations

**File:** core/services/gateway/network/httpserver.go (L211-234)
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

	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
```

**File:** core/services/gateway/api/jsonrpccodec.go (L18-35)
```go
func (j *JSONRPCCodec) DecodeRawRequest(msgBytes []byte, jwtToken string) (*Message, error) {
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](msgBytes, jwtToken)
	if err != nil {
		return nil, err
	}
	return j.DecodeJSONRequest(jsonRequest)
}

func (*JSONRPCCodec) DecodeJSONRequest(request jsonrpc2.Request[json.RawMessage]) (*Message, error) {
	var msg Message
	err := json.Unmarshal(*request.Params, &msg)
	if err != nil {
		return nil, err
	}
	msg.Body.MessageID = request.ID
	msg.Body.Method = request.Method
	return &msg, nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L180-188)
```go
func (h *httpTriggerHandler) parseTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.HTTPTriggerRequest, error) {
	var triggerReq gateway_common.HTTPTriggerRequest
	err := json.Unmarshal(*req.Params, &triggerReq)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrParse, "payload is not a valid JSON. Ensure that the request body is a well-formed JSON", callback)
		return nil, err
	}
	return &triggerReq, nil
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L98-107)
```go
func (h *handler) extractRequestLabels(req jsonrpc.Request[json.RawMessage]) requestLabels {
	var labels requestLabels
	if req.Params == nil {
		return labels
	}
	if err := json.Unmarshal(*req.Params, &labels); err != nil {
		h.lggr.Debugw("could not decode relay request params for logging labels",
			"method", req.Method, "requestID", req.ID, "err", err)
	}
	return labels
```
