## Analysis

The reported bug class is a boundary-condition mistake in a timestamp expiry check: using `>` where `>=` is correct, causing the exact expiry instant to be treated as still valid. The strongest reachable analog in an unprivileged-actor authentication path is the Vault `AllowListBasedAuth.AuthorizeRequest` expiry check.

### Title
Off-by-one boundary allows Vault allowlisted-request authorization to remain valid at the exact expiry second - (File: core/capabilities/vault/allow_list_based_auth.go)

### Summary
`allowListBasedAuth.AuthorizeRequest` rejects a request as expired only when `time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp)`, meaning at `now == ExpiryTimestamp` the request is still treated as authorized instead of expired.

### Finding Description
The authorization check is:
```go
if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
    ...
    return nil, errors.New("request authorization expired")
}
``` [1](#0-0) 

This is reachable from any unprivileged client sending a Vault gateway request (`vault.secrets.create`/`update`/`delete`/`list`), whose authorization is resolved through `AuthorizeRequest`, which is invoked from the generic `authorizer.authorizeAllowListBasedAuth` path. [2](#0-1) 

The logically-correct boundary is `now >= ExpiryTimestamp` implies expired (i.e., valid iff `now < ExpiryTimestamp`), matching the report's recommended fix pattern (`>=` instead of `>`). With the current `>` comparison, a request whose `ExpiryTimestamp` equals the current second is still authorized for that entire second, granting exactly one extra second of validity beyond the intended allowlist window set on-chain via `WorkflowRegistry.AllowlistRequest`. [3](#0-2) 

### Impact Explanation
Low — the extra window is bounded to at most one second (the same second in which `ExpiryTimestamp` falls), consistent with the original report's classification of the analogous bug as Low/QA rather than Medium: the surrounding logic (allowlist entry existing, digest matching) already constrains what can be authorized during that extra second, so the impact is a minor unintended widening of the trusted request window rather than a full bypass.

### Likelihood Explanation
Low-to-Medium — it triggers deterministically whenever a request is processed in exactly the same unix second as its configured `ExpiryTimestamp`, which is a narrow but reachable timing window for any unprivileged workflow owner whose request was allowlisted with a short-lived expiry.

### Recommendation
Change the comparison from strictly-greater-than to greater-than-or-equal so that the boundary second is treated as expired:
```diff
-       if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
+       if time.Now().UTC().Unix() >= int64(allowlistedRequest.ExpiryTimestamp) {
``` [4](#0-3) 

### Proof of Concept
1. On-chain, call `WorkflowRegistry.AllowlistRequest(digest, expiry)` with `expiry = now + N` seconds.
2. Wait until `time.Now().UTC().Unix() == expiry` exactly (the same second).
3. Send the allowlisted Vault gateway request at that instant; `AuthorizeRequest` computes `time.Now().UTC().Unix() > expiry` which is `false` (equal, not greater), so the request is authorized even though it is at/past its intended expiry boundary, matching the reported off-by-one class (`<=` used where `<` was intended).

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L64-68)
```go
	if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
		authorizedRequestStr := string(allowlistedRequest.RequestDigest[:])
		r.lggr.Debugw("AllowListBasedAuth authorization expired", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", authorizedRequestStr, "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
		return nil, errors.New("request authorization expired")
	}
```

**File:** core/capabilities/vault/authorizer.go (L130-137)
```go
func (a *authorizer) authorizeAllowListBasedAuth(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	if a.allowListBasedAuth == nil {
		err := errors.New("AllowListBasedAuth authorizer is nil")
		a.lggr.Errorw("AllowListBasedAuth unavailable", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	return a.allowListBasedAuth.AuthorizeRequest(ctx, req)
}
```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L1510-1517)
```go
func allowlistRequest(t *testing.T, owner string, request jsonrpc.Request[json.RawMessage], sethClient *seth.Client, wfRegistryContract *workflow_registry_v2_wrapper.WorkflowRegistry) {
	requestDigest, err := request.Digest()
	require.NoError(t, err, "failed to get digest for request")
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	require.NoError(t, err, "failed to decode digest")
	reqDigestBytes := [32]byte(requestDigestBytes)
	_, err = wfRegistryContract.AllowlistRequest(sethClient.NewTXOpts(), reqDigestBytes, uint32(time.Now().Add(1*time.Hour).Unix())) //nolint:gosec // disable G115
	require.NoError(t, err, "failed to allowlist request")
```
