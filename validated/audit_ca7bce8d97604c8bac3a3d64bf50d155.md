Found it: `DecodeJSONRequest` in `core/services/gateway/api/jsonrpccodec.go` dereferences `*request.Params` without checking whether `Params` is nil. This is directly analogous to the klever-go `RawData` nil-pointer-deref bug class: an unauthenticated field of an incoming untrusted message is dereferenced without a nil guard, in a path reachable from an internet-facing gateway endpoint, and (as far as I could verify) with no `recover()` protecting the HTTP handler goroutine.

### Title
Unauthenticated nil-pointer panic in gateway JSON-RPC request decoding (`DecodeJSONRequest` dereferences nil `Params`) - ([File: core/services/gateway/api/jsonrpccodec.go])

### Summary
`(*JSONRPCCodec).DecodeJSONRequest` unconditionally dereferences `*request.Params` to unmarshal the legacy `Message` envelope, with no nil check, mirroring the klever-go `tx.RawData.Version` nil-deref pattern (dereferencing an optional/omittable sub-field of an untrusted wire message without a guard). [1](#0-0) 

### Finding Description
The gateway's HTTP handler reads the raw request body from any caller and passes it straight into `gateway.ProcessRequest`, which calls `jsonrpc2.DecodeRequest` and then `g.codec.DecodeJSONRequest(jsonRequest)`. [2](#0-1) [3](#0-2) 

`DecodeJSONRequest` performs `json.Unmarshal(*request.Params, &msg)` without checking `request.Params != nil` first:
```go
func (*JSONRPCCodec) DecodeJSONRequest(request jsonrpc2.Request[json.RawMessage]) (*Message, error) {
	var msg Message
	err := json.Unmarshal(*request.Params, &msg)   // request.Params may be nil -> panic
	...
``` [1](#0-0) 

`jsonrpc2.Request[json.RawMessage].Params` is a `*json.RawMessage` pointer field populated from client-controlled JSON; a JSON-RPC request that omits the `params` field (which is valid per the JSON-RPC 2.0 spec for notification-style/no-param requests) decodes with `Params == nil`. Dereferencing that nil pointer in `DecodeJSONRequest` triggers a runtime nil-pointer panic, exactly the same bug class as `tx.RawData.Version` being dereferenced when `RawData` is omitted from the wire message in the klever-go advisory.

Other request-decoding paths in the same package correctly guard against this (e.g., `ValidatedMessageFromReq` explicitly checks `if req.Params == nil` before unmarshalling), confirming this is a known-necessary guard that was omitted specifically in `DecodeJSONRequest`. [4](#0-3) 

The call chain from an unauthenticated HTTP request to the panic is:
```
httpServer.handleRequest (unauthenticated POST)
  -> gateway.ProcessRequest
    -> jsonrpc2.DecodeRequest[json.RawMessage]   // Params optional, no default set
    -> codec.DecodeJSONRequest(jsonRequest)      // *request.Params dereferenced, no nil check
``` [5](#0-4) [3](#0-2) 

I was unable to fully verify, within the available context, whether the underlying HTTP server (`net/http.Server` in `httpserver.go`) or any wrapping middleware installs a per-request `recover()`. The plain `http.HandlerFunc(server.handleRequest)` shown does not itself contain a `recover()`, and Go's `net/http` server only recovers panics per-connection goroutine (logging and closing the connection) rather than crashing the whole process — this differs from the klever-go case where the entire process crashes. This is an important distinction: a panic here would likely only abort the single HTTP request/connection (Go's `net/http.Server` recovers per-handler-goroutine panics by default), not the whole gateway process, unless `ReadHeaderTimeout`/goroutine leaks or repeated panics exhaust resources.

### Impact Explanation
If reachable, this would let any unauthenticated client (the gateway HTTP endpoint requires no prior authentication before parsing the body) that sends a JSON-RPC request without a `params` field, or with `Method`/`ServiceName`, cause a panic in the request-handling goroutine of the gateway service. Given Go's standard `net/http` panic recovery on the server's own goroutine, the practical impact is most likely a single failed request / logged panic rather than a full process crash, which is a materially weaker impact than the CWE-476 "chain halt" scenario in the original report (which explicitly crashed the entire node process with no recover at any frame).

### Likelihood Explanation
Likelihood is high for triggering the nil dereference itself (trivial, unauthenticated, single malformed request), but I could not confirm with the tools available whether this path is actually reachable before other validations (e.g., whether `jsonrpc2.DecodeRequest` already defaults `Params` to a non-nil empty raw message, which would make this unreachable) or whether the process crashes vs. only the request goroutine. This uncertainty is due to `jsonrpc2.DecodeRequest`'s implementation living in the `chainlink-common` external package, which is outside the indexed repo scope and could not be inspected directly.

### Recommendation
Add a nil check on `request.Params` in `DecodeJSONRequest` before dereferencing, mirroring the existing guard in `ValidatedMessageFromReq`:
```go
func (*JSONRPCCodec) DecodeJSONRequest(request jsonrpc2.Request[json.RawMessage]) (*Message, error) {
	if request.Params == nil {
		return nil, errors.New("missing params attribute")
	}
	var msg Message
	err := json.Unmarshal(*request.Params, &msg)
	...
```
Additionally, wrap `httpServer.handleRequest` (and/or `gateway.ProcessRequest`) in a `recover()` as defense-in-depth so a single malformed message can never take down request processing goroutines, consistent with the `gin.Recovery()` middleware already used on the main node web router. [6](#0-5) 

### Proof of Concept
Send an unauthenticated POST to the gateway's configured HTTP path with a JSON-RPC request body that omits `params`, e.g.:
```json
{"jsonrpc":"2.0","id":"1","method":"anyMethod"}
```
This is decoded by `jsonrpc2.DecodeRequest[json.RawMessage]` into a `Request[json.RawMessage]` with `Params == nil` (assuming, unverified, that the library does not default it), then passed to `DecodeJSONRequest`, which executes `json.Unmarshal(*request.Params, &msg)` and panics with `invalid memory address or nil pointer dereference` on the nil `*json.RawMessage` dereference.

**Caveat on completeness:** I could not execute this PoC or inspect the `jsonrpc2.DecodeRequest` implementation (external `chainlink-common` module) to confirm end-to-end reachability and the exact runtime blast radius (single request vs. process crash). A Devin session with full filesystem/test access would be needed to confirm reachability and actual impact by running the equivalent of the original report's Go test harness against this code path.

### Citations

**File:** core/services/gateway/api/jsonrpccodec.go (L26-35)
```go
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

**File:** core/services/gateway/network/httpserver.go (L195-234)
```go
func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}

		// handle preflight requests
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
	}

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

**File:** core/services/gateway/gateway.go (L221-230)
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
```

**File:** core/services/gateway/handlers/common/message_util.go (L36-45)
```go
func ValidatedMessageFromReq(req *jsonrpc.Request[json.RawMessage]) (*api.Message, error) {
	if req.Version != "2.0" {
		return nil, errors.New("incorrect jsonrpc version")
	}
	if req.Method == "" {
		return nil, errors.New("empty method field")
	}
	if req.Params == nil {
		return nil, errors.New("missing params attribute")
	}
```

**File:** core/web/router.go (L64-72)
```go
	engine.Use(
		otelgin.Middleware("chainlink-web-routes",
			otelgin.WithTracerProvider(otel.GetTracerProvider())),
		limits.RequestSizeLimiter(config.WebServer().HTTPMaxSize()),
		loggerFunc(app.GetLogger()),
		gin.Recovery(),
		cors,
		secureMiddleware(tls.ForceRedirect(), tls.Host(), config.Insecure().DevWebServer()),
	)
```
