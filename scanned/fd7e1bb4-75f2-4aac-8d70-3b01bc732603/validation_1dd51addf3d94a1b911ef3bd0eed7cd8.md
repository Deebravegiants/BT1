### Title
Unbounded, linearly-scanned `allowListedRequests` slice causes DoS on Vault gateway request authorization - (File: `core/capabilities/vault/allow_list_based_auth.go`, `core/services/workflows/syncer/v2/workflow_registry.go`)

### Summary
Every incoming Vault gateway request (`secrets.create`, `secrets.update`, `secrets.delete`, `secrets.list`) is authorized by scanning the full in-memory `allowListedRequests` slice synced from the `WorkflowRegistry` contract. This slice has no bound on size and is scanned linearly, with retries, on the hot request-authorization path for every request received from the internet-facing gateway. An actor who can get entries allowlisted on-chain can grow this list without limit, degrading (and potentially indefinitely delaying) authorization for all subsequent legitimate requests handled by every Vault DON node — directly analogous to the reported unbounded-array-iteration griefing DoS.

### Finding Description
`allowListBasedAuth.AuthorizeRequest` computes a request digest and calls `findAllowlistedItemWithRetry`, which repeatedly fetches the full list of allowlisted requests and performs a full linear scan (`fetchAllowlistedItem`) to find a match, retrying up to `allowListBasedAuthRetryCount` (10) times with a 3-second sleep between attempts: [1](#0-0) 

The underlying data comes from `workflowRegistry.GetAllowlistedRequests`, which returns a full copy of the in-memory `allowListedRequests` slice on every call: [2](#0-1) 

This slice is populated by `syncAllowlistedRequests`, which appends newly observed on-chain allowlist entries to the existing (pruned) slice every 5 seconds, with no upper bound on total size — only expired entries are pruned, and expiry is attacker-controlled (an owner can set an arbitrarily far-future `ExpiryTimestamp`): [3](#0-2) 

The contract-fetch path itself only paginates in chunks of `MaxResultsPerQuery` (1,000) to page through however many total entries exist on-chain — it does not cap the total count, it just avoids over-fetching per RPC call: [4](#0-3) 

Because `GetAllowlistedRequests` copies and returns the *entire* list on every single incoming vault request (`AuthorizeRequest`), and `fetchAllowlistedItem` does a linear scan over it (repeated up to 11 times per request when the entry momentarily isn't found), the CPU/memory cost of authorizing every Vault gateway request scales linearly with the total number of allowlisted (unexpired) entries. There is no data structure (e.g., map keyed by digest) to make lookups O(1), and no cap on the number of entries a workflow owner may allowlist. A workflow owner able to call `AllowlistRequest` on the `WorkflowRegistry` contract (demonstrated in test helpers such as `allowlistRequest` in `system-tests/tests/smoke/cre/vault_don_test_helpers.go`) can register an arbitrarily large number of entries with long expiries, and this growth is unconditionally synced and copied/scanned by every Vault DON node on every incoming request: [5](#0-4) 

The existing test explicitly demonstrates the syncer tolerating and storing counts well beyond `MaxResultsPerQuery` (1,001+ entries), confirming there is no design-level cap on list growth, only pagination for fetching: [6](#0-5) 

This is architecturally the same bug class as the reported OpenQ `getLockedFunds` issue: an unbounded, attacker-growable collection is fully iterated (here, copied + linearly scanned, repeatedly) on a critical, per-request unprivileged-facing operation (request authorization on the internet-facing Vault gateway), with no size limit or indexed lookup to bound the cost.

### Impact Explanation
As the allowlist grows, every `HandleGatewayMessage` call for `secrets.create/update/delete/list` on every Vault DON node pays an ever-increasing linear cost just to authorize the request (copy + scan of the whole list, up to 11 times per request due to retries): [7](#0-6) 

This degrades latency and throughput of the entire gateway-facing Vault authorization pipeline for *all* users, not just the attacker, and in the worst case (very large list, combined with the retry loop) can push request processing time high enough to trigger gateway timeouts (`RequestTimeoutError`) for legitimate requests, effectively causing a DoS on secret creation/update/deletion/listing across the DON: [8](#0-7) 

### Likelihood Explanation
Likelihood is moderate-to-high in adversarial conditions: any address authorized to interact with the `WorkflowRegistry` contract for a DON family can repeatedly call `AllowlistRequest` with distinct digests and long expiries (cheap relative to the sustained node-side cost, since the cost is paid by every DON node on every subsequent request, not by the caller). There is no application-level cap, rate limit, or eviction policy beyond expiry-based pruning, and the syncer unconditionally accepts and stores whatever the contract reports.

### Recommendation
- Cap the maximum number of active allowlist entries retained in memory (and reject/alert when exceeded), and/or enforce an on-chain limit on entries per owner or per DON family.
- Replace the linear `fetchAllowlistedItem` scan with an O(1) lookup structure (e.g., a `map[[32]byte]*WorkflowRegistryOwnerAllowlistedRequest` keyed by `RequestDigest`), rebuilt once per sync tick, rather than copying and linearly scanning the full slice inside the hot per-request authorization path.
- Bound or shorten the maximum allowed `ExpiryTimestamp` window to reduce how long stale/abusive entries linger before pruning.
- Consider removing or reducing the retry loop's cost amplification (11x linear scans per request) by decoupling "wait for propagation" retries from "full re-scan" cost, e.g., checking only newly synced entries on retry.

### Proof of Concept
1. An authorized workflow owner repeatedly calls `AllowlistRequest` on the `WorkflowRegistry` contract with many distinct `RequestDigest` values and expiry timestamps far in the future (as done via `allowlistRequest` in `system-tests/tests/smoke/cre/vault_don_test_helpers.go`), growing the on-chain allowlist to tens/hundreds of thousands of entries.
2. Every Vault DON node's `workflowRegistry.syncAllowlistedRequests` (`core/services/workflows/syncer/v2/workflow_registry.go:766-806`) picks up and retains all unexpired entries in its `allowListedRequests` in-memory slice, unbounded.
3. Any legitimate user sends a `secrets.list`/`secrets.create` request through the gateway; `GatewayHandler.HandleGatewayMessage` invokes `requestProcessor.ProcessRequest` → `allowListBasedAuth.AuthorizeRequest` → `findAllowlistedItemWithRetry`, which copies and linearly scans the now-huge slice up to 11 times per request (`core/capabilities/vault/allow_list_based_auth.go:79-111`).
4. As the list grows, per-request authorization latency grows linearly, degrading service for all users and risking gateway-side request timeouts (`core/services/gateway/gateway.go:281-288`), reproducing the "unbounded loop causes indefinite DoS" bug class from the reference report in the Vault gateway's authorization path.

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

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L1510-1521)
```go
func allowlistRequest(t *testing.T, owner string, request jsonrpc.Request[json.RawMessage], sethClient *seth.Client, wfRegistryContract *workflow_registry_v2_wrapper.WorkflowRegistry) {
	requestDigest, err := request.Digest()
	require.NoError(t, err, "failed to get digest for request")
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	require.NoError(t, err, "failed to decode digest")
	reqDigestBytes := [32]byte(requestDigestBytes)
	_, err = wfRegistryContract.AllowlistRequest(sethClient.NewTXOpts(), reqDigestBytes, uint32(time.Now().Add(1*time.Hour).Unix())) //nolint:gosec // disable G115
	require.NoError(t, err, "failed to allowlist request")

	framework.L.Info().Msgf("Allowlisting request digest at contract %s, for owner: %s, digestHexStr: %s", wfRegistryContract.Address().Hex(), owner, requestDigest)
	allowedList, err := wfRegistryContract.GetAllowlistedRequests(&bind.CallOpts{}, big.NewInt(0), big.NewInt(100))
	require.NoError(t, err, "failed to validate allowlisted request")
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
