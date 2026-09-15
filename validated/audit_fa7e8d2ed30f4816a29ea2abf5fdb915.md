Audit Report

## Title
Unbounded, linearly-scanned `allowListedRequests` slice in Vault's `AllowListBasedAuth` enables workflow-owner-triggered DoS of request authorization - (File: `core/capabilities/vault/allow_list_based_auth.go`)

## Summary
Every Vault JSON-RPC request authorized via `allowListBasedAuth.AuthorizeRequest` triggers `findAllowlistedItemWithRetry`, which loads the full in-memory `allowListedRequests` slice and performs a linear scan (`fetchAllowlistedItem`), repeated up to `retryCount+1` (11) times with a `Sprintf`-based debug string built for every entry on every attempt [1](#0-0) . This slice is populated from the on-chain `WorkflowRegistry` allowlist by `syncAllowlistedRequests`, which only prunes entries once their `ExpiryTimestamp` passes and otherwise appends all newly seen allowlisted requests without any cap [2](#0-1) .

## Finding Description
The full slice is exposed unfiltered via `GetAllowlistedRequests` [3](#0-2) , and `AuthorizeRequest`/`findAllowlistedItemWithRetry` fetch and scan it on every incoming request, with a full O(n) debug-string rebuild (`allowedRequestsStrs`) executed unconditionally on each of the (up to 11) retry attempts, regardless of log level [1](#0-0) . This authorizer is wired directly into the Vault `GatewayHandler`, which processes every request forwarded from the gateway on behalf of all Vault clients [4](#0-3) .

The deployment-side changeset for `AllowlistRequest` only validates that `ExpiryTimestamp` is non-zero, with no upper bound enforced on how far in the future the expiry can be set [5](#0-4) , and the operation itself is a straightforward pass-through to the on-chain `WorkflowRegistry.AllowlistRequest` call with no visible additional caps in the surrounding Go tooling [6](#0-5) . I was unable to locate the Solidity source of `WorkflowRegistry.AllowlistRequest` itself within this repository's index (only generated Go bindings and Go-side deployment tooling reference it), so I could not directly confirm from the contract source whether the on-chain method enforces any rate limiting, per-owner caps, or fee/staking requirements beyond gas cost. This is a genuine gap in verification, not a refutation of the claim.

Nonetheless, the Go-side authorization code precisely matches what is described: unbounded slice growth via periodic merge-without-cap, full linear rescans on every authorization call, and repeated debug-string construction across retries — all confirmed directly in the cited source.

## Impact Explanation
This is a legitimate architectural weakness: an attacker who can grow the allowlist (via repeated `AllowlistRequest` calls with far-future expiries, assuming — as the report claims and as is typical for such permissionless "register my own request" contract methods — no meaningful cap exists on-chain) increases per-request authorization latency and CPU cost for the entire Vault DON, since every request (from any user) must scan and re-stringify the same growing list. This maps to a DoS/availability degradation of the Vault gateway's authorization pipeline, an in-scope impact category. The severity is more accurately "degraded performance / resource-exhaustion" rather than complete denial of service, since authorization ultimately still succeeds/fails correctly — it just becomes slower and more resource-intensive as the list grows.

## Likelihood Explanation
The likelihood is moderate and contingent on the true on-chain constraints of `WorkflowRegistry.AllowlistRequest`, which could not be fully verified from the Solidity source in this repository's index. Assuming the method is genuinely permissionless for any linked owner and has no on-chain cap on active entries or expiry horizon (as implied by the absence of such checks in the surrounding Go tooling), an attacker only needs gas funds and a linked owner address — both low-privilege, attacker-controllable preconditions — to repeatedly grow the list and degrade authorization performance for all tenants.

## Recommendation
- Replace the linear scan in `fetchAllowlistedItem` with a map keyed by `RequestDigest` for O(1) lookup [7](#0-6) .
- Guard the `allowedRequestsStrs` debug-string construction behind a log-level check so it is not built unconditionally on every retry attempt [8](#0-7) .
- Verify and, if absent, add an on-chain cap on `ExpiryTimestamp` horizon and/or maximum active allowlisted entries per owner/globally in the `WorkflowRegistry` contract to bound `syncAllowlistedRequests` growth [9](#0-8) .

## Proof of Concept
1. Link a workflow owner address (permissionless onboarding).
2. Repeatedly submit `WorkflowRegistry.AllowlistRequest(requestDigest, expiryTimestamp)` transactions with distinct digests and far-future expiries to grow the on-chain allowlist (see `UserAllowlistRequestOp` at `deployment/cre/workflow_registry/v2/changeset/operations/contracts/user_workflow_registry_ops.go:360-387`).
3. Confirm via logs/metrics that `syncAllowlistedRequests` merges these into `w.allowListedRequests` without shrinking (`core/services/workflows/syncer/v2/workflow_registry.go:780-795`).
4. Measure increasing latency/CPU in `findAllowlistedItemWithRetry` (`core/capabilities/vault/allow_list_based_auth.go:79-111`) for normal Vault requests as the list grows, via a Go benchmark/unit test constructing a large slice and timing `fetchAllowlistedItem` + debug-string building.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L79-94)
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
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L113-120)
```go
func (r *allowListBasedAuth) fetchAllowlistedItem(allowListedRequests []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest, digest [32]byte) *workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest {
	for _, item := range allowListedRequests {
		if item.RequestDigest == digest {
			return &item
		}
	}
	return nil
}
```

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L766-806)
```go
func (w *workflowRegistry) syncAllowlistedRequests(ctx context.Context) {
	ticker := w.getTicker(defaultTickIntervalForAllowlistedRequests)
	w.lggr.Debug("starting syncAllowlistedRequests")
	for {
		select {
		case <-ctx.Done():
			w.lggr.Debug("shutting down syncAllowlistedRequests, %s", ctx.Err())
			return
		case <-ticker:
			newAllowListedRequests, totalAllowlistedRequests, head, err := w.getAllowlistedRequests(ctx, w.contractReader)
			if err != nil {
				w.lggr.Errorw("failed to call getAllowlistedRequests", "err", err)
				continue
			}
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
			w.lggr.Debugw("synced allowlisted requests",
				"newRequestsNum", len(newAllowListedRequests),
				"expiredRequestsNum", expiredRequestsCount,
				"activeRequestsNum", len(w.allowListedRequests),
				"lastSeenOnchainRequestsNum", w.lastSeenAllowlistedRequestsCount,
				"blockHeight", head.Height,
			)
			w.allowListedMu.Unlock()
		}
	}
}
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

**File:** core/capabilities/vault/gw_handler.go (L84-126)
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
