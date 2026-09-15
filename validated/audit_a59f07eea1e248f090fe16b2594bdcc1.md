Audit Report

## Title
Unbounded OpenTelemetry metric cardinality from attacker-controlled JSON-RPC `method` field enables gateway resource-exhaustion DoS - (File: `core/services/gateway/gateway.go`)

## Summary
`gateway.ProcessRequest` extracts the JSON-RPC `method` field directly from an unauthenticated, attacker-controlled HTTP request body and passes it unmodified as an OpenTelemetry metric attribute value, with no allowlist or length validation applied before recording [1](#0-0) . This lets any client reaching the Gateway's public user port generate unbounded label cardinality in the `platform_gateway_user_msg_handler_duration_ms`/`platform_gateway_user_msgs_handled_total` metrics.

## Finding Description
In `ProcessRequest`, `method` is set from `jsonRequest.Method` (or `msg.Body.Method` for legacy requests) straight from the decoded, unauthenticated user request body [1](#0-0) . Unlike `jsonRequest.ID`, which is explicitly capped at 200 characters "to prevent abuse" [2](#0-1) , `method` has no length cap or allowlist check in `gateway.go` before it is used as a metric attribute in both the timeout branch and the normal-completion branch [3](#0-2) . `GatewayMetrics.RecordUserMsgHandlerDuration`/`RecordUserMsgHandlerInvocation` attach the raw `method` string as an `attribute.String("method", method)` label on a histogram and counter instrument with no sanitization [4](#0-3) .

Critically, this is reachable even for unsupported/unknown methods in at least the `vault` and `confidentialrelay` handlers, whose `HandleJSONRPCUserMessage` implementations return `nil` error after routing an "unsupported method" response through the callback channel rather than returning an error from the call itself [5](#0-4) , confirmed by the test asserting a `nil` error return from `HandleJSONRPCUserMessage` on an unsupported method [6](#0-5) . Because `err == nil` in `ProcessRequest`, execution proceeds past the early-return branch at line 277-278 straight into the metric-recording calls at lines 285-286/289-290, using the raw, attacker-chosen `method` string as the label value — with no allowlist rewrite to a bounded sentinel value. The Gateway's user-facing HTTP endpoint (`GetUserPort()`) accepts unauthenticated JSON-RPC POST bodies at `/user`, as shown in the sample config and integration test, which do not require prior login or API key [7](#0-6) [8](#0-7) .

For handlers wired via `multiHandler`, an unrecognized method causes `getHandler` to return an error, which propagates out of `HandleJSONRPCUserMessage` and triggers the early error return in `ProcessRequest` before any metric is recorded [9](#0-8)  — but this does not close the gap for handlers (like `vault`/`confidentialrelay`) that swallow the "unsupported method" case internally, or for any legitimate-but-attacker-chosen arbitrary method strings sent to known handlers, all of which reach the unsanitized metric recording code.

## Impact Explanation
This maps to a resource-exhaustion Denial-of-Service against the Gateway's metrics pipeline (CWE-400/unbounded cardinality class): an unauthenticated network client can force creation of unbounded new time-series/label combinations in the OpenTelemetry SDK and any downstream Prometheus/collector backend, degrading or exhausting memory on the Gateway host or its metrics infrastructure over time.

## Likelihood Explanation
High likelihood — no authentication, no allowlist, and no length restriction is applied to `method` before it becomes a metric label, and for handlers such as `vault` and `confidentialrelay`, the "unsupported method" code path returns `nil` from `HandleJSONRPCUserMessage`, guaranteeing metric recording occurs on every such request, repeatable indefinitely by an unprivileged remote client.

## Recommendation
Normalize the `method` value in `gateway.go` before passing it to `RecordUserMsgHandlerDuration`/`RecordUserMsgHandlerInvocation`: rewrite any value not present in the resolved handler's `Methods()` allowlist to a fixed sentinel (e.g., `"unknown"`), and/or cap its length similarly to the existing `jsonRequest.ID` check.

## Proof of Concept
1. Start a Gateway configured with a `vault` or `confidentialrelay` handler and OTel/Prometheus metrics enabled.
2. Send repeated unauthenticated HTTP POST requests to the Gateway's user port (`/user`) with distinct JSON-RPC bodies: `{"jsonrpc":"2.0","id":"<id>","method":"<random-unique-string-N>","params":{...valid params...}}` for N = 1..100000.
3. Because the `vault`/`confidentialrelay` handler's `HandleJSONRPCUserMessage` returns `nil` even for unsupported methods, `ProcessRequest` proceeds to call `g.gMetrics.RecordUserMsgHandlerDuration`/`RecordUserMsgHandlerInvocation` with each unique raw `method` string.
4. Observe the metrics backend/collector accumulating one new time series per unique `method` value.

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

**File:** core/services/gateway/handlers/vault/handler.go (L422-424)
```go
	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L817-845)
```go
	t.Run("unsupported method", func(t *testing.T) {
		var wg sync.WaitGroup
		h, callback, don, _ := setupHandler(t)
		don.AssertNotCalled(t, "SendToNode")

		unsupportedMethodRequest := jsonrpc.Request[json.RawMessage]{
			ID:     "2",
			Method: "vault.unsupported.method",
			Params: (*json.RawMessage)(&params),
		}

		wg.Go(func() {
			resp, err := callback.Wait(t.Context())
			if !assert.NoError(t, err) { //nolint:testifylint // require illegal inside wg.Go goroutine
				return
			}
			var secretsResponse jsonrpc.Response[vaultcommon.CreateSecretsResponse]
			err = json.Unmarshal(resp.RawResponse, &secretsResponse)
			if !assert.NoError(t, err) { //nolint:testifylint // require illegal inside wg.Go goroutine
				return
			}
			assert.Equal(t, unsupportedMethodRequest.ID, secretsResponse.ID, "Request ID should match")
			assert.Contains(t, secretsResponse.Error.Message, "unsupported method(vault.unsupported.method)")
			assert.Equal(t, api.ToJSONRPCErrorCode(api.UnsupportedMethodError), secretsResponse.Error.Code, "Error code should match")
		})

		err := h.HandleJSONRPCUserMessage(t.Context(), unsupportedMethodRequest, callback)
		require.NoError(t, err)
		wg.Wait()
```

**File:** core/scripts/gateway/sample_config.toml (L1-9)
```text
[UserServerConfig]
Port = 8080
Path = "/user"
ContentTypeHeader = "application/jsonrpc"
ReadTimeoutMillis = 1000
WriteTimeoutMillis = 1000
RequestTimeoutMillis = 1000
MaxRequestBytes = 10_000
CORSEnabled = false
```

**File:** core/services/gateway/integration_tests/gateway_integration_test.go (L195-230)
```go
	userPort, nodePort := gateway.GetUserPort(), gateway.GetNodePort()
	userURL := fmt.Sprintf("http://localhost:%d/user", userPort)
	nodeURL := fmt.Sprintf("ws://localhost:%d/node", nodePort)
	require.Equal(t, http.StatusServiceUnavailable, getHTTPStatus(t, fmt.Sprintf("http://localhost:%d/health", userPort)))
	require.Equal(t, http.StatusOK, getHTTPStatus(t, fmt.Sprintf("http://localhost:%d/health", nodePort)))

	// Launch Connector
	client := &client{privateKey: nodeKeys.PrivateKey}
	// client acts as a signer here
	connector, err := connector.NewGatewayConnector(parseConnectorConfig(t, nodeConfigTemplate, nodeKeys.Address, nodeURL), client, clockwork.NewRealClock(), lggr, "")
	require.NoError(t, err)
	require.NoError(t, connector.AddHandler(t.Context(), []string{"test"}, client))
	client.connector = connector
	servicetest.Run(t, connector)
	require.Eventually(t, func() bool {
		return getHTTPStatus(t, fmt.Sprintf("http://localhost:%d/health", userPort)) == http.StatusOK
	}, testutils.WaitTimeout(t), testutils.TestInterval)

	// Send requests until one of them reaches Connector (i.e. the node)
	gomega.NewGomegaWithT(t).Eventually(func() bool {
		req := newJSONRPCHTTPRequestObject(t, messageID1, userURL, userKeys.PrivateKey)
		httpClient := &http.Client{}
		resp, doErr := httpClient.Do(req) // could initially return error if Gateway is not fully initialized yet
		if doErr == nil {
			resp.Body.Close()
		}
		return client.done.Load()
	}, testutils.WaitTimeout(t), testutils.TestInterval).Should(gomega.BeTrue())

	// Send another request and validate that response has correct content and sender
	req := newJSONRPCHTTPRequestObject(t, messageID2, userURL, userKeys.PrivateKey)
	httpClient := &http.Client{}
	resp, err := httpClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()
	require.Equal(t, http.StatusOK, resp.StatusCode)
```

**File:** core/services/gateway/multihandler.go (L62-69)
```go
func (m *multiHandler) HandleJSONRPCUserMessage(ctx context.Context, jsonRequest jsonrpc.Request[json.RawMessage], callback handlers.Callback) error {
	h, err := m.getHandler(jsonRequest.Method)
	if err != nil {
		return fmt.Errorf("failed to get handler for method %s: %w", jsonRequest.Method, err)
	}

	return h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
}
```
