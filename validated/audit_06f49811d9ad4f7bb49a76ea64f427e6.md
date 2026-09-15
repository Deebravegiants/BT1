### Title
Unbounded resource creation from unauthenticated user requests in the confidential relay gateway handler - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

### Summary
`HandleJSONRPCUserMessage` in `core/services/gateway/handlers/confidentialrelay/handler.go` accepts any incoming JSON-RPC user message from the internet-facing gateway HTTP endpoint and, without any authentication/authorization check or per-caller rate limiting, allocates a persistent `activeRequest` entry and immediately fans the message out to every node in the DON.

### Finding Description
Incoming public HTTP requests reach `gateway.ProcessRequest` [1](#0-0)  which dispatches to `handler.HandleJSONRPCUserMessage` for the resolved handler. For the confidential relay handler, this method performs only an empty-ID check and a 200-character length check before creating global state and forwarding the request to the DON: [2](#0-1) 

`newActiveRequest` inserts an entry into the handler-wide `h.activeRequests` map keyed only by the caller-supplied request ID, with no cap on the total number of concurrently tracked requests and no authentication of the caller: [3](#0-2) 

`fanOutToNodes` then synchronously sends the raw, unauthenticated request to every DON member over the node websocket connection: [4](#0-3) 

Unlike the sibling `vault` handler, which runs `h.requestProcessor.ProcessRequest` (authorization) before calling `newActiveRequest` [5](#0-4) , the confidential relay handler has no equivalent authorization step at all before state allocation and network fan-out. The comment on the vault processor even documents this exact class of risk — deferring limiter/tenant creation until after auth specifically "to let unauthenticated callers create unbounded limiter tenants" — confirming the team is aware of, and has fixed, this pattern elsewhere but not here: [6](#0-5) 

Rate limiting in this handler exists only on the node→gateway response path (`perNodeRateLimiters`, `globalNodeRateLimiter` in `HandleNodeMessage`), not on the unprivileged user→gateway request path: [7](#0-6) . The underlying HTTP transport (`core/services/gateway/network/httpserver.go`) enforces only a max body-size limiter, not a per-caller or global request-rate limit, before invoking `ProcessRequest`.

This mirrors CVE-2019-10079's bug class: an unauthenticated remote party can send a flood of distinct "frames" (here, distinct JSON-RPC request IDs) that each cause the server to allocate and retain state (map entries, goroutines via `errgroup`, background sweep tracking) with no rate limit gating that allocation.

### Impact Explanation
An unauthenticated client can repeatedly POST JSON-RPC requests with unique IDs (bounded only by the 200-char ID length and the HTTP body-size limiter) to exhaust gateway memory via the growing `activeRequests` map, and simultaneously flood every node in the target DON with forwarded relay requests via `fanOutToNodes`/`don.SendToNode`, since each call spawns concurrent sends per node. This is a resource-exhaustion / availability risk affecting the gateway process and the connected DON, reachable by any unprivileged internet client that can reach the public gateway HTTP endpoint.

### Likelihood Explanation
High for an attacker with network access to the gateway's public HTTP endpoint: no authentication, JWT, or allowlist check gates entry into this method, and no request-rate limiting exists on the ingress path before the expensive map insertion and DON fan-out. Requests only need unique IDs (trivial to generate) and remain valid until `removeExpiredRequests` reaps them after `RequestTimeoutSec` (default 30s), giving an attacker a sustained window to keep the map populated.

### Recommendation
Add authentication/authorization (or at minimum, an unauthenticated per-IP/global rate limiter and a hard cap on `len(h.activeRequests)`) before `newActiveRequest` and `fanOutToNodes` are invoked in `HandleJSONRPCUserMessage`, mirroring the pre-authorization gate already present in the vault handler's `HandleJSONRPCUserMessage` flow.

### Proof of Concept
1. Obtain the public URL of the gateway's user-facing HTTP endpoint serving the confidential relay handler (`MethodSecretsGet` / `MethodCapabilityExec`).
2. Script a loop that POSTs valid-looking JSON-RPC 2.0 requests with `method` set to one of these methods, each with a fresh, unique `id` (up to 200 chars), and arbitrary/garbage `params`.
3. Send these at high volume with no authentication headers.
4. Observe `h.activeRequests` map growth (via metrics/heap profiling) and increased outbound traffic to every DON node member from `fanOutToNodes`, until the gateway's memory or DON node ingress capacity is exhausted, or the requests are cleared after `RequestTimeoutSec`, allowing sustained flooding by continuing the loop.

Note: I could not verify whether an additional authentication layer (e.g., a reverse proxy or `WebServer.RateLimit`-style middleware in front of the gateway's HTTP server, distinct from `core/web/router.go`'s node-operator API) is deployed operationally in front of this specific gateway user endpoint outside of the code paths I inspected; if such a layer exists, it would materially reduce the practical likelihood of this being exploitable in a given deployment.

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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-412)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	labels := h.extractRequestLabels(req)
	l := h.requestLogger(req, labels)
	l.Debugw("handling confidential relay request", "nodes", len(h.donConfig.Members), "f", h.donConfig.F)

	ar, err := h.newActiveRequest(req, labels, callback)
	if err != nil {
		return err
	}

	return h.fanOutToNodes(ctx, l, ar)
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L414-430)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], labels requestLabels, callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID, "executionID", labels.ExecutionID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		labels:    labels,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L438-453)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	l := logger.With(h.lggr, "method", resp.Method, "requestID", resp.ID, "nodeAddr", nodeAddr)
	l.Debugw("handling node response")

	nodeRateLimiter, ok := h.perNodeRateLimiters[nodeAddr]
	if !ok {
		return fmt.Errorf("received message from unexpected node %s", nodeAddr)
	}
	if !nodeRateLimiter.Allow(ctx) {
		l.Debugw("node is rate limited", "nodeAddr", nodeAddr)
		return nil
	}
	if !h.globalNodeRateLimiter.Allow(ctx) {
		l.Debug("global relay rate limit exceeded")
		return nil
	}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L686-708)
```go
func (h *handler) fanOutToNodes(ctx context.Context, l logger.Logger, ar *activeRequest) error {
	var (
		group      errgroup.Group
		nodeErrors atomic.Uint32
	)

	// Each send is bounded independently. A node whose websocket accepts no writes blocks
	// until its context is cancelled, and because the caller only reads the response callback
	// after this function returns, an unbounded send would hold the request open until the
	// client gives up, discarding a bundle that already reached quorum.
	sendCtx, cancel := context.WithTimeout(ctx, h.nodeSendTimeout)
	defer cancel()

	for _, node := range h.donConfig.Members {
		group.Go(func() error {
			err := h.don.SendToNode(sendCtx, node.Address, &ar.req)
			if err != nil {
				nodeErrors.Add(1)
				l.Errorw("error sending request to node", "node", node.Address, "error", err)
			}
			return nil
		})
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L422-441)
```go
	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
	authorizedOwner := authorized.AuthResult.AuthorizedOwner()

	h.lggr.Debugw("handling authorized vault request", "method", req.Method, "requestID", req.ID, "authorizedOwner", authorizedOwner)
	ar, activeRequestErr := h.newActiveRequest(req, callback)
	if activeRequestErr != nil {
		return activeRequestErr
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L30-34)
```go
// before this processor rewrites the request ID or stamps params.
//
// Owner-scoped limit checks are deferred until after authorization: each new owner tenant
// registered by a scoped limiter spawns a persistent background updater, so checking them
// pre-auth would let unauthenticated callers create unbounded limiter tenants.
```
