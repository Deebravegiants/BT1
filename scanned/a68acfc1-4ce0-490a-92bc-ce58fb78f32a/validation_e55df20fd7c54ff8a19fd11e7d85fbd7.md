### Title
Unbounded, linearly-scanned `allowListedRequests` slice in Vault's `AllowListBasedAuth` enables workflow-owner-triggered DoS of request authorization - (File: `core/capabilities/vault/allow_list_based_auth.go`)

### Summary
The Vault gateway's request authorization path (`allowListBasedAuth.AuthorizeRequest`) authorizes every incoming Vault JSON-RPC request by linearly scanning an in-memory slice of allowlisted requests (`fetchAllowlistedItem`) that is populated from the on-chain `WorkflowRegistry` contract's allowlist. That slice grows unbounded because any linked (but otherwise unprivileged, non-admin) workflow owner can permissionlessly call `AllowlistRequest` on the `WorkflowRegistry` contract with an arbitrarily distant expiry timestamp, and entries are only pruned once expired. As the on-chain/in-memory list grows, every single authorization call becomes progressively more expensive (O(n) scan, repeated up to `retryCount+1` times with debug-string building), degrading or ultimately affecting the ability of the Vault DON to authorize requests for *all* users - the same array-based DoS class described in the external report (unbounded array growth causing DOS when traversed on every operation).

