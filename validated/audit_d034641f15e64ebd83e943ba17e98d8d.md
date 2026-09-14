## Finding

### Title
Gateway HTTP Action leaks detailed SSRF-block reasons (scheme/port/IP) to the requesting workflow - ([File: core/services/gateway/network/httpclient.go])

### Summary
The gateway's outbound HTTP action capability returns differentiated, detailed error strings when a workflow-controlled URL is blocked by the SSRF allowlist (distinguishing blocked scheme, blocked port, and blocked IP), and forwards this raw error text back to the requesting workflow. This lets an unprivileged workflow author use the gateway as an SSRF oracle to probe the internal network topology reachable from the gateway, mirroring the Gitea CVE-2021-45325 pattern of leaking internal-network detail through differentiated error responses.

### Finding Description
`httpClient.Send` in [1](#0-0)  classifies outbound request failures using `isBlockedRequest`, which distinguishes safeurl-typed errors for blocked scheme, blocked port, blocked/invalid IP, and disabled redirects [2](#0-1) . When blocked, it wraps `ErrBlockedRequest` together with a `truncateLogError`-sanitized `*url.Error` that still preserves the scheme, host, and the specific safeurl reason (e.g. `"port: 8080 not found in allowlist"`, `"ip: 169.254.0.1 not found in allowlist"`, `"scheme: file not found in allowlist"` as exercised in [3](#0-2) ).

This detailed error is then propagated verbatim into the capability response: `createHTTPRequestCallback` sets `ErrorMessage: err.Error()` on `OutboundHTTPResponse` for every failure case, including blocked requests [4](#0-3) . This response is sent back to the requesting DON node via `sendResponseToNode` and ultimately becomes the result of the workflow's HTTP action capability call, i.e., it is visible to whoever authored/runs the workflow that issued the outbound request in `makeOutgoingRequest` [5](#0-4) .

Because the three block categories (scheme/port/IP-not-in-allowlist) and the two live-network categories (`ErrHTTPSend`/`ErrHTTPRead`, meaning the address was reachable and attempted) produce distinguishable text, a workflow author who fully controls the outbound `URL` can iterate over internal hostnames/IPs and ports and use the returned error text as an oracle to determine: (a) which addresses are blocked by policy vs. (b) which addresses were actually dialed (network error/timeout) — revealing which internal hosts/ports exist and are reachable from the gateway's network, without needing any other access to that network.

### Impact Explanation
This is an information-disclosure / SSRF-oracle issue: a low-privilege workflow author (someone who can only submit an HTTP-action-capability workflow through the gateway, not a node operator) can enumerate the gateway's internal network topology (reachable internal hosts/ports, firewall/allowlist boundaries) by observing differentiated block/error messages returned in the capability response. This is directly analogous to the Gitea SSRF advisory, where differentiated OpenID-URL error text leaked internal network details through the UI to an unauthenticated user.

### Likelihood Explanation
Any workflow that can invoke the gateway's HTTP action capability with an attacker-controlled `URL` field can trigger this at will; the classification logic runs on every request and the resulting message is always echoed back in `ErrorMessage`, so exploitation requires no special privilege beyond normal workflow submission.

### Recommendation
Return a generic, non-differentiating error (e.g., a single "request blocked or failed" message, similar to the `internalErrorMessage` constant already used elsewhere in this package) to the workflow for all blocked/failed outbound requests, while preserving the detailed `truncateLogError` output only in server-side logs/metrics (as is already done via `l.Warnw`/`l.Errorw`). Avoid exposing the underlying safeurl reason (scheme/port/IP) and host in the response payload delivered to workflow authors.

### Proof of Concept
1. Author a workflow that invokes the gateway's HTTP action capability, setting `OutboundHTTPRequest.URL` to a series of internal candidate targets, e.g. `http://169.254.169.254`, `http://10.0.0.5:22`, `http://10.0.0.5:9999`, `file:///etc/passwd`.
2. Observe the `OutboundHTTPResponse.ErrorMessage` returned for each:
   - `"blocked request: ip: 169.254.169.254 not found in allowlist"` → address blocked by policy (host may or may not exist).
   - `"blocked request: port: 9999 not found in allowlist"` → different reason, confirms scheme/host accepted but port not allowed.
   - A generic `ErrHTTPSend`/timeout-style message → address was actually dialed (network reachable, no allowlist block), indicating the host exists and is live inside the gateway's network.
3. By diffing these categories across many candidate internal addresses/ports, an attacker builds a map of the gateway's reachable internal infrastructure without ever needing direct network access — the same class of leak described in GHSA-8h8p-x289-vvqr.

### Citations

**File:** core/services/gateway/network/httpclient.go (L376-399)
```go
// isBlockedRequest checks if an error is caused by blocked/invalid input (e.g., blocked IP, invalid scheme, blocked headers)
// It checks for safeurl typed errors.
func isBlockedRequest(err error) bool {
	if err == nil {
		return false
	}

	// Check safeurl typed errors - use errors.As for type checking
	var (
		ipv6Err              *safeurl.IPv6BlockedError
		portErr              *safeurl.AllowedPortError
		schemeErr            *safeurl.AllowedSchemeError
		invalidHostErr       *safeurl.InvalidHostError
		ipErr                *safeurl.AllowedIPError
		redirectsDisabledErr *redirectsDisabledError
	)

	return errors.As(err, &ipv6Err) ||
		errors.As(err, &portErr) ||
		errors.As(err, &schemeErr) ||
		errors.As(err, &invalidHostErr) ||
		errors.As(err, &ipErr) ||
		errors.As(err, &redirectsDisabledErr)
}
```

**File:** core/services/gateway/network/httpclient.go (L477-487)
```go
	resp, err := c.client.Do(r)
	if err != nil {
		truncatedErr := truncateLogError(err)
		c.metrics.recordTotal(ctx, req.Method, 0, false, traceState.connReused.Load(), time.Since(requestStart))
		if isBlockedRequest(err) {
			c.lggr.Warnw("HTTP request blocked", "err", truncatedErr)
			return nil, fmt.Errorf("%w: %w", ErrBlockedRequest, truncatedErr)
		}
		c.lggr.Errorw("failed to send HTTP request", "err", truncatedErr)
		return nil, errors.Join(truncatedErr, ErrHTTPSend)
	}
```

**File:** core/services/gateway/network/httpclient_test.go (L329-361)
```go
	}{
		{
			name:          "blocked port",
			url:           "http://177.0.0.1:8080",
			expectedError: "port: 8080 not found in allowlist",
			blockPort:     true,
		},
		{
			name:          "blocked scheme",
			url:           "file://127.0.0.1",
			expectedError: "scheme: file not found in allowlist",
		},
		{
			name:          "explicitly blocked IP",
			url:           "http://169.254.0.1",
			expectedError: "ip: 169.254.0.1 not found in allowlist",
		},
		{
			name:          "explicitly blocked IP - internal network",
			url:           "http://169.254.0.1",
			expectedError: "ip: 169.254.0.1 not found in allowlist",
		},
		{
			name:          "explicitly blocked IP - loopback",
			url:           "http://127.0.0.1",
			expectedError: "ip: 127.0.0.1 not found in allowlist",
		},
		{
			name:          "explicitly blocked IP - loopback without scheme",
			url:           "127.0.0.1",
			expectedError: "host:  is not valid",
		},
		{
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L346-374)
```go
		resp, err := h.send(ctx, httpReq, req)
		externalEndpointLatency := time.Since(start)
		if err != nil {
			isBlockedRequest := errors.Is(err, network.ErrBlockedRequest)
			isHTTPSendError := errors.Is(err, network.ErrHTTPSend)
			isHTTPReadError := errors.Is(err, network.ErrHTTPRead)
			isExternalEndpointError := isHTTPSendError || isHTTPReadError

			switch {
			case isBlockedRequest:
				l.Warnw("HTTP request blocked", "requestID", requestID, "err", err)
				h.metrics.IncrementBlockedRequestCount(ctx, h.lggr)
			case isHTTPSendError:
				l.Warnw("error while sending HTTP request to external endpoint", "requestID", requestID, "err", err)
				h.metrics.IncrementHTTPSendErrorCount(ctx, h.lggr)
			case isHTTPReadError:
				l.Warnw("error while reading HTTP response from external endpoint", "requestID", requestID, "err", err)
				h.metrics.IncrementHTTPReadErrorCount(ctx, h.lggr)
			default:
				l.Errorw("error while sending HTTP request", "requestID", requestID, "err", err)
			}

			return gateway_common.OutboundHTTPResponse{
				ErrorMessage:            err.Error(),
				IsExternalEndpointError: isExternalEndpointError, // error while sending request to or reading response from external endpoint
				IsValidationError:       isBlockedRequest,        // validation error before sending request to external endpoint
				ExternalEndpointLatency: externalEndpointLatency,
			}
		}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L404-454)
```go
func (h *gatewayHandler) makeOutgoingRequest(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	requestID := resp.ID
	h.lggr.Debugw("handling outgoing message", "requestID", requestID, "nodeAddr", nodeAddr)
	var req gateway_common.OutboundHTTPRequest
	err := json.Unmarshal(*resp.Result, &req)
	if err != nil {
		return fmt.Errorf("failed to unmarshal HTTP request from node %s: %w", nodeAddr, err)
	}
	timeout := time.Duration(req.TimeoutMs) * time.Millisecond
	httpReq := network.HTTPRequest{
		Method:           req.Method,
		URL:              req.URL,
		Headers:          req.Headers, //nolint:staticcheck // forward deprecated Headers for backward compatibility; request uses MultiHeaders when set
		MultiHeaders:     req.MultiHeaders,
		Body:             req.Body,
		MaxResponseBytes: req.MaxResponseBytes,
		Timeout:          timeout,
	}

	sendResponseTimeout := time.Duration(defaultSendResponseTimeoutMs) * time.Millisecond

	// send response to node async
	h.wg.Go(func() {
		// not cancelled when parent is cancelled to ensure the goroutine can finish
		baseCtx := context.WithoutCancel(ctx)
		httpCtx, httpCancel := context.WithTimeout(baseCtx, timeout)
		defer httpCancel()
		l := logger.With(h.lggr, "requestID", requestID, "method", req.Method, "timeout", req.TimeoutMs)
		var outboundResp gateway_common.OutboundHTTPResponse
		callback := h.createHTTPRequestCallback(httpCtx, requestID, httpReq, req)
		if req.CacheSettings.MaxAgeMs > 0 {
			h.metrics.IncrementCacheReadCount(ctx, h.lggr)
			outboundResp = h.responseCache.Fetch(httpCtx, req, callback, req.CacheSettings.Store)
		} else {
			outboundResp = callback()
			if req.CacheSettings.Store {
				h.responseCache.Set(req, outboundResp)
			}
		}
		h.metrics.IncrementActionCapabilityRequestCount(ctx, nodeAddr, h.lggr)
		// Use a separate context for sending the response to the node so that an
		// expired HTTP request timeout does not prevent delivering the result.
		sendCtx, sendCancel := context.WithTimeout(baseCtx, sendResponseTimeout)
		defer sendCancel()
		err := h.sendResponseToNode(sendCtx, requestID, outboundResp, nodeAddr)
		if err != nil {
			l.Errorw("error sending response to node", "err", err, "nodeAddr", nodeAddr, "requestID", requestID)
			h.metrics.IncrementActionCapabilityFailures(ctx, nodeAddr, h.lggr)
		}
	})
	return nil
```
