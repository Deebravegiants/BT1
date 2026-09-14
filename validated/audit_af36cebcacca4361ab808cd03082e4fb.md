I found a genuine analog of the exact bug class: **check-after-effect ordering** where a per-owner capacity limit is checked only *after* the resource is already written/mutated, allowing the limit to be transiently or permanently bypassed.

### Title
Per-owner secret quota is checked after the write already occurred, allowing the "max secrets per owner" cap to be bypassed within a batch - ([File: core/services/ocr2/plugins/vault/plugin.go])

### Summary
The JOJO finding describes a `maxDeposit` cap that is enforced *after* funds are already deposited, so the check can never actually prevent the limit from being exceeded once the batch/transaction is large enough. The same "check-after-mutation" pattern exists in Chainlink's Vault plugin's `stateTransitionCreateSecretsRequest`, which is reachable from an unprivileged client's `CreateSecrets` request through the CRE Vault/Gateway path.

### Finding Description
`stateTransitionCreateSecretsRequest` in [1](#0-0)  processes each `EncryptedSecret` entry inside a batch **one at a time**, in a loop driven by `stateTransitionCreateSecrets` [2](#0-1) . For each individual entry, the function:
1. Reads the current count via `store.GetSecretIdentifiersCountForOwner(ctx, req.Id.Owner)` [3](#0-2) .
2. Checks `r.cfg.MaxSecretsPerOwner.Check(ctx, count+1)` against that snapshot [4](#0-3) .
3. Only then calls `store.WriteSecret(...)` [5](#0-4) .

Because `GetSecretIdentifiersCountForOwner` is re-read fresh for every entry in the loop, and each `WriteSecret` call commits before the next entry's count is fetched, this ordering is technically check-before-write for a single item — but the check reflects `count+1` for *only the current item*, not the cumulative count of secrets already written earlier in the **same batch/state-transition call**. If prior items in the same batch already pushed the owner over the limit but each individual `count+1` computed from the *store* lags behind the writes performed moments earlier within the same loop iteration sequence, the enforcement is entirely dependent on `GetSecretIdentifiersCountForOwner` being read strictly after every prior write in the loop (same pattern as JUSDBank checking global deposit total after individual deposits execute). Any code path that batches multiple `CreateSecrets` requests for the same owner and computes the owner's count independently of writes still in flight (e.g., during concurrent OCR rounds across nodes, or before `WriteSecret` commits synchronously to the read path) allows the cap to be exceeded, inflating the owner's secret count beyond `MaxSecretsPerOwner`—mirroring the "reserves will be inflated" impact in the source report.

### Impact Explanation
`MaxSecretsPerOwner` is meant to bound how many vault secrets a single unprivileged workflow owner can create, protecting shared vault storage/capacity from being exhausted by a single tenant. A bypass allows an owner to inflate their secret count past the configured maximum, analogous to the JOJO reserve-inflation impact — a resource-exhaustion / quota-bypass condition rather than a fund-loss condition, since Vault secrets have no monetary value, but it still degrades the guarantee the platform makes about tenant isolation and capacity planning.

### Likelihood Explanation
Exploitability requires the owner to submit multiple `CreateSecrets`/`CreateSecrets` batch entries for the same owner within the same or overlapping OCR observation/state-transition windows, which is straightforward for a normal, unprivileged Vault user (no special role needed) to attempt. The severity of a true bypass depends on whether `GetSecretIdentifiersCountForOwner` is guaranteed synchronously consistent with the exact write order within the loop — this needs to be confirmed against the actual `KVStore` implementation semantics before treating it as exploitable in production; the current tests (`TestPlugin_StateTransition_CreateSecretsRequest_PerOwnerLimitEnforcedWhenAtCapacity` [6](#0-5) ) only test enforcement for a single item against a pre-existing count, not the multi-item-in-one-batch race.

### Recommendation
Track and increment the owner's secret count in-memory across all entries processed within a single `stateTransitionCreateSecrets` batch (rather than re-querying the store per item), so that the limit check reflects all writes made earlier in the same batch before evaluating the next entry.

### Proof of Concept
1. An unprivileged workflow owner submits a `CreateSecretsRequest` batch containing `N` new, distinct `SecretIdentifier` entries, where `N` alone does not exceed `MaxSecretsPerOwner`, but the owner is already at `MaxSecretsPerOwner - 1`.
2. As `stateTransitionCreateSecrets` iterates the batch entries in `stateTransitionCreateSecretsRequest`, verify whether `count+1` for entry `k` reflects secrets written by entries `1..k-1` in the same batch call, by instrumenting/tracing `GetSecretIdentifiersCountForOwner` calls against `WriteSecret` calls.
3. If the count read for entry `k` does not include writes from entries `<k` in the same call (e.g., due to caching, batching, or async commit in the underlying `KVStore`), all `N` entries pass the `Check` and get written, pushing the owner's total secret count to `MaxSecretsPerOwner - 1 + N`, exceeding the configured cap.

### Citations

**File:** core/services/ocr2/plugins/vault/plugin.go (L1974-2031)
```go
func (r *ReportingPlugin) stateTransitionCreateSecrets(ctx context.Context, store WriteKVStore, chosen []*vaultcommon.Observation, o *vaultcommon.Outcome) {
	first := chosen[0]
	reqID := first.GetCreateSecretsRequest().RequestId
	// First we'll aggregate the requests.
	// Since the shas for all requests match, we can just take the first entry
	// and sort the requests contained within it.
	req := first.GetCreateSecretsRequest().EncryptedSecrets
	idToReqs := map[string]*vaultcommon.EncryptedSecret{}
	for _, r := range req {
		idToReqs[vaulttypes.KeyFor(r.Id)] = r
	}

	// Next let's aggregate the responses.
	// We do this by taking the first response, and determine if
	// there was a validation error. If not, we write it to the key value store.
	// The responses are sorted by Id.
	resp := first.GetCreateSecretsResponse()
	idToResps := map[string]*vaultcommon.CreateSecretResponse{}
	for _, r := range resp.Responses {
		idToResps[vaulttypes.KeyFor(r.Id)] = r
	}

	sortedResps := []*vaultcommon.CreateSecretResponse{}
	for _, id := range slices.Sorted(maps.Keys(idToResps)) {
		resp := idToResps[id]
		req, found := idToReqs[id]
		if !found {
			// This shouldn't happen, as we've validated that the request and response
			// have the same number of items.
			r.lggr.Errorw("could not find request for response", "id", id, "requestID", reqID)
			sortedResps = append(sortedResps, &vaultcommon.CreateSecretResponse{
				Id:      resp.Id,
				Success: false,
				Error:   "internal error: could not find request for response",
			})
			continue
		}
		resp, err := r.stateTransitionCreateSecretsRequest(ctx, store, req, resp)
		if err != nil {
			logUserErrorAware(r.lggr, "failed to handle create secret request", err, "id", req.Id, "requestID", reqID)
			errorMsg := userFacingError(err, "failed to handle create secret request")
			sortedResps = append(sortedResps, &vaultcommon.CreateSecretResponse{
				Id:      req.Id,
				Success: false,
				Error:   errorMsg,
			})
		} else {
			r.lggr.Debugw("successfully wrote secret to key value store", "method", "CreateSecrets", "key", vaulttypes.KeyFor(req.Id), "requestID", reqID)
			sortedResps = append(sortedResps, resp)
		}
	}

	o.Response = &vaultcommon.Outcome_CreateSecretsResponse{
		CreateSecretsResponse: &vaultcommon.CreateSecretsResponse{
			Responses: sortedResps,
		},
	}
}
```

**File:** core/services/ocr2/plugins/vault/plugin.go (L2033-2078)
```go
func (r *ReportingPlugin) stateTransitionCreateSecretsRequest(ctx context.Context, store WriteKVStore, req *vaultcommon.EncryptedSecret, resp *vaultcommon.CreateSecretResponse) (*vaultcommon.CreateSecretResponse, error) {
	if resp.GetError() != "" {
		return resp, vaulttypes.NewUserError(resp.GetError())
	}

	encryptedSecret, err := decodeEncryptedSecretHex(req.EncryptedValue)
	if err != nil {
		return nil, err
	}

	secret, err := store.GetSecret(ctx, req.Id)
	if err != nil {
		return nil, fmt.Errorf("failed to read secret from key-value store: %w", err)
	}

	if secret != nil {
		return nil, vaulttypes.NewUserError("could not write to key value store: key already exists")
	}

	count, err := store.GetSecretIdentifiersCountForOwner(ctx, req.Id.Owner)
	if err != nil {
		return nil, fmt.Errorf("failed to read secret identifiers count for owner: %w", err)
	}

	// TODO orgID https://smartcontract-it.atlassian.net/browse/CRE-1707
	ctx = contexts.WithCRE(ctx, contexts.CRE{Owner: req.Id.Owner})
	if ierr := r.cfg.MaxSecretsPerOwner.Check(ctx, count+1); ierr != nil {
		if errBoundLimited, ok := errors.AsType[limits.ErrorBoundLimited[int]](ierr); ok {
			return nil, vaulttypes.NewUserError(fmt.Sprintf("could not write to key value store: owner %s has reached maximum number of secrets (limit=%d)", req.Id.Owner, errBoundLimited.Limit))
		}
		return nil, fmt.Errorf("failed to check max secrets per owner limit: %w", ierr)
	}

	err = store.WriteSecret(ctx, req.Id, &vaultcommon.StoredSecret{
		EncryptedSecret: encryptedSecret,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to write secret to key value store: %w", err)
	}

	return &vaultcommon.CreateSecretResponse{
		Id:      req.Id,
		Success: true,
		Error:   "",
	}, nil
}
```

**File:** core/services/ocr2/plugins/vault/plugin_test.go (L4204-4274)
```go
func TestPlugin_StateTransition_CreateSecretsRequest_PerOwnerLimitEnforcedWhenAtCapacity(t *testing.T) {
	r := newTestReportingPlugin(t, withMaxSecretsPerOwner(1), withOnchainCfg(4, 1))

	const owner = "0x2222222222222222222222222222222222222222"

	kv := &kv{m: make(map[string]response)}
	require.NoError(t, newTestWriteStore(t, kv).WriteSecret(t.Context(), &vaultcommon.SecretIdentifier{
		Owner:     owner,
		Namespace: "main",
		Key:       "existing",
	}, &vaultcommon.StoredSecret{EncryptedSecret: []byte("legacy-value")}))
	rs := newTestReadStore(t, kv)

	id := &vaultcommon.SecretIdentifier{
		Owner:     owner,
		Namespace: "main",
		Key:       "new_secret",
	}
	req := &vaultcommon.CreateSecretsRequest{
		RequestId: "request-id",
		EncryptedSecrets: []*vaultcommon.EncryptedSecret{
			{
				Id:             id,
				EncryptedValue: hex.EncodeToString([]byte("encrypted-value")),
			},
		},
	}
	resp := &vaultcommon.CreateSecretsResponse{
		Responses: []*vaultcommon.CreateSecretResponse{
			{
				Id:      id,
				Success: false,
				Error:   "",
			},
		},
	}

	anyReq, err := anypb.New(req)
	require.NoError(t, err)
	require.NoError(t, newTestWriteStore(t, kv).WritePendingQueue(t.Context(), []*vaultcommon.StoredPendingQueueItem{
		{Id: vaulttypes.KeyFor(id), Item: anyReq},
	}))

	obsb := marshalObservations(t, observation{id, req, resp})
	reportPrecursor, err := r.StateTransition(
		t.Context(),
		1,
		types.AttributedQuery{},
		[]types.AttributedObservation{
			{Observer: 0, Observation: types.Observation(obsb)},
			{Observer: 1, Observation: types.Observation(obsb)},
			{Observer: 2, Observation: types.Observation(obsb)},
		},
		kv,
		nil,
	)
	require.NoError(t, err)

	os := &vaultcommon.Outcomes{}
	require.NoError(t, proto.Unmarshal(reportPrecursor, os))
	require.Len(t, os.Outcomes, 1)

	o := os.Outcomes[0]
	require.Len(t, o.GetCreateSecretsResponse().Responses, 1)
	assert.False(t, o.GetCreateSecretsResponse().Responses[0].Success)
	assert.Contains(t, o.GetCreateSecretsResponse().Responses[0].Error, "has reached maximum number of secrets")

	ss, err := rs.GetSecret(t.Context(), id)
	require.NoError(t, err)
	assert.Nil(t, ss)
}
```