### Finding Description
`workflowRegistry.syncAllowlistedRequests` (`core/services/workflows/syncer/v2/workflow_registry.go:766-806`) periodically fetches allowlisted requests from the chain and merges them into `w.allowListedRequests`, pruning only entries whose `ExpiryTimestamp` has passed: [1](#0-0) 

This full slice is exposed via `GetAllowlistedRequests`: [2](#0-1) 

Every Vault request authorized through the `allowListBasedAuth` path fetches this slice and performs a linear scan (`fetchAllowlistedItem`), repeating up to `retryCount+1` (11) times if the digest isn't yet found, sleeping `retryInterval` (3s) between attempts, and building a full debug-string representation of the entire list on each attempt: [3](#0-2) 

Any linked workflow owner (an unprivileged, non-admin actor from the protocol's perspective) can grow this list arbitrarily by repeatedly calling `AllowlistRequest` on the `WorkflowRegistry` contract with a far-future `ExpiryTimestamp`: [4](#0-3) [5](#0-4) 

There is no cap on `ExpiryTimestamp` (`VerifyPreconditions` only rejects a zero value), and no bound on the total number of active allowlisted requests that can accumulate before expiry pruning removes them: [6](#0-5) 

This `allowListBasedAuth` mechanism is wired into the Vault gateway's node-side request handler (`GatewayHandler`) that processes all incoming requests forwarded from the gateway on behalf of all Vault clients: [7](#0-6) 

### Impact Explanation
Because every incoming Vault request (from any user/workflow owner) must pass through `AllowListBasedAuth.AuthorizeRequest`, and that function scans the entire allowlisted-requests slice (potentially multiple times per request due to retries), an unprivileged workflow owner who repeatedly calls the permissionless `AllowlistRequest` contract method with distant expiries can grow this slice without bound. This degrades the authorization latency (and CPU/memory cost of building debug log strings) for *every* subsequent Vault request across the entire DON, not just the attacker's own requests - a classic array-based DoS affecting availability of the Vault authorization/gateway pipeline for all tenants.

### Likelihood Explanation
Likelihood is moderate: the action (`AllowlistRequest`) is reachable by any user who has linked their workflow owner address (a normal, permissionless onboarding step, not an admin-only action), requires only gas cost per call, and has no explicit cap on the number of entries or how far in the future `ExpiryTimestamp` can be set, so an attacker can grow the list cheaply and let entries live for a long time before pruning.

### Recommendation
- Enforce a maximum on `ExpiryTimestamp` (e.g., cap window relative to `now`) and/or a maximum number of active allowlisted entries per owner and globally, rejecting new `AllowlistRequest` calls once the cap is reached.
- Replace the linear array scan in `fetchAllowlistedItem`/`allowListedRequests` with a map keyed by `RequestDigest` for O(1) lookup, avoiding O(n) growth in authorization latency.
- Avoid unconditionally building the full `allowedRequestsStrs` debug representation of the list on every authorization attempt; only build/log it when actually needed (e.g., guarded by log-level check).

### Proof of Concept
1. Link a workflow owner via `LinkOwner` (permissionless onboarding).
2. Repeatedly call `WorkflowRegistry.AllowlistRequest(requestDigest, expiryTimestamp)` with `expiryTimestamp` set far in the future (e.g., years out), for many distinct digests, to grow `totalAllowlistedRequests` (see test helper at `core/services/workflows/syncer/v2/workflow_syncer_v2_test.go:875-911` and `allowlistRequestParams`).
3. Observe that `workflowRegistry.syncAllowlistedRequests` merges all these entries into `w.allowListedRequests` (`core/services/workflows/syncer/v2/workflow_registry.go:780-795`), and the slice never shrinks because entries haven't expired.
4. Send normal Vault requests through the gateway; each call to `AuthorizeRequest`/`findAllowlistedItemWithRetry` (`core/capabilities/vault/allow_list_based_auth.go:79-111`) must scan the now-large slice up to 11 times, with debug-string construction of the entire list each time, increasing authorization latency and resource usage for all Vault DON traffic as the list grows.

### Citations

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L780-795)
```go
			w.allowListedMu.Lock()
			// Prune expired requests
			activeAllowlistedRequests := []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest{}
			expiredRequestsCount := 0
			for _, request := range w.allowListedRequests {
				if int64(request.ExpiryTimestamp) > time.Now().Unix() {
					activeAllowlistedRequests = append(activeAllowlistedRequests, request)
				} else {
					expiredRequestsCount++
				}
			}

			// Add new requests
			activeAllowlistedRequests = append(activeAllowlistedRequests, newAllowListedRequests...)
			w.allowListedRequests = activeAllowlistedRequests
			w.lastSeenAllowlistedRequestsCount = totalAllowlistedRequests
```

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L1218-1224)
```go
func (w *workflowRegistry) GetAllowlistedRequests(_ context.Context) []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest {
	w.allowListedMu.RLock()
	defer w.allowListedMu.RUnlock()
	allowListedRequests := make([]workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest, len(w.allowListedRequests))
	copy(allowListedRequests, w.allowListedRequests)
	return allowListedRequests
}
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L79-111)
```go
func (r *allowListBasedAuth) findAllowlistedItemWithRetry(ctx context.Context, req jsonrpc.Request[json.RawMessage], requestDigest string, requestDigestBytes32 [32]byte) (*workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest, []string, error) {
	for attempt := 0; attempt <= r.retryCount; attempt++ {
		allowedRequests := r.workflowRegistrySyncer.GetAllowlistedRequests(ctx)
		allowedRequestsStrs := make([]string, 0, len(allowedRequests))
		for _, rr := range allowedRequests {
			allowedReqStr := fmt.Sprintf("AuthorizedOwner: %s, RequestDigest: %s, ExpiryTimestamp: %d", rr.Owner.Hex(), hex.EncodeToString(rr.RequestDigest[:]), rr.ExpiryTimestamp)
			allowedRequestsStrs = append(allowedRequestsStrs, allowedReqStr)
		}
		r.lggr.Debugw("AllowListBasedAuth loaded allowlisted requests", "method", req.Method, "requestID", req.ID, "attempt", attempt+1, "allowedRequests", allowedRequestsStrs)

		allowlistedRequest := r.fetchAllowlistedItem(allowedRequests, requestDigestBytes32)
		if allowlistedRequest != nil {
			return allowlistedRequest, allowedRequestsStrs, nil
		}
		if attempt == r.retryCount {
			return nil, allowedRequestsStrs, nil
		}

		r.lggr.Debugw("AllowListBasedAuth request digest not yet allowlisted, retrying",
			"method", req.Method,
			"requestID", req.ID,
			"digestHexStr", requestDigest,
			"attempt", attempt+1,
			"maxAttempts", r.retryCount+1,
			"retryInterval", r.retryInterval)
		if err := sleepWithContext(ctx, r.retryInterval); err != nil {
			r.lggr.Debugw("AllowListBasedAuth retry canceled", "method", req.Method, "requestID", req.ID, "error", err)
			return nil, nil, err
		}
	}

	return nil, nil, nil // unreachable: loop always returns
}
```

**File:** deployment/cre/workflow_registry/v2/changeset/operations/contracts/user_workflow_registry_ops.go (L360-387)
```go
var UserAllowlistRequestOp = operations.NewOperation(
	"user-allowlist-request-op",
	semver.MustParse("1.0.0"),
	"User Allowlist Request in WorkflowRegistry V2",
	func(b operations.Bundle, deps WorkflowRegistryOpDeps, input UserAllowlistRequestOpInput) (UserAllowlistRequestOpOutput, error) {
		// Execute the transaction using the strategy
		operation, _, err := deps.Strategy.Apply(func(opts *bind.TransactOpts) (*types.Transaction, error) {
			tx, err := deps.Registry.AllowlistRequest(opts, input.RequestDigest, input.ExpiryTimestamp)
			if err != nil {
				return nil, fmt.Errorf("failed to call AllowlistRequest: %w", err)
			}
			return tx, nil
		})
		if err != nil {
			return UserAllowlistRequestOpOutput{}, fmt.Errorf("failed to execute AllowlistRequest: %w", err)
		}
		if operation != nil {
			deps.Env.Logger.Infof("Created MCMS proposal for AllowlistRequest on chain %d", input.ChainSelector)
		} else {
			deps.Env.Logger.Infof("Successfully user allowlisted request on chain %d", input.ChainSelector)
		}
		return UserAllowlistRequestOpOutput{
			Success:         true,
			MCMSOperation:   operation,
			RegistryAddress: deps.Registry.Address(),
		}, nil
	},
)
```

**File:** deployment/cre/workflow_registry/v2/changeset/user_workflow_registry.go (L716-736)
```go
// UserAllowlistRequest allows a user to request allowlist status
type UserAllowlistRequest struct{}

type UserAllowlistRequestInput struct {
	ExpiryTimestamp uint32 `json:"expiryTimestamp"`
	RequestDigest   string `json:"requestDigest"`

	ChainSelector             uint64                   `json:"chainSelector"`             // Chain Selector
	MCMSConfig                *crecontracts.MCMSConfig `json:"mcmsConfig,omitempty"`      // MCMS configuration
	WorkflowRegistryQualifier string                   `json:"workflowRegistryQualifier"` // Qualifier to identify the specific workflow registry
}

func (u UserAllowlistRequest) VerifyPreconditions(e cldf.Environment, config UserAllowlistRequestInput) error {
	if config.ExpiryTimestamp == 0 {
		return errors.New("expiry timestamp cannot be zero")
	}
	if len(config.RequestDigest) == 0 {
		return errors.New("request digest cannot be empty")
	}
	return nil
}
```

**File:** core/capabilities/vault/gw_handler.go (L84-141)
```go
func NewGatewayHandler(
	secretsService vaulttypes.SecretsService,
	connector gatewayConnector,
	workflowRegistrySyncer workflowsyncerv2.WorkflowRegistrySyncer,
	lggr logger.Logger,
	limitsFactory limits.Factory,
	authorizer Authorizer,
	auth0 *Auth0Config,
) (*GatewayHandler, error) {
	var jwtAuthService services.Service
	var jwtBasedAuth Authorizer
	if auth0 != nil {
		var err error
		jwtAuthService, err = NewJWTBasedAuth(JWTBasedAuthConfig{
			IssuerURL: auth0.IssuerURL,
			Audience:  auth0.Audience,
			TenantID:  auth0.TenantID,
		}, limitsFactory, lggr)
		if err != nil {
			return nil, fmt.Errorf("failed to create JWTBasedAuth: %w", err)
		}
		jwtBasedAuth = jwtAuthService.(Authorizer)
	}

	if authorizer == nil {
		allowListBasedAuth := NewAllowListBasedAuth(lggr, workflowRegistrySyncer)
		authorizer = NewAuthorizer(allowListBasedAuth, jwtBasedAuth, lggr)
	}

	requestValidator, err := NewRequestValidatorFromLimitsFactory(limitsFactory)
	if err != nil {
		return nil, fmt.Errorf("failed to create request validator: %w", err)
	}

	metrics, err := newMetrics()
	if err != nil {
		return nil, fmt.Errorf("failed to create metrics: %w", err)
	}

	requestProcessor, err := NewGatewayVaultRequestProcessor(requestValidator, authorizer, true, lggr)
	if err != nil {
		return nil, fmt.Errorf("failed to create gateway vault request processor: %w", err)
	}

	gh := &GatewayHandler{
		secretsService:   secretsService,
		gatewayConnector: connector,
		requestProcessor: requestProcessor,
		jwtAuthService:   jwtAuthService,
		lggr:             lggr.Named(HandlerName),
		metrics:          metrics,
	}
	gh.Service, gh.eng = services.Config{
		Name:  "GatewayHandler",
		Start: gh.start,
		Close: gh.close,
	}.NewServiceEngine(lggr)
	return gh, nil
```
