## Title
Missing List-Size Bound Check During Vault `ListSecretIdentifiers` Observation Allows Unbounded Resource Consumption Before Limit Enforcement - ([File: core/services/ocr2/plugins/vault/plugin.go])

### Summary
The ImageMagick MNG-coder advisory describes a bug class where a component reads and processes list items without checking a configured maximum-count policy first, allowing the policy limit to be effectively bypassed and causing excessive resource use. An analogous pattern exists in the Chainlink Vault OCR reporting plugin's `ListSecretIdentifiers` observation path: the node reads and materializes the *entire* set of secret identifiers for a requested owner with no size cap, and only checks the `MaxSecretsPerOwner` bound later, when a *different* oracle validates the *already-produced* observation.

### Finding Description
`processListSecretIdentifiersRequest` reads an owner's full metadata record from the KV store, sorts every stored identifier, and returns them all (optionally filtered by namespace) with no bound/limit check applied: [1](#0-0) 

This function is invoked directly from `observeListSecretIdentifiers`, i.e. during each node's own `Observation()` production for every incoming `ListSecretIdentifiers` request — an unprivileged, externally-triggerable JSON-RPC vault method: [2](#0-1) 

By contrast, the `MaxSecretsPerOwner` bound is enforced only as a *peer cross-check* — inside `ValidateObservation`, via `validateListSecretIdentifiersResponseSize`, which is applied to observations that other oracles receive, not to the observation the producing node itself just computed: [3](#0-2) [4](#0-3) 

Additionally, the request-side validator that gates a `ListSecretIdentifiers` request before it even reaches the DON contains no batch/result-size limiter at all, unlike its sibling validators for `GetSecrets` and `DeleteSecrets`, which both call `MaxRequestBatchSizeLimiter.Check`: [5](#0-4) 

So the sequence for every DON member per request is: (1) read full owner metadata, (2) sort all identifiers, (3) build the complete response slice — all unconditionally — and only *after* that, when a peer validates the observation, is the `MaxSecretsPerOwner` policy checked. This mirrors the MNG advisory precisely: the "list limit policy" exists but is applied after, not before, the expensive read/processing work, so the policy does not actually bound the work the node performs to satisfy the request.

### Impact Explanation
Every member of the vault DON performs the unbounded read/sort/materialize work for each `ListSecretIdentifiers` request regardless of the configured `MaxSecretsPerOwner` limit, because the bound is enforced only downstream during cross-oracle observation validation, not at the point of doing the actual work. This is a CWE-400/CWE-407 uncontrolled resource consumption pattern: an unprivileged client that can drive an owner's stored secret-identifier count above the configured limit (or otherwise cause metadata to grow large) forces repeated full-list computation across the DON on every list call, with the "list limit policy" only ever rejecting the result after the cost has already been paid by all nodes, not preventing it.

### Likelihood Explanation
The `ListSecretIdentifiers` request is reachable via the standard unauthenticated-request-shape gateway/vault capability path exercised in `core/capabilities/vault/capability.go` and `core/capabilities/vault/gw_handler.go`, requiring only that a client can submit vault list requests for an owner (subject to normal allowlist/JWT authorization, not privileged operator access). The missing pre-read bound check is deterministic and triggers on every request for an owner whose stored identifier count is at or above the configured limit.

### Recommendation
Enforce `MaxSecretsPerOwner` (or an equivalent read-time cap) inside `processListSecretIdentifiersRequest` before/while iterating and sorting `md.SecretIdentifiers`, so that the node bounds the work it performs and the size of the response it constructs, rather than relying solely on peer-side `ValidateObservation` checks after the fact. Consider also adding a defensive bound check to `RequestValidator.ValidateListSecretIdentifiersRequest` for consistency with `ValidateGetSecretsRequest`/`ValidateDeleteSecretsRequest`.

### Proof of Concept
1. Cause (or have) an owner's stored `StoredMetadata.SecretIdentifiers` to exceed the configured `MaxSecretsPerOwner` value (e.g., via repeated `CreateSecrets` calls, whose write-time enforcement of this specific cap could not be confirmed from the available code and should be verified independently).
2. Submit a `ListSecretIdentifiers` request for that owner through the vault capability path (`core/capabilities/vault/capability.go:214-222`).
3. Observe that every DON node executes `processListSecretIdentifiersRequest`, reading, sorting, and constructing the full identifier list in its own `Observation()` call before any size limit is applied — the `MaxSecretsPerOwner` check only fires later in `ValidateObservation` on peers' copies of the observation, after the expensive work has already occurred on every node.

Note: I could not conclusively verify from the indexed code whether `CreateSecrets`/write-time flows enforce `MaxSecretsPerOwner` inline (only one non-list usage location was found in the grep results, and its content wasn't inspected); this should be confirmed to fully establish the write-side attack surface for growing an owner's identifier count past the limit.

### Citations

**File:** core/services/ocr2/plugins/vault/plugin.go (L1122-1146)
```go
func (r *ReportingPlugin) observeListSecretIdentifiers(ctx context.Context, seqNr uint64, requestID string, reader ReadKVStore, req proto.Message, o *vaultcommon.Observation) {
	tp := req.(*vaultcommon.ListSecretIdentifiersRequest)
	l := r.typedRequestLggr(seqNr, requestID, "ListSecretIdentifiers").With("owner", tp.Owner)
	o.RequestType = vaultcommon.RequestType_LIST_SECRET_IDENTIFIERS
	o.Request = &vaultcommon.Observation_ListSecretIdentifiersRequest{
		ListSecretIdentifiersRequest: tp,
	}

	resp, err := r.processListSecretIdentifiersRequest(ctx, seqNr, requestID, reader, tp)
	if err != nil {
		l.Debugw("failed to process list secret identifiers request", "error", err)
		o.Response = &vaultcommon.Observation_ListSecretIdentifiersResponse{
			ListSecretIdentifiersResponse: &vaultcommon.ListSecretIdentifiersResponse{
				Error:   err.Error(),
				Success: false,
			},
		}
		return
	}

	l.Debugw("observed list secret identifiers request")
	o.Response = &vaultcommon.Observation_ListSecretIdentifiersResponse{
		ListSecretIdentifiersResponse: resp,
	}
}
```

**File:** core/services/ocr2/plugins/vault/plugin.go (L1148-1187)
```go
func (r *ReportingPlugin) processListSecretIdentifiersRequest(ctx context.Context, seqNr uint64, requestID string, reader ReadKVStore, req *vaultcommon.ListSecretIdentifiersRequest) (*vaultcommon.ListSecretIdentifiersResponse, error) {
	if err := r.validateListSecretIdentifiersOwnerNonempty(req); err != nil {
		return nil, err
	}

	md, err := reader.GetMetadata(ctx, req.Owner)
	if err != nil {
		return nil, fmt.Errorf("failed to get metadata for owner: %w", err)
	}

	if md == nil {
		// No metadata, so the list is empty.
		// The user hasn't added any items to the vault DON yet.
		r.typedRequestLggr(seqNr, requestID, "ListSecretIdentifiers").With("owner", req.Owner).Debugw("successfully read metadata for owner: no metadata found, returning empty list")
		return &vaultcommon.ListSecretIdentifiersResponse{Identifiers: []*vaultcommon.SecretIdentifier{}, Success: true}, nil
	}

	sort.Slice(md.SecretIdentifiers, func(i, j int) bool {
		if md.SecretIdentifiers[i].Namespace == md.SecretIdentifiers[j].Namespace {
			return md.SecretIdentifiers[i].Key < md.SecretIdentifiers[j].Key
		}
		return md.SecretIdentifiers[i].Namespace < md.SecretIdentifiers[j].Namespace
	})

	if req.Namespace == "" {
		return &vaultcommon.ListSecretIdentifiersResponse{Identifiers: md.SecretIdentifiers, Success: true}, nil
	}

	si := []*vaultcommon.SecretIdentifier{}
	for _, id := range md.SecretIdentifiers {
		if id.Namespace == req.Namespace {
			si = append(si, id)
		}
	}

	return &vaultcommon.ListSecretIdentifiersResponse{
		Identifiers: si,
		Success:     true,
	}, nil
}
```

**File:** core/services/ocr2/plugins/vault/request_validation.go (L211-218)
```go
func (r *ReportingPlugin) validateListSecretIdentifiersOwnerWire(ctx context.Context, req *vaultcommon.ListSecretIdentifiersRequest) error {
	return r.validator.ValidateSecretIdentifier(ctx, req.Owner, req.Owner, req.Namespace)
}

func (r *ReportingPlugin) validateListSecretIdentifiersResponseSize(ctx context.Context, owner string, identifierCount int) error {
	innerCtx := contexts.WithCRE(ctx, contexts.CRE{Owner: owner})
	return r.cfg.MaxSecretsPerOwner.Check(innerCtx, identifierCount)
}
```

**File:** core/services/ocr2/plugins/vault/contribution_validation.go (L256-284)
```go
func (r *ReportingPlugin) validateListSecretIdentifiersContribution(ctx context.Context, req *vaultcommon.ListSecretIdentifiersRequest, o *vaultcommon.Observation) error {
	if embedded := o.GetListSecretIdentifiersRequest(); embedded != nil && !proto.Equal(embedded, req) {
		return errors.New("embedded ListSecretIdentifiers request does not match pending queue request")
	}

	resp := o.GetListSecretIdentifiersResponse()
	if resp == nil {
		return errors.New("ListSecretIdentifiers observation must have a response")
	}

	if !resp.Success {
		if resp.GetError() != "" {
			return fmt.Errorf("%s", resp.GetError())
		}
		return errors.New("ListSecretIdentifiers observation failed")
	}

	if err := r.validateListSecretIdentifiersOwnerWire(ctx, req); err != nil {
		return fmt.Errorf("ListSecretIdentifiers request contains invalid secret identifier: %w", err)
	}

	if err := r.validateListSecretIdentifiersResponseSize(ctx, req.Owner, len(resp.Identifiers)); err != nil {
		if errBoundLimited, ok := errors.AsType[limits.ErrorBoundLimited[int]](err); ok {
			return fmt.Errorf("ListSecretIdentifiers response exceeds maximum number of secrets per owner (have=%d, limit=%d): %w", len(resp.Identifiers), errBoundLimited.Limit, err)
		}
		return fmt.Errorf("failed to check max secrets per owner limit: %w", err)
	}

	return nil
```

**File:** core/capabilities/vault/validator.go (L180-252)
```go
func (r *RequestValidator) ValidateGetSecretsRequest(ctx context.Context, request *vaultcommon.GetSecretsRequest) error {
	if len(request.Requests) == 0 {
		return errors.New("no GetSecret request specified in request")
	}
	if len(request.Requests) >= vaulttypes.MaxBatchSize {
		return fmt.Errorf("request batch size exceeds maximum of %d", vaulttypes.MaxBatchSize)
	}

	uniqueIDs := map[string]bool{}
	for idx, req := range request.Requests {
		if req.Id == nil {
			return errors.New("secret ID must have id set at index " + strconv.Itoa(idx))
		}
		if req.Id.Key == "" {
			return errors.New("secret ID must have key set at index " + strconv.Itoa(idx) + ": " + req.Id.String())
		}
		if err := r.ValidateSecretIdentifier(ctx, req.Id.Key, req.Id.Owner, req.Id.Namespace); err != nil {
			return fmt.Errorf("invalid secret identifier at index %d: %w", idx, err)
		}

		_, ok := uniqueIDs[vaulttypes.KeyFor(req.Id)]
		if ok {
			return errors.New("duplicate secret ID found at index " + strconv.Itoa(idx) + ": " + req.Id.String())
		}

		uniqueIDs[vaulttypes.KeyFor(req.Id)] = true
	}

	return nil
}

func (r *RequestValidator) ValidateListSecretIdentifiersRequest(ctx context.Context, request *vaultcommon.ListSecretIdentifiersRequest) error {
	if request.RequestId == "" || request.Owner == "" {
		return errors.New("requestID or owner must not be empty")
	}
	if err := r.ValidateSecretIdentifier(ctx, request.Owner, request.Owner, request.Namespace); err != nil {
		return fmt.Errorf("invalid secret identifier: %w", err)
	}
	return nil
}

func (r *RequestValidator) ValidateDeleteSecretsRequest(ctx context.Context, request *vaultcommon.DeleteSecretsRequest) error {
	if request.RequestId == "" {
		return errors.New("request ID must not be empty")
	}
	if err := r.MaxRequestBatchSizeLimiter.Check(ctx, len(request.Ids)); err != nil {
		if errBoundLimited, ok := errors.AsType[limits.ErrorBoundLimited[int]](err); ok {
			return fmt.Errorf("request batch size exceeds maximum of %d: %w", errBoundLimited.Limit, err)
		}
		return fmt.Errorf("failed to check request batch size limit: %w", err)
	}
	if len(request.Ids) == 0 {
		return errors.New("request batch must contain at least 1 item")
	}

	uniqueIDs := map[string]bool{}
	for idx, id := range request.Ids {
		if id == nil {
			return errors.New("secret ID must not be nil at index " + strconv.Itoa(idx))
		}
		if err := r.ValidateSecretIdentifier(ctx, id.Key, id.Owner, id.Namespace); err != nil {
			return fmt.Errorf("invalid secret identifier at index %d: %w", idx, err)
		}

		_, ok := uniqueIDs[vaulttypes.KeyFor(id)]
		if ok {
			return errors.New("duplicate secret ID found at index " + strconv.Itoa(idx) + ": " + id.String())
		}

		uniqueIDs[vaulttypes.KeyFor(id)] = true
	}
	return nil
}
```
