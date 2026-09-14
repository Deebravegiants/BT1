### Title
Unauthenticated user-controlled JSON-RPC `method` string recorded as unbound-cardinality OTel metric label in the Gateway's user-facing HTTP endpoint - (File: core/services/gateway/gateway.go)

### Summary
`gateway.ProcessRequest`, the entry point invoked by the Gateway's public HTTP server for every request arriving on the user-facing port, takes the JSON-RPC `method` field verbatim from the incoming, unauthenticated client request and uses it as a metric attribute value without validating it against any allow-list of known methods.

### Finding Description
In `(g *gateway) ProcessRequest`, the request `method` is read straight from client input before dispatch: [1](#0-0) 

Regardless of whether the handler call succeeds, times out, or errors, the raw `method` string is then passed into the gateway's OpenTelemetry metrics: [2](#0-1) 

Those calls attach `method` directly as an OTel attribute with no normalization ("unknown" bucket) or restriction to known handler methods: [3](#0-2) 

The `method` value originates from the JSON-RPC `method` field decoded from the raw client payload (`jsonRequest.Method` from `jsonrpc2.DecodeRequest`), which is attacker-controlled and unauthenticated at this stage — decoding happens before any per-handler authentication/authorization check (e.g., signature verification inside individual handlers such as `vault` or `confidentialrelay`) is performed. Handler-level method validation (e.g., `httpTriggerHandler.validateMethod`) rejects unknown methods with an error response, but this validation happens *inside* the handler after `ProcessRequest` has already dispatched the call — and crucially the metrics in `ProcessRequest` are recorded using the raw `method` string regardless of handler outcome, not a normalized/validated value. This mirrors the OpenTelemetry-Go Contrib `otelhttp` disclosure exactly: an attribute derived from unauthenticated, attacker-supplied request data (analogous to `http.method`/`User-Agent`) is fed into a metrics pipeline without cardinality bounding.

Every distinct JSON-RPC `method` string sent by any anonymous client produces a new time series in two histogram/counter instruments (`platform_gateway_user_msg_handler_duration_ms`, `platform_gateway_user_msgs_handled_total`), as well as via `promRequest`/`h.gMetrics` combined with `response.ErrorCode.String()`.

A partial mitigating control exists: `Telemetry.MetricCardinalityLimit` caps the OTel SDK's per-instrument attribute-set count (default 100000): [4](#0-3) 
However, this is a global safety-valve, not a fix — an attacker can still exhaust up to 100,000 unique series per instrument (multiplied across the two instruments and any error-code combinations) purely by varying the `method` string on unauthenticated JSON-RPC requests, well beyond legitimate cardinality (a handful of real method names), causing elevated memory/CPU usage in the metrics SDK and downstream collectors before the limit engages.

### Impact Explanation
An unauthenticated remote actor can repeatedly POST JSON-RPC requests to the Gateway's public HTTP endpoint with random `method` values (with no other valid content required to reach the metrics-recording code path — the request only needs to fail after `ServiceName()`/DON lookup or during handler processing). Each unique method string creates a new metric series, consuming memory in the OTel SDK aggregation store and downstream metrics backend. Sustained abuse can degrade or exhaust node/gateway memory and CPU, a denial-of-service condition consistent with CWE-770 (Allocation of Resources Without Limits).

### Likelihood Explanation
High. The Gateway's user-facing HTTP endpoint is explicitly designed to accept unauthenticated/public traffic (`GetUserPort`), and reaching the metric-recording lines requires no valid signature or credential — only a JSON body that decodes with a `method` field and passes basic ID-length and JSON syntax checks. No allow-listing or normalization of `method` occurs before the value reaches the metrics layer in `gateway.go`.

### Recommendation
Before recording `RecordUserMsgHandlerDuration`/`RecordUserMsgHandlerInvocation`, normalize `method` to a fixed, known set of legitimate handler/service methods (e.g., map any value not in an explicit allow-list to `"unknown"`), mirroring the fix applied upstream in `opentelemetry-go-contrib` PR #4277. Apply the same normalization anywhere else raw JSON-RPC/HTTP `method` strings are used as metric attributes in the gateway/capabilities handler metrics code (e.g., `core/services/gateway/handlers/capabilities/handler.go`, `core/capabilities/webapi/outgoing_connector_handler.go`) if those are reachable with unauthenticated/unvalidated method values.

### Proof of Concept
1. Identify the Gateway's user-facing HTTP endpoint (`config.Path` on the port returned by `GetUserPort`).
2. Send a large number of POST requests each with a distinct, randomly generated `method` field and a syntactically valid JSON-RPC envelope, e.g.:
   `{"jsonrpc":"2.0","id":"<id>","method":"<random-string-N>","params":{}}`
3. Ensure the `params`/service name lookup fails deterministically to reach either the "Service name not found" or the dispatch/timeout path in `ProcessRequest`; the `method` value is used for metric recording via `g.gMetrics.RecordUserMsgHandlerDuration`/`RecordUserMsgHandlerInvocation` at lines 285-290/289-290 in all these paths as long as a handler is found for the DON/service, or directly if handled and errored.
4. Observe growth in the number of distinct time series for `platform_gateway_user_msg_handler_duration_ms` / `platform_gateway_user_msgs_handled_total` and corresponding memory growth in the metrics SDK, up to the configured `MetricCardinalityLimit` (default 100000), at which point metric-recording degrades/drops but resource consumption up to that point is already attacker-controlled.

### Citations

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

**File:** core/services/gateway/gateway.go (L283-290)
```go
	if err != nil {
		response := api.RequestTimeoutError
		g.gMetrics.RecordUserMsgHandlerDuration(ctx, method, response.String(), duration)
		g.gMetrics.RecordUserMsgHandlerInvocation(ctx, method, response.String())
		return newError(jsonRequest.ID, response, "handler timeout: "+err.Error())
	}
	g.gMetrics.RecordUserMsgHandlerDuration(ctx, method, response.ErrorCode.String(), duration)
	g.gMetrics.RecordUserMsgHandlerInvocation(ctx, method, response.ErrorCode.String())
```

**File:** core/services/gateway/monitoring/metrics.go (L51-63)
```go
func (m *GatewayMetrics) RecordUserMsgHandlerDuration(ctx context.Context, method string, responseCode string, duration time.Duration) {
	m.userMsgHandleDuration.Record(ctx, duration.Milliseconds(), metric.WithAttributes(
		attribute.String("method", method),
		attribute.String("responseCode", responseCode),
	))
}

func (m *GatewayMetrics) RecordUserMsgHandlerInvocation(ctx context.Context, method string, responseCode string) {
	m.userMsgHandleCount.Add(ctx, 1, metric.WithAttributes(
		attribute.String("method", method),
		attribute.String("responseCode", responseCode),
	))
}
```

**File:** core/services/chainlink/config_telemetry.go (L278-283)
```go
func (b *telemetryConfig) MetricCardinalityLimit() int {
	if b.s.MetricCardinalityLimit == nil {
		return 100000
	}
	return *b.s.MetricCardinalityLimit
}
```
