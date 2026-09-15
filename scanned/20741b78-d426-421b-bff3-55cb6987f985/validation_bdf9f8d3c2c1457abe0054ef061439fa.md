### Title
JSON-RPC Parsing and JWT Verification Occur Before Any Rate Limiting in Gateway HTTP Trigger Path, Enabling Memory/CPU Amplification - (File: core/services/gateway/network/httpserver.go, core/services/gateway/gateway.go, core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The Gateway's user-facing HTTP endpoint reads and fully JSON-decodes every inbound request — and, for HTTP-trigger requests, performs JWT signature verification and workflow-metadata lookups — before any rate limiting is applied. There is no per-IP rate limiting and no global concurrency semaphore gating the HTTP endpoint; the only pre-parsing control is a payload-size limiter. This mirrors the reported "parse-before-rate-limit" bug class: an unprivileged client can force the Gateway to repeatedly perform expensive JSON parsing (and cryptographic verification) work, with rate limiting only enforced deep in the request pipeline, well after the costly operations have already run.

### Finding Description
`httpServer.handleRequest` reads the full request body (bounded only by `MaxRequestBytesLimiter`, a size limit, not a rate or concurrency limit) and immediately forwards it to the handler with no IP-based throttling or global concurrency gate: [1](#0-0) 

`gateway.ProcessRequest` then unconditionally double-parses the JSON payload (`jsonrpc2.DecodeRequest` followed by `codec.DecodeJSONRequest`) before any method dispatch or rate-limit check occurs: [2](#0-1) 

For the HTTP Trigger path (the primary externally-reachable workflow-execution entry point), `HandleUserTriggerRequest` performs, in order: JSON body parsing (`validatedTriggerRequest` → `parseTriggerRequest`), workflow ID resolution, and JWT authentication (`authorizeRequest`, which performs ECDSA signature verification) — and only afterward calls `checkRateLimit`: [3](#0-2) 

`checkRateLimit` is scoped strictly per-workflow-owner and only reachable after a workflow has already been successfully resolved and authenticated: [4](#0-3) 

There is no per-IP limiter anywhere in the gateway package (`RemoteIP`/`ClientIP`/`X-Forwarded-For` are absent from `core/services/gateway/**` except in an mTLS test), and no global concurrency semaphore gating the HTTP endpoint itself — only a payload-size limiter (`GatewayIncomingPayloadSizeLimit`) exists at that layer: [5](#0-4) 

As a result, an unauthenticated/unprivileged remote caller can send a high volume of near-max-size requests, each of which forces the Gateway to: (1) allocate/parse JSON twice, (2) allocate/parse the trigger-specific payload again, and (3) perform ECDSA JWT verification — all prior to any throttling decision, since rate limiting is applied only after these steps succeed and a valid workflow/owner is resolved. Requests targeting nonexistent workflows or invalid JWTs never reach `checkRateLimit` at all, so they cost full parsing/crypto effort with zero rate-limit accounting.

### Impact Explanation
This is directly analogous to the reported bug class: JSON parsing (memory amplification) and, worse, asymmetric cryptographic verification (JWT/ECDSA, which is CPU-expensive) happen unconditionally before rate limiting on the internet-facing Gateway. Absent per-IP or pre-parse throttling, a modest number of concurrent malicious clients can drive outsized memory allocation and CPU consumption on the Gateway relative to the bytes sent, degrading availability for legitimate workflow triggers served by the same Gateway instance.

### Likelihood Explanation
The HTTP Trigger endpoint is explicitly designed to be reachable by external/unprivileged callers (it authenticates via JWT rather than pre-established session), and no code path gates parsing or authentication behind a rate limiter or per-source-IP control. This makes the vulnerable code path trivially reachable without any special privileges.

### Recommendation
1. Apply IP-based or global concurrency rate limiting at the `httpServer.handleRequest` layer, before the body is read/parsed, similar in spirit to the existing size limiter.
2. Move or add a cheap pre-check rate limit ahead of JSON parsing and JWT verification in `HandleUserTriggerRequest`/`gateway.ProcessRequest`, rather than gating only on a fully-resolved, authenticated workflow owner.
3. Consider a global semaphore limiting concurrent in-flight parsing/verification operations on the Gateway's user-facing port, independent of workflow resolution outcome.

### Proof of Concept
An unprivileged client can repeatedly POST near-max-size (bounded by `GatewayIncomingPayloadSizeLimit`) JSON-RPC bodies with `method: workflows.execute` to the Gateway's HTTP trigger endpoint, using either invalid JWTs or workflow selectors that fail resolution. Each request forces double JSON parsing (`gateway.ProcessRequest`) plus trigger-payload parsing and (when a syntactically valid but unauthorized JWT is supplied) full ECDSA verification (`authorizeRequest`) before any rate-limit check is reached, since `checkRateLimit` is only invoked after workflow resolution and authorization succeed. Issuing many such requests concurrently from a small number of source IPs (no per-IP limiting exists) amplifies memory/CPU cost with no throttling control until deep in the pipeline.

### Citations

**File:** core/services/gateway/network/httpserver.go (L57-64)
```go
func (c *HTTPServerConfig) ensureLimiters(lf limits.Factory) (err error) {
	if c.MaxRequestBytesLimiter == nil {
		limit := cresettings.Default.GatewayIncomingPayloadSizeLimit
		limit.DefaultValue = config.Size(c.MaxRequestBytes)
		c.MaxRequestBytesLimiter, err = limits.MakeUpperBoundLimiter(lf, limit)
	}
	return err
}
```

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L392-417)
```go
func (h *httpTriggerHandler) checkRateLimit(ctx context.Context, workflowID, requestID string, callback handlers.Callback) error {
	workflowRef, found := h.workflowMetadataHandler.GetWorkflowReference(workflowID)
	if !found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "workflow reference not found", callback)
		return errors.New("workflow reference not found")
	}

	orgID := h.resolveOrgID(ctx, workflowRef.workflowOwner)
	ctx = contexts.WithCRE(ctx, contexts.CRE{Owner: workflowRef.workflowOwner, Org: orgID, Workflow: workflowID})
	if err := h.userRateLimiter.AllowErr(ctx); err != nil {
		lggr := logger.With(h.lggr, platform.KeyWorkflowID, workflowID, platform.KeyWorkflowOwner, workflowRef.workflowOwner, "requestID", requestID, "err", err)
		if errLimited, ok := errors.AsType[limits.ErrorRateLimited](err); ok {
			switch errLimited.Scope {
			case settings.ScopeWorkflow:
				lggr.Errorf("failed to start execution: per workflow rate limit exceeded")
				h.metrics.IncrementWorkflowThrottled(ctx, h.lggr)
			default:
				lggr.Errorf("failed to start execution: unexpected rate limit for scope %s", errLimited.Scope)
			}
			h.handleUserError(ctx, requestID, jsonrpc.ErrLimitExceeded, "rate limit exceeded", callback)
			return err
		}
		return fmt.Errorf("failed to check rate limit: %w", err)
	}
	return nil
}
```
