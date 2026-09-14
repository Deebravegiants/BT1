## Finding: Missing Cache-Control Header on Gateway HTTP Responses Allows Caching of Authentication-Sensitive Data

### Title
Internet-facing gateway HTTP endpoint omits Cache-Control header, enabling client/proxy caching of authentication-sensitive JSON-RPC responses - (File: core/services/gateway/network/httpserver.go)

### Summary
The chainlink gateway's public-facing HTTP server (`httpServer.handleRequest`) writes JSON-RPC responses to clients without ever setting a `Cache-Control` header, mirroring the report's root cause (a caching-header omission on an auth-adjacent endpoint that leaks sensitive protocol data to intermediate caches). [1](#0-0) 

### Finding Description
`handleRequest` is the sole entry point for all gateway JSON-RPC traffic — it reads the raw request body, forwards it to `ProcessRequest`, and writes the raw response with only a `Content-Type` header set: `w.Header().Set("Content-Type", s.config.ContentTypeHeader); w.WriteHeader(httpStatusCode); w.Write(rawResponse)`. [2](#0-1)  No `Cache-Control`, `Pragma`, or `Vary` header is ever set on this path.

The route is also registered with the plain (pre-1.22 style) pattern `mux.Handle(config.Path, handler)`, which does not restrict the accepted HTTP method — GET requests carrying a JSON-RPC body are processed identically to POST requests. [3](#0-2)  Combined with the absence of any `Cache-Control` directive, a `200 OK` response to a GET-style request is heuristically cacheable per RFC 7234 by any conforming intermediary (browser cache, corporate proxy, CDN) sitting in front of the gateway.

These JSON-RPC responses can carry authorization-sensitive payloads — for example the vault gateway handler returns request digests, authorized owner addresses, and secret identifiers/namespaces as part of `AuthResult` and secrets-list responses. [4](#0-3) [5](#0-4)  There is no per-request `Vary` header (e.g., on `Authorization` or the request body hash) to prevent a shared/naive cache from conflating requests from different callers.

### Impact Explanation
If a caching intermediary between the caller and the gateway (browser cache, corporate proxy, or CDN in front of the gateway's public HTTP listener) applies default heuristic freshness to these unauthenticated-looking 200 responses, a subsequent unrelated caller could receive a stale, previously-cached response containing another user's authorization metadata (owner address, request digest, secret namespace/key identifiers) — a cross-user response confusion analogous to the reported nonce leak.

### Likelihood Explanation
Exploitability depends on an intermediary actually choosing to cache the response (most clients issue JSON-RPC via POST, and most caches do not cache POST by default). However, because the handler and route registration place no explicit restriction on HTTP method and set no `Cache-Control`/`Vary` headers at all, the endpoint relies entirely on client/proxy behavior rather than an explicit protocol guarantee, which is the same weakness class flagged in the original report (relying on implicit non-caching behavior rather than explicit `no-cache`/`no-store` directives).

### Recommendation
Explicitly set `Cache-Control: no-store` (stronger than the report's own remediation of `no-cache`, since these are authenticated/authorization-bearing responses, not just nonces) on every response written in `httpServer.handleRequest`, and add a `Vary: Authorization` header if any caching is ever intentionally introduced. Additionally, consider restricting the route registration to `POST` explicitly (e.g., `mux.Handle("POST "+config.Path, handler)`) to remove ambiguity about GET-cacheability.

### Proof of Concept
1. Deploy the gateway with `CORSEnabled` or a caching reverse proxy in front of `httpServer`.
2. Send a JSON-RPC request as `GET /<path>` with a valid vault `secrets.list` payload and valid auth; observe the 200 response contains `Content-Type` only, no `Cache-Control`.
3. A caching proxy configured with default heuristic freshness (common misconfiguration, matching the report's scenario where "the client implements caching based on the Cache-Control header" or its absence) stores the response keyed only by URL/method, not by the request body or `Authorization` header.
4. A second, unrelated caller hitting the same path/method receives the cached response containing the first caller's authorized owner address and secret identifiers.

### Citations

**File:** core/services/gateway/network/httpserver.go (L107-114)
```go
	mux := http.NewServeMux()
	var handler http.Handler
	handler = http.HandlerFunc(server.handleRequest)
	if config.RequestTimeoutMillis > 0 {
		handler = http.TimeoutHandler(handler, time.Duration(config.RequestTimeoutMillis)*time.Millisecond, "Request timed out")
	}
	mux.Handle(config.Path, handler)
	mux.Handle(HealthCheckPath, http.HandlerFunc(server.handleHealthCheck))
```

**File:** core/services/gateway/network/httpserver.go (L233-245)
```go
	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
	duration := time.Since(startTime)
	s.hMetrics.RecordRequestDuration(r.Context(), httpStatusCode, duration)
	s.hMetrics.RecordRequestCount(r.Context(), httpStatusCode)

	w.Header().Set("Content-Type", s.config.ContentTypeHeader)
	w.WriteHeader(httpStatusCode)
	_, err = w.Write(rawResponse) //nolint:gosec // G705: response body is written with an explicit Content-Type, not rendered as HTML
	if err != nil {
		s.lggr.Error("error when writing response", err)
	}
}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L278-292)
```go
	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID

	if err := stamp(prefixedRequestID); err != nil {
		p.lggr.Errorw("failed to stamp authorized request params", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("failed to stamp authorized request params: %w", err)
	}

	p.lggr.Debugw("authorized gateway vault request", "method", req.Method, "requestID", req.ID, "owner", authorizedOwner, "orgID", authResult.OrgID(), "workflowOwner", authResult.WorkflowOwner())
	return &AuthorizedGatewayVaultRequest{
		Req:        *req,
		AuthResult: authResult,
	}, nil
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L70-77)
```go
	digestKey := string(allowlistedRequest.RequestDigest[:])
	r.lggr.Debugw("AllowListBasedAuth authorization succeeded", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", digestKey, "owner", allowlistedRequest.Owner.Hex(), "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
	return &AuthResult{
		workflowOwner: allowlistedRequest.Owner.Hex(),
		digest:        digestKey,
		expiresAt:     int64(allowlistedRequest.ExpiryTimestamp),
	}, nil
}
```
