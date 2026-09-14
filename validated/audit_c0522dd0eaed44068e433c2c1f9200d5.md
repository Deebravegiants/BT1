## Finding: Cross-tenant secret deletion via unvalidated `Owner` field in `DeleteSecretsRequest`

### Summary
For `MethodSecretsList`, the node-side handler explicitly overwrites the requested owner with the authenticated owner before calling the secrets service: `r.Owner = authResult.AuthorizedOwner()` [1](#0-0) . For `MethodSecretsDelete`, no equivalent step exists — `handleSecretsDelete` unmarshals the raw request and passes it straight to `h.secretsService.DeleteSecrets(ctx, r)` without ever consulting the `AuthResult` [2](#0-1) .

### Finding Description
The gateway/node vault pipeline authorizes a request by matching its **digest** against an allow-listed `(owner, digest, expiry)` tuple from the workflow registry [3](#0-2) . This proves that *some* authorized owner permitted *this exact request bytes* to run — it does not, by itself, guarantee that the `Owner` field(s) embedded inside `DeleteSecretsRequest.Ids` match the `AuthorizedOwner()` returned by the authorizer.

`GatewayVaultRequestProcessor.processDeleteSecretsRequest` unmarshals `DeleteSecretsRequest`, runs `ValidateDeleteSecretsRequest` (structural validation only), then calls `authorizeAndStamp`, which authorizes the request and stamps the owner-prefixed `RequestId` — but never rewrites or checks `deleteReq.Ids[i].Owner` against `authResult.AuthorizedOwner()` [4](#0-3) . Compare this to `processCreateSecretsRequest`/`processUpdateSecretsRequest`, which at least run `ValidateCiphertextSizes` scoped by `authorized.AuthResult.AuthorizedOwner()` [5](#0-4) , and `processListSecretIdentifiersRequest`, whose result is force-scoped to `AuthorizedOwner()` on the node side.

On the node side, `HandleGatewayMessage` routes `MethodSecretsDelete` through the same processor and obtains an `authResult`, but that result is discarded for `handleSecretsDelete` — it is only forwarded into `handleSecretsList` [6](#0-5) . As a result, whatever `Owner` value is embedded inside the (attacker/workflow-owner supplied) `DeleteSecretsRequest.Ids` is passed as-is to `secretsService.DeleteSecrets`.

This is analogous to the Stars Arena bug class described in the report: an attacker-controlled value (there, a block height inserted as an AVAX amount in `sellShares()`; here, an arbitrary `Owner` field inside `DeleteSecretsRequest.Ids`) is trusted and used directly in a state-mutating operation instead of being derived from/validated against the already-authenticated principal.

### Impact Explanation
If the underlying `SecretsService.DeleteSecrets` implementation does not itself re-validate `Ids[].Owner` against the digest-authorized owner (this repo's index does not show that check happening inside the OCR2 vault plugin/report-observation path either — `observeGetSecrets` reads by `vaulttypes.KeyFor(sr.Id)` without visible owner re-derivation [7](#0-6) ), a workflow owner who obtains one allow-listed digest for a `SecretsDelete` request could submit `Ids` whose `Owner` field references a *different* tenant's namespace, deleting another owner's secrets — a cross-tenant deletion / owner-scope bypass.

### Likelihood Explanation
Reaching this path only requires an unprivileged workflow owner who can get **any** valid `SecretsDelete` request allow-listed for their own address (a normal part of the vault workflow) and then crafts the JSON-RPC params with a different `Owner`/`Namespace` in one or more `SecretIdentifier` entries before submission — the allowlist digest matches on request bytes and expiry, not on cross-checking the payload's internal `Owner` fields against the resolved `AuthorizedOwner()`. This is fully reachable from an unprivileged client via the internet-facing gateway (`HandleJSONRPCUserMessage` → `GatewayVaultRequestProcessor.ProcessRequest`).

### Recommendation
- In `processDeleteSecretsRequest` (and any other write/read path taking `SecretIdentifier`/`Owner` fields), after `authorizeAndStamp` returns, validate (or forcibly overwrite, as is done for List) every `Ids[i].Owner` against `authorized.AuthResult.AuthorizedOwner()`, rejecting or rewriting mismatches before calling the secrets service.
- Audit `SecretsService.DeleteSecrets`/`GetSecrets`/`CreateSecrets`/`UpdateSecrets` implementations to confirm whether they independently enforce owner scoping; if not, add that enforcement centrally in the processor rather than relying on each call site.
- Add a regression test mirroring the existing List owner-scoping test that asserts `DeleteSecretsRequest.Ids[].Owner` cannot diverge from `AuthorizedOwner()`.

### Proof of Concept
1. Workflow owner `0xAAA` gets a `SecretsDelete` JSON-RPC request digest allow-listed on the workflow registry for their own address (normal flow, e.g. via `AllowlistRequest`) — see the allowlisting mechanism used in tests [8](#0-7) .
2. Owner `0xAAA` crafts the exact allow-listed request bytes, but sets `Ids: [{Owner: "0xBBB", Namespace: "ns", Key: "victim-secret"}]`.
3. Gateway/node authorizer matches the digest and expiry (both depend only on request bytes/method, not on payload owner semantics) and returns `AuthResult{AuthorizedOwner: "0xAAA", ...}`.
4. `processDeleteSecretsRequest` stamps the request ID with `0xAAA::` prefix but leaves `deleteReq.Ids[0].Owner == "0xBBB"` untouched [4](#0-3) .
5. `GatewayHandler.handleSecretsDelete` forwards the unmodified request straight to `secretsService.DeleteSecrets` [2](#0-1) , deleting `0xBBB`'s secret.

**Uncertainty / limitation:** I could not confirm from the indexed code whether the internal `SecretsService.DeleteSecrets` implementation (OCR2 vault plugin / DKG-backed storage) independently re-derives/enforces ownership from `AuthResult` before performing the delete — the relevant plugin code (`core/services/ocr2/plugins/vault/plugin.go`) shows the `GetSecrets` observation path but not the delete-path owner check, and full contents of that file were not available in the index. If such enforcement exists deeper in the pipeline, the practical impact is reduced to defense-in-depth; if it does not, this is a directly exploitable cross-tenant deletion. Confirming this requires reviewing the full `SecretsService` implementation, which would need a Devin session with complete file access.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L200-222)
```go
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

	if response == nil {
		switch req.Method {
		case vaulttypes.MethodSecretsCreate:
			response = h.handleSecretsCreate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsUpdate:
			response = h.handleSecretsUpdate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsDelete:
			response = h.handleSecretsDelete(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsList:
			response = h.handleSecretsList(ctx, gatewayID, req, authResult)
```

**File:** core/capabilities/vault/gw_handler.go (L313-336)
```go
func (h *GatewayHandler) handleSecretsDelete(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.DeleteSecretsRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized delete secrets request", "request", r.String())
	resp, err := h.secretsService.DeleteSecrets(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to delete secrets: %w", err))
	}

	resultBytes, err := resp.ToJSONRPCResult()
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}

	return &jsonrpc.Response[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      req.ID,
		Method:  req.Method,
		Result:  (*json.RawMessage)(&resultBytes),
	}
}
```

**File:** core/capabilities/vault/gw_handler.go (L338-343)
```go
func (h *GatewayHandler) handleSecretsList(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage], authResult *AuthResult) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.ListSecretIdentifiersRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
	r.Owner = authResult.AuthorizedOwner()
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L32-76)
```go
// AuthorizeRequest authorizes a request using AllowListBasedAuth.
// It does NOT check if the request method is allowed.
func (r *allowListBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	r.lggr.Debugw("AllowListBasedAuth authorizing request", "method", req.Method, "requestID", req.ID)
	requestDigest, err := req.Digest()
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to create digest", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to decode digest", "method", req.Method, "requestID", req.ID, "requestDigest", requestDigest, "error", err)
		return nil, err
	}
	requestDigestBytes32 := [32]byte(requestDigestBytes)
	if r.workflowRegistrySyncer == nil {
		r.lggr.Errorw("AllowListBasedAuth workflowRegistrySyncer is nil", "method", req.Method, "requestID", req.ID)
		return nil, errors.New("internal error: workflowRegistrySyncer is nil")
	}
	allowlistedRequest, allowedRequestsStrs, err := r.findAllowlistedItemWithRetry(ctx, req, requestDigest, requestDigestBytes32)
	if err != nil {
		return nil, err
	}
	if allowlistedRequest == nil {
		r.lggr.Debugw("AllowListBasedAuth request digest not allowlisted",
			"method", req.Method,
			"requestID", req.ID,
			"digestHexStr", requestDigest,
			"allowedRequestsStrs", allowedRequestsStrs)
		return nil, errors.New("request not allowlisted")
	}

	if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
		authorizedRequestStr := string(allowlistedRequest.RequestDigest[:])
		r.lggr.Debugw("AllowListBasedAuth authorization expired", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", authorizedRequestStr, "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
		return nil, errors.New("request authorization expired")
	}

	digestKey := string(allowlistedRequest.RequestDigest[:])
	r.lggr.Debugw("AllowListBasedAuth authorization succeeded", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", digestKey, "owner", allowlistedRequest.Owner.Hex(), "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
	return &AuthResult{
		workflowOwner: allowlistedRequest.Owner.Hex(),
		digest:        digestKey,
		expiresAt:     int64(allowlistedRequest.ExpiryTimestamp),
	}, nil
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L146-148)
```go
	if err := p.validator.ValidateCiphertextSizes(ctx, authorized.AuthResult.AuthorizedOwner(), createReq.EncryptedSecrets); err != nil {
		return nil, p.validationError(req, err)
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L194-224)
```go
func (p *GatewayVaultRequestProcessor) processDeleteSecretsRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}

	var deleteReq vaultcommon.DeleteSecretsRequest
	if err := json.Unmarshal(*req.Params, &deleteReq); err != nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: err}
	}
	if p.stripOwnerPrefixForAuth {
		deleteReq.RequestId = req.ID
		if err := marshalVaultParams(req, &deleteReq); err != nil {
			return nil, InvalidVaultParamsError{Method: req.Method, Err: err}
		}
	} else {
		deleteReq.RequestId = coalesceRequestID(deleteReq.RequestId, req.ID)
	}

	if err := p.validator.ValidateDeleteSecretsRequest(ctx, &deleteReq); err != nil {
		return nil, p.validationError(req, err)
	}

	return p.authorizeAndStamp(ctx, req, func(prefixedRequestID string) error {
		deleteReq.RequestId = prefixedRequestID
		vaultutils.ApplySecretIdentifierNamespaceDefaults(deleteReq.Ids)
		return marshalVaultParams(req, &deleteReq)
	})
}
```

**File:** core/services/ocr2/plugins/vault/plugin.go (L909-927)
```go
func (r *ReportingPlugin) observeGetSecrets(ctx context.Context, seqNr uint64, requestID string, reader ReadKVStore, req proto.Message, o *vaultcommon.Observation) {
	l := r.typedRequestLggr(seqNr, requestID, "GetSecrets")
	tp := req.(*vaultcommon.GetSecretsRequest)
	o.RequestType = vaultcommon.RequestType_GET_SECRETS

	requestsCountForID := map[string]int{}
	for _, sr := range tp.Requests {
		var key string
		if sr.Id == nil {
			key = "<nil>"
		} else {
			key = vaulttypes.KeyFor(sr.Id)
		}
		requestsCountForID[key]++
	}

	resps := []*vaultcommon.SecretResponse{}
	for _, secretRequest := range tp.Requests {
		resp, ierr := r.observeGetSecretsRequest(ctx, reader, secretRequest, requestsCountForID)
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
