### Title
Off-by-one in allowlisted request expiry check permits authorization exactly one second past intended expiry - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
`allowListBasedAuth.AuthorizeRequest` rejects a pre-approved (allowlisted) Vault request only when the current time is *strictly greater than* the allowlisted digest's `ExpiryTimestamp`. This mirrors exactly the reported Hubble `InsuranceFund` bug class: a boundary comparison that should exclude the expiry instant but instead includes it, letting the privileged action succeed at `now == expiry`.

### Finding Description
The allowlist-based authorizer used by the Vault gateway handler validates that an unprivileged, internet-facing JSON-RPC request digest matches a workflow-registry-approved entry and has not expired:

```go
if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
    ...
    return nil, errors.New("request authorization expired")
}
``` [1](#0-0) 

This is a strict `>` check, so a request whose `time.Now().UTC().Unix() == ExpiryTimestamp` is treated as still valid and is authorized:

```go
return &AuthResult{
    workflowOwner: allowlistedRequest.Owner.Hex(),
    digest:        digestKey,
    expiresAt:     int64(allowlistedRequest.ExpiryTimestamp),
}, nil
``` [2](#0-1) 

The test suite for this authorizer only exercises `now == expiry+100` (valid) and `now == expiry-1` for the "expired" case (i.e., the entry's expiry is set to `time.Now()-1`), never exercising the exact boundary `now == expiry`:

```go
allowlisted[0].ExpiryTimestamp = uint32(time.Now().UTC().Unix() - 1)
...
require.ErrorContains(t, err, "authorization expired")
``` [3](#0-2) 

confirming the exact-equality boundary is untested and unguarded, structurally identical to the original Solidity finding's `currentTimestamp <= expiryTime` boundary bug.

### Impact Explanation
`AllowListBasedAuth.AuthorizeRequest` is the authorization gate for Vault capability requests arriving over the gateway from unprivileged workflow-owner clients (secrets create/list/delete, etc., as seen in `gw_handler_test.go`, e.g. `TestGatewayHandler_CreateUpdateReusesCachedPublicKey`) [4](#0-3) . It is the mechanism by which a specific pre-approved request digest, tied to a fixed expiry set by the on-chain workflow registry, is allowed to execute exactly once (replay protection is handled separately by `RequestReplayGuard`). Because the expiry check uses `>` rather than `>=`, a workflow-owner-approved action remains executable for one full second beyond its intended cutoff. This is a genuine authorization-boundary flaw of the exact same class as the audit finding (using a stale/expiring authorization to perform an action that should have been rejected), though its window is fixed at ~1 second (Unix-second granularity) rather than being attacker-controlled or unbounded, and it does not by itself enable free extraction of value the way the auction's `_getAuctionPrice()` returning 0 did.

### Likelihood Explanation
Exploitability is low-to-moderate: an attacker (or the legitimate but no-longer-authorized caller) would need to time a request so that it lands in the single Unix-second where `now == ExpiryTimestamp`, which is a very narrow, non-attacker-controllable window in most cases and requires network/clock timing luck rather than being deterministically triggerable like the original Solidity bug (where the attacker could simply wait until the exact expiry block timestamp, which is trivial in a deterministic block-time context). This makes the practical likelihood of hitting the boundary low, though the logical flaw itself is real and reachable from an unprivileged actor via the gateway/Vault authorization path.

### Recommendation
Change the comparison in `AuthorizeRequest` to treat the expiry instant itself as expired, consistent with the recommended fix pattern in the original report:
```go
if time.Now().UTC().Unix() >= int64(allowlistedRequest.ExpiryTimestamp) {
    return nil, errors.New("request authorization expired")
}
```
Add an explicit unit test asserting `now == ExpiryTimestamp` is rejected, mirroring the recommended fix from the original report (`currentTimestamp < expiryTime` instead of `<=`).

### Proof of Concept
1. A workflow owner obtains (via the on-chain `WorkflowRegistry`) an allowlisted request digest with `ExpiryTimestamp = T`.
2. The workflow owner (or anyone who can reconstruct/replay the exact request before replay-guard consumption) sends the corresponding JSON-RPC request to the gateway at the instant `time.Now().UTC().Unix() == T`.
3. `AllowListBasedAuth.AuthorizeRequest` evaluates `T > T` → `false`, so the expiry branch is skipped and the request is authorized as if it were still within its valid window, one second past when it was supposed to have been denied.
4. This is demonstrable by amending `TestAllowListBasedAuth_ListSecrets`'s expired-request sub-case to set `allowlisted[0].ExpiryTimestamp = uint32(time.Now().UTC().Unix())` and observing `AuthorizeRequest` returns `nil` error (success) instead of `"authorization expired"`, based on the same code path exercised by [5](#0-4) .

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L64-68)
```go
	if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
		authorizedRequestStr := string(allowlistedRequest.RequestDigest[:])
		r.lggr.Debugw("AllowListBasedAuth authorization expired", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", authorizedRequestStr, "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
		return nil, errors.New("request authorization expired")
	}
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L70-76)
```go
	digestKey := string(allowlistedRequest.RequestDigest[:])
	r.lggr.Debugw("AllowListBasedAuth authorization succeeded", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", digestKey, "owner", allowlistedRequest.Owner.Hex(), "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
	return &AuthResult{
		workflowOwner: allowlistedRequest.Owner.Hex(),
		digest:        digestKey,
		expiresAt:     int64(allowlistedRequest.ExpiryTimestamp),
	}, nil
```

**File:** core/capabilities/vault/allow_list_based_auth_test.go (L191-203)
```go
	// Expired request
	allowlistedReqCopy := allowlistedRequest
	allowlistedReqCopy.ID = "456"
	allowlistedReqCopyDigest, err := allowlistedReqCopy.Digest()
	require.NoError(t, err)
	allowlistedReqCopyDigestBytes, err := hex.DecodeString(allowlistedReqCopyDigest)
	require.NoError(t, err)
	allowlisted[0].RequestDigest = [32]byte(allowlistedReqCopyDigestBytes)
	allowlisted[0].ExpiryTimestamp = uint32(time.Now().UTC().Unix() - 1) //nolint:gosec // it is a safe conversion
	mockSyncer.On("GetAllowlistedRequests", mock.Anything).Return(allowlisted)
	authResult, err = auth.AuthorizeRequest(t.Context(), allowlistedReqCopy)
	require.Nil(t, authResult)
	require.ErrorContains(t, err, "authorization expired")
```

**File:** core/capabilities/vault/gw_handler_test.go (L784-837)
```go
func TestGatewayHandler_CreateUpdateReusesCachedPublicKey(t *testing.T) {
	t.Parallel()

	lggr := logger.TestLogger(t)
	ctx := t.Context()

	secretsService := vaulttypesmocks.NewSecretsService(t)
	gwConnector := connector_mocks.NewGatewayConnector(t)
	allowListBasedAuth := vaultcapmocks.NewAuthorizer(t)

	pk, pkHex := testMasterPublicKey(t)
	secretsService.EXPECT().GetPublicKey(mock.Anything, mock.Anything).
		Return(&vaultcommon.GetPublicKeyResponse{PublicKey: pkHex}, nil).Once()

	handler, err := vaultcap.NewGatewayHandler(
		secretsService,
		gwConnector,
		nil,
		lggr,
		limits.Factory{Settings: cresettings.DefaultGetter},
		vaultcap.NewAuthorizer(allowListBasedAuth, nil, lggr),
		nil,
	)
	require.NoError(t, err)

	makeCreateRequest := func(id string) *jsonrpc.Request[json.RawMessage] {
		params, err := json.Marshal(vaultcommon.CreateSecretsRequest{
			EncryptedSecrets: []*vaultcommon.EncryptedSecret{{
				Id:             &vaultcommon.SecretIdentifier{Key: "test_secret", Owner: "0xAbC"},
				EncryptedValue: encryptSecretForOwner(t, pk, "0xAbC"),
			}},
		})
		require.NoError(t, err)
		raw := json.RawMessage(params)
		return &jsonrpc.Request[json.RawMessage]{
			Method: vaulttypes.MethodSecretsCreate,
			ID:     id,
			Params: &raw,
		}
	}

	for i, id := range []string{"1", "2"} {
		authResult := vaultcap.NewAuthResult("", "0xabc", "digest-"+id, time.Now().Add(time.Minute).Unix())
		allowListBasedAuth.EXPECT().AuthorizeRequest(mock.Anything, mock.MatchedBy(func(req jsonrpc.Request[json.RawMessage]) bool {
			return req.Method == vaulttypes.MethodSecretsCreate && req.ID == id
		})).Return(authResult, nil).Once()
		secretsService.EXPECT().CreateSecrets(mock.Anything, mock.Anything).
			Return(&vaulttypes.Response{ID: "test_secret"}, nil).Once()
		gwConnector.On("SendToGateway", mock.Anything, "gateway-1", mock.MatchedBy(func(resp *jsonrpc.Response[json.RawMessage]) bool {
			return resp.Error == nil
		})).Return(nil).Once()

		require.NoError(t, handler.HandleGatewayMessage(ctx, "gateway-1", makeCreateRequest(id)), "request %d", i+1)
	}
```
