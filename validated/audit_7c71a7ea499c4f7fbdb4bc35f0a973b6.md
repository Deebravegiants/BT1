Audit Report

## Title
Unbounded, linearly-scanned `allowListedRequests` slice causes DoS on Vault gateway request authorization - (File: `core/capabilities/vault/allow_list_based_auth.go`, `core/services/workflows/syncer/v2/workflow_registry.go`)

## Summary
Every Vault gateway request (`secrets.create/update/delete/list`) is authorized by `allowListBasedAuth.AuthorizeRequest`, which repeatedly (up to 11 times, with 3s sleeps) fetches a full copy of the in-memory `allowListedRequests` slice and performs a linear scan to find a matching digest. This slice is populated by `workflowRegistry.syncAllowlistedRequests` with no upper bound on total size — only expiry-based pruning exists — so a workflow owner able to call `AllowlistRequest` on-chain can grow the list indefinitely, degrading authorization latency for every subsequent request handled by every Vault DON node.

## Finding Description
`findAllowlistedItemWithRetry` in `core/capabilities/vault/allow_list_based_auth.go` fetches `GetAllowlistedRequests` (a full slice copy under an RLock) and calls `fetchAllowlistedItem`, a linear scan, on every attempt of up to `retryCount+1` (11) iterations per single incoming gateway request. `syncAllowlistedRequests` in `core/services/workflows/syncer/v2/workflow_registry.go` only prunes entries by expiry timestamp and unconditionally appends all newly observed on-chain entries — there is no cap on total entries retained. The on-chain fetch path (`getAllowlistedRequests`) only paginates fetching in chunks of `MaxResultsPerQuery` (1,000); it does not cap the total count of entries that can exist. The existing test `Test_InitialStateSyncV2` explicitly creates 1,001+ allowlisted entries and confirms the syncer stores and tolerates this without any limit, validating that no design-level cap exists.

Regarding exploitability: `AllowlistRequest` on the `WorkflowRegistry` contract is called by a "workflow owner" that must first self-link via `LinkOwner`, which — per the test helper `updateAuthorizedAddressV2` and `generateAndSignOwnershipProof` — requires only a self-generated signature proving control of the calling address (plus being on an "allowed signers" list configured by DON operators, or MCMS/authorized-address gating in some deployments). The wrapper code and deployment changesets (`deployment/cre/workflow_registry/v2/changeset/user_workflow_registry.go`) show `UserAllowlistRequest` is a standard user-facing changeset action, not an owner/admin-only operation, and its `VerifyPreconditions` only checks that expiry and digest are non-empty — no rate limit or per-owner cap is enforced there either. This confirms that the linear-scan authorization path scales with a value that a "workflow owner" (a normal, low-privilege participant in this system) directly controls and can grow without bound.

## Impact Explanation
As `allowListedRequests` grows, `HandleGatewayMessage` for every Vault DON node pays an ever-increasing linear cost (full slice copy + scan, up to 11× per request) merely to authorize any request. This degrades latency/throughput of the gateway-facing Vault authorization pipeline for all users and can, in the worst case, push processing time past the gateway's callback timeout (`gateway.go`'s `RequestTimeoutError`), effectively causing a denial of service on secret creation/update/deletion/listing across the DON. This maps to the "unauthorized denial of service via unbounded resource growth on an internet-facing gateway path" impact class.

## Likelihood Explanation
Likelihood is moderate: any address able to self-link as a workflow owner (a standard, low-barrier onboarding step, gated only by allowed-signer configuration and a self-signed ownership proof, not admin/operator credentials) can repeatedly call `AllowlistRequest` with distinct digests and long expiries. The cost of each call is borne by the caller on-chain (gas), but the resulting node-side degradation is paid by every DON node on every subsequent request — an asymmetric griefing vector with no application-level cap, rate limit, or eviction policy beyond expiry-based pruning.

## Recommendation
- Cap the maximum number of active allowlist entries retained in memory per owner and/or globally, rejecting or throttling further `AllowlistRequest` calls beyond the cap (ideally enforced on-chain).
- Replace the linear `fetchAllowlistedItem` scan with an O(1) lookup structure (e.g., a `map[[32]byte]*WorkflowRegistryOwnerAllowlistedRequest` keyed by `RequestDigest`), rebuilt once per sync tick rather than copied and scanned per request.
- Bound the maximum allowed `ExpiryTimestamp` window to reduce the time abusive/stale entries can linger.
- Decouple "wait for propagation" retries in `findAllowlistedItemWithRetry` from full re-scans, e.g., only re-checking newly synced entries on retry.

