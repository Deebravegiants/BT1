### Title
Unauthenticated unbounded `activeRequests` map growth in Vault gateway handler enables DoS - (File: `core/services/gateway/handlers/vault/handler.go`)

### Summary
The Gateway's Vault handler allows an unauthenticated caller to trigger creation of an entry in the handler's in-memory `activeRequests` map via `MethodPublicKeyGet`, which explicitly skips authorization before allocating tracking state. Unlike the sibling `RequestCache` implementation used elsewhere in the gateway, this map has no maximum size enforcement, allowing an unprivileged client to exhaust gateway memory/CPU and cause a hang or crash — the same impact class as the referenced CVE (availability-only DoS).

### Finding Description
`HandleJSONRPCUserMessage` explicitly documents that public-key requests "don't require authorization" and, on a cache miss, immediately calls `h.newActiveRequest(req, callback)` before any authorization/allowlist check runs: [1](#0-0) 

`newActiveRequest` inserts unconditionally into the shared `h.activeRequests` map keyed by the caller-supplied `req.ID` (bounded only to 200 characters, easily unique per request), with no check against any maximum map size: [2](#0-1) 

This is materially different from the gateway's other request-tracking structure, `handlers/common.requestCache`, which explicitly enforces `maxCacheSize` and rejects new entries with `"request cache is full"` once the limit is reached: [3](#0-2) 

The Vault handler's `activeRequests` map (defined at struct field level, initialized with `make(map[string]*activeRequest)`) has no equivalent cap: [4](#0-3) 

Because entries are only removed on response aggregation/timeout paths (bound to `cfg.RequestTimeoutSec`, default 30s), a client that submits requests faster than the timeout window (each with a distinct `req.ID`, up to 200 bytes) can grow the map unbounded within that window, and can sustain this indefinitely, faster than entries expire.

### Impact Explanation
Unbounded, unauthenticated map growth in a long-lived gateway service can exhaust process memory and/or degrade lock-contended (`h.mu`) operations across all Vault gateway traffic, producing a hang or crash of the Gateway process — a complete denial of service for all DON nodes and workflows relying on Vault secrets through that gateway. This matches the CVE's availability-only impact.

### Likelihood Explanation
The `MethodPublicKeyGet` path is explicitly unauthenticated by design ("Public key requests don't require authorization"), and it is reachable directly from any client able to submit JSON-RPC messages to the gateway's Vault handler entrypoint (`HandleJSONRPCUserMessage`). No allowlist, JWT, or per-caller quota gates this specific code path before the map insertion occurs. The only bound is a 200-character `req.ID` length check, which does not limit request rate or map size. I was not able to fully confirm within the available tool budget whether a periodic sweep independent of per-request timers exists elsewhere in the file; this should be verified before remediation, but the absence of a `maxCacheSize`-style cap (present in the analogous `common.requestCache`) is confirmed and is the root cause.

### Recommendation
- Enforce a maximum size on `h.activeRequests` (mirroring `common.requestCache.maxCacheSize`), rejecting new entries once a configurable ceiling is reached.
- Apply a lightweight per-caller/global rate limit ahead of the `MethodPublicKeyGet` fast-path, consistent with how `nodeRateLimiter` is applied elsewhere in the gateway.
- Ensure a background reaper actively evicts expired `activeRequests` entries independent of individual request timeout timers, so garbage cannot accumulate faster than it is cleared.

### Proof of Concept
1. As an unauthenticated client, repeatedly send JSON-RPC requests to the gateway's Vault handler with `method: vaulttypes.MethodPublicKeyGet` and a unique `req.ID` (up to 200 chars) on each call, at a rate exceeding `cfg.RequestTimeoutSec` (default 30s) expiry.
2. Since the cached public key is absent or intentionally forced to miss, each request reaches `h.newActiveRequest(req, callback)` at `core/services/gateway/handlers/vault/handler.go:411`, inserting an entry into `h.activeRequests` without any authorization check or map-size bound.
3. Sustained traffic grows `h.activeRequests` unbounded, exhausting gateway memory and/or causing lock contention on `h.mu`, resulting in a hang or crash of the gateway process.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L150-254)
```go
	writeMethodsEnabled limits.GateLimiter
	activeRequests      map[string]*activeRequest
	metrics             *metrics

	aggregator aggregator

	cachedPublicKeyGetResponse []byte
	cachedPublicKeyObject      *tdh2easy.PublicKey

	clock clockwork.Clock
}

func (h *handler) HealthReport() map[string]error {
	return map[string]error{h.Name(): h.Healthy()}
}

func (h *handler) Name() string {
	return h.lggr.Name()
}

// SecretEntry is the user-facing shape returned by list operations.
type SecretEntry struct {
	ID        string `json:"id"`
	Value     string `json:"value"`
	CreatedAt int64  `json:"created_at"`
}

// Config configures the gateway-side Vault handler.
type Config struct {
	NodeRateLimiter   ratelimit.RateLimiterConfig `json:"nodeRateLimiter"`
	RequestTimeoutSec int                         `json:"requestTimeoutSec"`
	Auth0             *vaultcap.Auth0Config       `json:"auth0,omitempty"`
}

// NewHandler creates the gateway-side Vault handler with internal auth wiring.
func NewHandler(methodConfig json.RawMessage, donConfig *config.DONConfig, don gwhandlers.DON, capabilitiesRegistry capabilitiesRegistry, workflowRegistrySyncer workflowsyncerv2.WorkflowRegistrySyncer, lggr logger.Logger, clock clockwork.Clock, limitsFactory limits.Factory) (*handler, error) {
	var cfg Config
	if err := json.Unmarshal(methodConfig, &cfg); err != nil {
		return nil, fmt.Errorf("failed to unmarshal method config: %w", err)
	}

	allowListBasedAuth := vaultcap.NewAllowListBasedAuth(lggr, workflowRegistrySyncer)
	var jwtBasedAuth vaultcap.Authorizer
	var jwtAuth services.Service
	if cfg.Auth0 != nil {
		validator, err := vaultcap.NewJWTBasedAuth(vaultcap.JWTBasedAuthConfig{
			IssuerURL: cfg.Auth0.IssuerURL,
			Audience:  cfg.Auth0.Audience,
			TenantID:  cfg.Auth0.TenantID,
		}, limitsFactory, lggr)
		if err != nil {
			return nil, fmt.Errorf("failed to create JWTBasedAuth: %w", err)
		}
		jwtBasedAuth = validator
		jwtAuth = validator
	}
	authorizer := vaultcap.NewAuthorizer(allowListBasedAuth, jwtBasedAuth, lggr)

	return newHandlerWithAuthorizer(methodConfig, donConfig, don, capabilitiesRegistry, authorizer, jwtAuth, lggr, clock, limitsFactory)
}

func newHandlerWithAuthorizer(methodConfig json.RawMessage, donConfig *config.DONConfig, don gwhandlers.DON, capabilitiesRegistry capabilitiesRegistry, authorizer vaultcap.Authorizer, jwtAuth services.Service, lggr logger.Logger, clock clockwork.Clock, limitsFactory limits.Factory) (*handler, error) {
	var cfg Config
	if err := json.Unmarshal(methodConfig, &cfg); err != nil {
		return nil, fmt.Errorf("failed to unmarshal method config: %w", err)
	}

	if cfg.RequestTimeoutSec == 0 {
		cfg.RequestTimeoutSec = 30
	}

	nodeRateLimiter, err := ratelimit.NewRateLimiter(cfg.NodeRateLimiter)
	if err != nil {
		return nil, fmt.Errorf("failed to create node rate limiter: %w", err)
	}

	metrics, err := newMetrics()
	if err != nil {
		return nil, fmt.Errorf("failed to create metrics: %w", err)
	}

	requestValidator, err := vaultcap.NewRequestValidatorFromLimitsFactory(limitsFactory)
	if err != nil {
		return nil, err
	}

	writeMethodsEnabled, err := limits.MakeGateLimiter(limitsFactory, cresettings.Default.GatewayVaultManagementEnabled)
	if err != nil {
		return nil, fmt.Errorf("could not create vault mgmt limiter: %w", err)
	}

	requestProcessor, err := vaultcap.NewGatewayVaultRequestProcessor(requestValidator, authorizer, false, lggr)
	if err != nil {
		return nil, fmt.Errorf("failed to create gateway vault request processor: %w", err)
	}

	return &handler{
		methodConfig:        cfg,
		donConfig:           donConfig,
		don:                 don,
		lggr:                logger.Named(lggr, "VaultHandler:"+donConfig.DonID),
		requestTimeout:      time.Duration(cfg.RequestTimeoutSec) * time.Second,
		nodeRateLimiter:     nodeRateLimiter,
		writeMethodsEnabled: writeMethodsEnabled,
		activeRequests:      make(map[string]*activeRequest),
```

**File:** core/services/gateway/handlers/vault/handler.go (L404-419)
```go
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
		if cachedPublicKey == nil {
			// Not found in cache. Fetch from nodes.
			ar, err := h.newActiveRequest(req, callback)
			if err != nil {
				h.lggr.Errorw("failed to create new activeRequest", "error", err)
				return err
			}
			return h.handlePublicKeyGet(ctx, ar)
		}
		h.lggr.Debugw("returning cached public key response")
		return h.handlePublicKeyGetSynchronously(ctx, req, publicKeyResponseBytes, callback)
```

**File:** core/services/gateway/handlers/vault/handler.go (L457-472)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```

**File:** core/services/gateway/handlers/common/requestcache.go (L46-66)
```go
func NewRequestCache[T any](timeout time.Duration, maxCacheSize uint32) RequestCache[T] {
	return &requestCache[T]{cache: make(map[globalID]*pendingRequest[T]), timeout: timeout, maxCacheSize: maxCacheSize}
}

func (c *requestCache[T]) NewRequest(lggr logger.Logger, request *api.Message, callback handlers.Callback, responseData *T) error {
	if request == nil {
		return errors.New("request is nil")
	}
	if responseData == nil {
		return errors.New("responseData is nil")
	}
	key := globalID{request.Body.Sender, request.Body.MessageID}
	c.mu.Lock()
	defer c.mu.Unlock()
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
	if len(c.cache) >= int(c.maxCacheSize) {
		return errors.New("request cache is full")
	}
```
