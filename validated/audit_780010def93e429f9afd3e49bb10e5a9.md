I have enough evidence to write up the finding now.

### Title
CORS Wildcard-Suffix Bypass in Gateway User HTTP Server Allows Cross-Origin Data Theft - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's internet-facing user HTTP server implements a custom CORS origin allowlist check, `isAllowedOrigin`, instead of using a vetted CORS library. When an operator configures a wildcard subdomain pattern (e.g. `https://*.ethereum.org`) in `CORSAllowedOrigins`, the matching logic uses a plain string-suffix comparison rather than a proper subdomain-boundary check. This lets any attacker who registers a domain name that merely *ends with* the same string (e.g. `evilethereum.org`, which is not a subdomain of `ethereum.org` at all) be treated as an allowed origin, enabling cross-origin reads of gateway responses from arbitrary attacker-controlled sites — the same bug class as the referenced lollms-webui CORS misconfiguration (CVE-2024-6674), where an over-broad/incorrect origin check exposed data to unauthorized origins.

### Finding Description
The relevant logic is in `isAllowedOrigin`: [1](#0-0) 

For each configured allowed origin containing a wildcard host (`*.host`), the code strips the `*.` prefix and then checks `strings.HasSuffix(originHost, allowedHost)`. This is a naive suffix match with no requirement that the preceding character be a `.` (i.e., no real subdomain boundary check). Consequently, an origin such as `https://evilethereum.org` (a completely distinct, attacker-registrable domain) satisfies `strings.HasSuffix("evilethereum.org", "ethereum.org")` and is incorrectly treated as a subdomain of the allowed `ethereum.org`.

This function is invoked directly from the request handler that serves the Gateway's user-facing (internet-facing) HTTP endpoint: [2](#0-1) 

When `CORSEnabled` is true and the check passes, the server reflects the attacker's `Origin` header back in `Access-Control-Allow-Origin`, allowing the browser to expose the JSON-RPC response body to script running on the attacker's page.

The existing test suite exercises the intended wildcard behavior but does not cover the boundary-less matching flaw (e.g. it tests `https://ethereum.remix.org` failing correctly because it doesn't end with the suffix, but never tests a domain that ends with the suffix without a dot boundary, such as `evilethereum.org`): [3](#0-2) 

The gateway's `CORSAllowedOrigins` is a first-class, documented configuration option reachable from any unprivileged HTTP client that can present an arbitrary `Origin` header: [4](#0-3) 

### Impact Explanation
The gateway user HTTP server is the internet-facing entry point through which unprivileged clients submit JSON-RPC requests that get routed to DON handlers and whose responses can carry job/workflow results and other application data via `gateway.ProcessRequest`: [5](#0-4) 

If any operator relies on wildcard subdomain entries in `CORSAllowedOrigins` (a supported and documented pattern per the test suite), an attacker can register a look-alike domain that satisfies the flawed suffix check and mount a cross-origin page that issues fetch requests to the gateway, reading back responses that should only be visible to the legitimate subdomains of the intended organization. This is a genuine allowlist-bypass in an unprivileged-actor-reachable path, matching the "allowlist bypass" / "cross-user response confusion" impact categories.

### Likelihood Explanation
Exploitability requires: (1) the gateway operator configuring `CORSEnabled = true` with at least one wildcard entry in `CORSAllowedOrigins`, and (2) the attacker registering or controlling a domain that lexically ends with the configured suffix. Both conditions are plausible in production since wildcard subdomain allowlisting is a documented, tested feature intended for legitimate multi-subdomain deployments (e.g., `*.ethereum.org`), and domain registration matching an arbitrary suffix string is trivial and cheap for an attacker to obtain (e.g., registering `evil-ethereum.org` or `notethereum.org`-style domains). No credentials or privileged access are required — only crafting an `Origin` header from a browser context on the attacker's own domain.

### Recommendation
Fix `isAllowedOrigin` in `core/services/gateway/network/httpserver.go` to enforce a proper subdomain boundary when matching wildcard hosts — i.e., require that `originHost` either equals `allowedHost` or ends with `"." + allowedHost`, not just an arbitrary suffix. Add regression tests covering domains that share a suffix string but are not true subdomains (e.g. `evilethereum.org` vs. `*.ethereum.org`). Consider replacing the hand-rolled matcher with a well-tested CORS library or a strict host-parsing approach (parsing to labels and comparing suffix *segments*, not raw substrings).

### Proof of Concept
1. Configure the gateway with:
```toml
CORSEnabled = true
CORSAllowedOrigins = ["https://*.ethereum.org"]
```
2. From a browser page hosted at `https://evilethereum.org` (a domain the attacker legitimately owns/registers, unrelated to `ethereum.org`), issue:
```js
fetch("https://<gateway-host>/user", {
  method: "POST",
  headers: {"Content-Type": "application/jsonrpc"},
  body: JSON.stringify({jsonrpc:"2.0", id:"1", method:"<service>.<method>", params:{}})
}).then(r => r.json()).then(data => console.log(data));
```
3. Because `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true` in `isAllowedOrigin`, the server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, and the browser exposes the JSON-RPC response contents to the attacker's script — confirmed by tracing `handleRequest` → `isAllowedOrigin` at [6](#0-5) .

### Citations

**File:** core/services/gateway/network/httpserver.go (L157-193)
```go
func (s *httpServer) isAllowedOrigin(origin string) bool {
	originScheme, originHost, originPort, err := s.splitURL(origin)
	if err != nil {
		s.lggr.Debug("error parsing origin URL", err)
		return false
	}
	for _, allowed := range s.config.CORSAllowedOrigins {
		// probably better to do this once when server starts and store it in a map
		// this is an easier solution so we don't have to apply more changes to the code
		// just need to be careful when specifying allowed origins in the config file
		allowedScheme, allowedHost, allowedPort, err := s.splitURL(allowed)
		if err != nil {
			s.lggr.Debug("error parsing allowed origin URL", err)
			continue
		}
		// skip if the scheme doesn't match at all
		if originScheme != allowedScheme {
			continue
		}
		// skip if the port doesn't match at all
		if originPort != allowedPort {
			continue
		}
		// check for exact host match (e.g., remix.com)
		if originHost == allowedHost {
			return true
		}
		// check for wildcard host match (e.g., *.remix.com)
		if strings.HasPrefix(allowedHost, "*.") {
			allowedHost = allowedHost[2:]
			if strings.HasSuffix(originHost, allowedHost) {
				return true
			}
		}
	}
	return false
}
```

**File:** core/services/gateway/network/httpserver.go (L195-209)
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
```

**File:** core/services/gateway/network/httpserver_test.go (L152-186)
```go
func TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards(t *testing.T) {
	t.Parallel()
	_, handler, url := startNewServer(t, 100_000, 100_000, true,
		[]string{"https://*.ethereum.org", "https://*.valid.domain.com", "http://*.gov"})

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin := "https://remix.ethereum.org"
	resp, respBytes := sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Equal(t, origin, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Equal(t, "GET, POST, OPTIONS", resp.Header.Get("Access-Control-Allow-Methods"))
	require.Equal(t, "Content-Type", resp.Header.Get("Access-Control-Allow-Headers"))

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin = "https://another.valid.domain.com"
	resp, respBytes = sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Equal(t, origin, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Equal(t, "GET, POST, OPTIONS", resp.Header.Get("Access-Control-Allow-Methods"))
	require.Equal(t, "Content-Type", resp.Header.Get("Access-Control-Allow-Headers"))

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin = "http://example.gov"
	resp, respBytes = sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Equal(t, origin, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Equal(t, "GET, POST, OPTIONS", resp.Header.Get("Access-Control-Allow-Methods"))
	require.Equal(t, "Content-Type", resp.Header.Get("Access-Control-Allow-Headers"))
}
```

**File:** core/scripts/gateway/sample_config.toml (L1-10)
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
CORSAllowedOrigins = []
```

**File:** core/services/gateway/gateway.go (L221-295)
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
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
	}

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

	g.lggr.Debugw("received response from handler", "handler", handlerKey, "response", response, "requestID", jsonRequest.ID)
	promRequest.WithLabelValues(response.ErrorCode.String()).Inc()
	return response.RawResponse, api.ToHTTPErrorCode(response.ErrorCode)
}
```