## Proof of Concept
1. Self-link an EOA as a workflow owner via `LinkOwner` (using a self-generated ownership-proof signature, as done in `updateAuthorizedAddressV2`/`generateAndSignOwnershipProof`).
2. Repeatedly call `AllowlistRequest` on `WorkflowRegistry` with many distinct `RequestDigest` values and far-future `ExpiryTimestamp`s (as in `allowlistRequest` helper in `system-tests/tests/smoke/cre/vault_don_test_helpers.go`), growing the on-chain allowlist to tens/hundreds of thousands of entries — the existing `Test_InitialStateSyncV2` test already demonstrates 1,001+ entries being accepted without any cap.
3. Every Vault DON node's `syncAllowlistedRequests` (`core/services/workflows/syncer/v2/workflow_registry.go:766-806`) retains all unexpired entries in its unbounded in-memory `allowListedRequests` slice.
4. Send a legitimate `secrets.list`/`secrets.create` request through the gateway; `GatewayHandler.HandleGatewayMessage` → `AuthorizeRequest` → `findAllowlistedItemWithRetry` (`core/capabilities/vault/allow_list_based_auth.go:79-111`) copies and linearly scans the now-large slice up to 11 times per request, with measurably increased authorization latency as list size grows, risking `RequestTimeoutError` under sufficient list growth (`core/services/gateway/gateway.go:281-288`). [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L79-96)
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

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L1236-1268)
```go
func (w *workflowRegistry) getAllowlistedRequests(ctx context.Context, contractReader types.ContractReader) ([]workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest, *big.Int, *types.Head, error) {
	if contractReader == nil {
		return nil, nil, nil, errors.New("cannot fetch allow listed requests: nil contract reader")
	}
	contractBinding := types.BoundContract{
		Address: w.workflowRegistryAddress,
		Name:    WorkflowRegistryContractName,
	}

	// Read current total allowlisted requests
	var headAtLastRead *types.Head
	var totalAllowlistedRequestsResult *big.Int
	readIdentifier := contractBinding.ReadIdentifier(TotalAllowlistedRequestsMethodName)
	headAtLastRead, err := contractReader.GetLatestValueWithHeadData(
		ctx, readIdentifier, primitives.Unconfirmed, nil, &totalAllowlistedRequestsResult,
	)
	if err != nil {
		return []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest{}, w.lastSeenAllowlistedRequestsCount, &types.Head{Height: "0"}, errors.New("failed to get latest value with head data. error: " + err.Error())
	}

	if w.lastSeenAllowlistedRequestsCount.Cmp(totalAllowlistedRequestsResult) == 0 {
		return []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest{}, totalAllowlistedRequestsResult, headAtLastRead, nil
	}

	var newAllowlistedRequests []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest
	readIdentifier = contractBinding.ReadIdentifier(GetActiveAllowlistedRequestsReverseMethodName)
	var endIndex = new(big.Int).Sub(totalAllowlistedRequestsResult, big.NewInt(1))
	var startIndex *big.Int

	for {
		var err error
		var response struct {
			AllowlistedRequests []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest
```

**File:** core/services/workflows/syncer/v2/workflow_syncer_v2_test.go (L67-92)
```go
	// Add requests to ensure we go above the MaxResultsPerQuery
	activeAllowlistedRequestsCount := int(MaxResultsPerQuery + 1)
	expiryTimestamp := time.Now().Add(24 * time.Hour)
	for i := range activeAllowlistedRequestsCount {
		createSecretsRequestParams, marshalErr := json.Marshal(vaultcommon.CreateSecretsRequest{
			EncryptedSecrets: []*vaultcommon.EncryptedSecret{
				{
					Id: &vaultcommon.SecretIdentifier{
						Key:       strconv.Itoa(i),
						Namespace: "active",
					},
					EncryptedValue: "encrypted-value",
				},
			},
		})
		require.NoError(t, marshalErr)

		allowlistRequest(t, backendTH, wfRegistryC, allowlistRequestParams{
			Request: jsonrpc.Request[json.RawMessage]{
				Method: vaulttypes.MethodSecretsCreate,
				Params: (*json.RawMessage)(&createSecretsRequestParams),
			},
			Owner:           backendTH.ContractsOwner.From,
			ExpiryTimestamp: expiryTimestamp,
		})
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

**File:** core/capabilities/vault/gw_handler.go (L180-211)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

	var response *jsonrpc.Response[json.RawMessage]
	var authResult *AuthResult

	switch req.Method {
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}
```

**File:** core/services/gateway/gateway.go (L281-288)
```go
	response, err := callback.Wait(ctx)
	duration := time.Since(startTime)
	if err != nil {
		response := api.RequestTimeoutError
		g.gMetrics.RecordUserMsgHandlerDuration(ctx, method, response.String(), duration)
		g.gMetrics.RecordUserMsgHandlerInvocation(ctx, method, response.String())
		return newError(jsonRequest.ID, response, "handler timeout: "+err.Error())
	}
```
