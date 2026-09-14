This confirms an unbounded-cardinality metrics DoS reachable from unauthenticated/unprivileged clients hitting the gateway's public HTTP endpoint.

### Title
Unbounded OpenTelemetry metric cardinality from attacker-controlled JSON-RPC `method` field enables gateway resource-exhaustion DoS - (File: `core/services/gateway/gateway.go`)

### Summary
`gateway.ProcessRequest`, which handles every inbound HTTP request to the Gateway's user-facing port, extracts the JSON-RPC `method` field directly from the untrusted request body and passes it as an OpenTelemetry metric attribute without validating it against an allowlist of known methods, exactly the bug class described in the Vapor advisory (unbounded per-path counters/timers draining the metrics backend/host).

### Finding Description
In `core/services/gateway/gateway.go`, `ProcessRequest` decodes the raw JSON-RPC request and, for the non-legacy path, sets `method = jsonRequest.Method` directly from client input [1](#0-0) . This `method` string is later recorded as an attribute value on two metric instruments regardless of whether the method is recognized/supported: [2](#0-1) 

The underlying metrics implementation in `core/services/gateway/monitoring/metrics.go` attaches the raw `method` string as an `attribute.String("method", method)` label on both a histogram (`userMsgHandleDuration`) and a counter (`userMsgHandleCount`): [3](#0-2) 

Unlike the `jsonRequest.ID` field, which is explicitly capped at 200 characters "to prevent abuse" [4](#0-3) , the `method` field has no length restriction and no allowlist check before being used as a metric label. Any client can send JSON-RPC requests with unique/random `method` strings (the request only needs to pass `jsonRequest.ServiceName()` resolution to a known handler, or fails earlier and never reaches this code path — but the metric recording occurs even in the error/timeout branch at line 283-287, using whatever attacker-supplied `method` was parsed, before the handler validates or rejects the unsupported method).

This mirrors the exact CWE-400/GHSA-gcj9-jj38-hwmc pattern: an internet-facing HTTP-backed service creates a new, permanent time-series/label combination for every distinct value of an attacker-controlled string, causing unbounded memory growth in the OpenTelemetry/Prometheus metrics backend (label cardinality explosion) that can eventually exhaust the Gateway host's or its downstream metrics collector's memory.

### Impact Explanation
An unauthenticated/unprivileged client with network access to the Gateway's user-facing HTTP port (`GetUserPort()`) can repeatedly send JSON-RPC requests with distinct `method` values, causing the metrics SDK (and any Prometheus/OTel collector behind it) to allocate a new label set/time series per unique value. Over time this drains memory on the Gateway node and potentially on downstream metrics infrastructure, degrading or crashing the service — a resource-exhaustion Denial of Service.

### Likelihood Explanation
High likelihood: no authentication, no allowlist check, and no length/format restriction on the `method` value is applied before it is used as a metric label, and the code path is reached on every single inbound HTTP request to the Gateway.

### Recommendation
Before recording `userMsgHandleDuration`/`userMsgHandleCount` (and any other user-input-derived metric attributes), normalize the `method` value to a bounded, known set — e.g., rewrite any method not in the handler's supported method list to a fixed sentinel such as `"unknown"` or `"unsupported_method"`, mirroring the Vapor patch that rewrites undefined routes to `vapor_route_undefined`. Additionally, consider capping/validating the `method` field length similarly to the existing `jsonRequest.ID` length check.

### Proof of Concept
1. Start a Gateway with metrics/OTel bootstrapped.
2. Send repeated HTTP POST requests to the Gateway's user port with a JSON-RPC body such as `{"jsonrpc":"2.0","id":"1","method":"<random-unique-string-N>","params":{}}` for N = 1..100000, varying the method each time.
3. Observe that `userMsgHandleDuration`/`userMsgHandleCount` metrics accumulate a new label/time-series per unique `method` value, growing unboundedly in the metrics backend/collector memory.

### Citations

**File:** core/services/gateway/gateway.go (L231-234)
```go
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

**File:** core/services/gateway/gateway.go (L281-290)
```go
	response, err := callback.Wait(ctx)
	duration := time.Since(startTime)
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
