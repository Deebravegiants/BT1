### Title
CPU-Exhaustion DoS via Unthrottled ECDSA/JWT Authentication on HTTP Trigger Path - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The Gateway's internet-facing HTTP Trigger endpoint performs expensive ECDSA signature recovery to verify the request JWT (`authorizeRequest`) *before* any rate limiting is applied (`checkRateLimit`). An unprivileged remote client can send an unbounded stream of well-formed `workflows.execute` JSON-RPC requests, each forcing a full public-key recovery + JWT/claims verification, with no request-count throttling gating this step. This is the same bug class as CVE-2021-20201 (SPICE TLS renegotiation DoS): an expensive per-request cryptographic operation can be triggered repeatedly by a remote, unauthenticated actor with no cost control ahead of it, causing CPU exhaustion.

### Finding Description
`httpTriggerHandler.HandleUserTriggerRequest` processes every inbound trigger request in this fixed order:
1. `validatedTriggerRequest` (cheap JSON/field validation)
2. `resolveWorkflowID`
3. `authorizeRequest` — verifies the request JWT, which recovers the signer's ECDSA public key and validates the signature/claims (`core/utils/jwt.go`, `VerifyRequestJWT` → `GetSignersEthAddress`)
4. `checkRateLimit` — only now is `userRateLimiter.AllowErr` consulted, and it is scoped per-workflow-owner [1](#0-0) 

The package's own README documents this ordering explicitly: authentication (step 3, ECDSA JWT verification) precedes rate limiting (step 4): [2](#0-1) 

`authorizeRequest` calls `workflowMetadataHandler.Authorize`, which performs the JWT verification per incoming request: [3](#0-2) 

`VerifyRequestJWT` unconditionally performs an ECDSA public-key recovery (`GetSignersEthAddress`) on every call, before any further validation, regardless of whether the signature or workflow ultimately turns out to be valid: [4](#0-3) 

The rate limiter is only reached and only meaningful once a valid `workflowID`/owner context is resolved: [5](#0-4) 

The underlying HTTP transport (`core/services/gateway/network/httpserver.go`) enforces only a body-size limit before dispatching to `ProcessRequest`; no visible global per-connection or per-IP request-rate limiter gates the number of requests that reach the handler chain: [6](#0-5) 

Because the costly cryptographic step happens ahead of any throttling, and the throttling that does exist is keyed on workflow/owner (data the attacker doesn't need to control precisely — any well-formed but forged JWT/workflow selector will still force the recovery step before being rejected), a remote unauthenticated actor can flood the endpoint with unique/garbage JWTs and workflow IDs to force continuous ECDSA recovery work with no compounding penalty.

### Impact Explanation
An unauthenticated, unprivileged network client can drive sustained CPU consumption on the Gateway process by sending a high volume of `workflows.execute` requests with syntactically valid but bogus JWTs/workflow selectors. Each request forces full elliptic-curve signature recovery and JSON claim parsing before rejection, and because rate limiting is applied after this cost is paid, the limiter does not prevent the CPU burn itself — only the downstream side effects. This can degrade Gateway availability/latency for legitimate DON node users, matching the CVSS 5.3 (CPU-consumption-only) impact profile of the reference CVE.

### Likelihood Explanation
Likelihood is high for causing a lesser DoS: the endpoint is explicitly internet-facing and designed to accept requests from arbitrary external users/workflows before any bot/allowlist restriction is applied at that layer; no CAPTCHA, proof-of-work, or pre-auth request-count throttle was found gating the JWT-verification step. Constructing a "well-formed" request with a fabricated JWT/workflow ID requires no special access — it is the normal, expected shape of a legitimate request.

### Recommendation
- Apply a cheap, connection/IP-scoped rate limiter (or a global request-budget limiter) in front of `authorizeRequest`, before any ECDSA recovery is performed, so that unauthenticated request volume itself is bounded independent of workflow/owner identity.
- Consider validating structurally cheap invariants (e.g., digest/format checks) prior to invoking `GetSignersEthAddress`, and/or caching/short-circuiting repeated failures from the same origin.
- Reconsider ordering so `checkRateLimit`-equivalent throttling for "unknown/unauthenticated" traffic happens before the expensive cryptographic authentication step, mirroring the mitigation used for the referenced CVE (limiting renegotiation frequency before the expensive handshake work is redone).

### Proof of Concept
1. Craft an arbitrary `jsonrpc.Request` with method `workflows.execute`, a syntactically valid three-part JWT `req.Auth` signed with any throwaway key, and a `WorkflowSelector` (random/nonexistent workflow ID is fine since request validation of the selector happens after basic field checks but the auth/JWT recovery step is still invoked for any resolvable-looking workflow ID/owner pair).
2. POST this repeatedly and concurrently (many goroutines/processes) to the Gateway's public HTTP endpoint that lands in `ProcessRequest` → `HandleJSONRPCUserMessage` → `HandleUserTriggerRequest`.
3. Observe that each request forces `VerifyRequestJWT`'s ECDSA recovery (`GetSignersEthAddress`) prior to being rejected by `authorizeRequest`/`checkRateLimit`, and that CPU usage scales with the raw request rate rather than being bounded by the per-workflow-owner limiter, since that limiter is only reached after the expensive step.

**Caveat / uncertainty:** I was not able to fully inspect `workflow_metadata_handler.go`'s `Authorize` implementation directly (tool budget exhausted) to confirm there is no earlier lightweight rejection path (e.g., an existing-workflow lookup) that could short-circuit before JWT verification in all cases; the ordering evidence comes from `authorizeRequest`'s call into `Authorize` and the README's documented process flow. It's also possible an upstream reverse proxy or infrastructure-level rate limiter exists outside this repository that would mitigate the raw request volume — that could not be verified from the codebase alone.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-376)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
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

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L77-86)
```markdown
### 4.1 Process Flow

1. **Request Validation**: Validates JSON-RPC format, method, and parameters
2. **Workflow Resolution**: Resolves workflow ID from selector (ID, owner, name, tag)
3. **Authentication**: Verifies JWT token (ECDSA signature) and checks authorized keys
4. **Rate Limiting**: Enforces per-workflow-owner rate limits
5. **Node Distribution**: Sends request to all DON members with retry logic
6. **Response Aggregation**: Collects and aggregates responses from nodes (2f + 1 identical responses required, where f is max faulty nodes)
7. **User Response**: Returns aggregated result to the original requester

```

**File:** core/utils/jwt.go (L246-266)
```go
	signedString, signature, err := splitToken(tokenString)
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	decodedSignature, err := base64.RawURLEncoding.DecodeString(signature)
	if err != nil {
		return nil, gethcommon.Address{}, fmt.Errorf("signature segment is not valid base64url: %w", err)
	}
	pubKey, err := GetSignersEthAddress([]byte(signedString), decodedSignature)
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	verifiedToken, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (any, error) {
		if token.Method.Alg() != EthereumSigningMethod.Alg() {
			return nil, fmt.Errorf("unsupported JWT 'alg': '%s'. Expected '%s'", token.Method.Alg(), EthereumSigningMethod.Alg())
		}
		if _, ok := token.Method.(*SigningMethodEth); !ok {
			return nil, jwt.ErrSignatureInvalid
		}
		return pubKey, nil
	})
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
