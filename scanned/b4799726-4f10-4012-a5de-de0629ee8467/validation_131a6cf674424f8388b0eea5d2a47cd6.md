## Finding

An unprivileged attacker can pre-empt (race and consume) another workflow owner's single-use, on-chain-allowlisted Vault request before the legitimate caller submits it, permanently denying that specific action — a "disable the function" analog to the reported Teller bug, where anyone could call an unguarded function to defeat another party's authorized-but-not-yet-executed action.

### Title
Unauthenticated request-digest front-running permanently consumes another owner's allowlisted Vault authorization (DoS) - (File: core/capabilities/vault/allow_list_based_auth.go)

### Summary
The Vault gateway's allowlist-based authentication authorizes a JSON-RPC request purely by matching its content digest against an on-chain allowlist entry — it never verifies that the submitter is the workflow owner who registered that allowlist entry. Combined with a single global, first-writer-wins replay guard, any unauthenticated third party who can reconstruct the exact plaintext of an allowlisted request can submit it to the gateway first and permanently burn the owner's one-time authorization, exactly like the reported bug where anyone could call an access-control-free `withdraw` to pre-empt/disable the legitimate liquidation flow.

### Finding Description
`allowListBasedAuth.AuthorizeRequest` computes a digest of the incoming request and checks only whether that digest exists in the on-chain `WorkflowRegistryOwnerAllowlistedRequest` set — it performs no signature check or sender-identity check at all: [1](#0-0) 

The authorization result is then fed into a global `RequestReplayGuard` that is keyed solely by digest, with no binding to who submitted it — the first caller to present the matching digest "wins" and the entry is marked seen: [2](#0-1) [3](#0-2) 

The allowlist entry itself is created by an on-chain transaction (`WorkflowRegistry.AllowlistRequest`), which is publicly readable by anyone via the registry's `GetAllowlistedRequests` view / event stream, exactly as done by the workflow owner tooling itself: [4](#0-3) 

For `vault.secrets.list` and `vault.secrets.delete`, the entire request body (owner address, namespace, key, request ID) is sent as plaintext — no ciphertext is required to construct these requests, and owner-scoped identifiers are validated only *after* authorization succeeds: [5](#0-4) 

Because the digest is a hash of exactly this plaintext (method + id + params), any attacker who already knows or can guess the owner's plaintext request (e.g., a `SecretsDelete` for a secret whose namespace/key names are conventional or previously observed in a `SecretsList` response, with a predictable `request_id`) can reconstruct the identical JSON-RPC request byte-for-byte, and race it to the gateway before the legitimate owner does. Since the gateway path has no per-caller authentication requirement for this flow (`req.Auth == ""` uses the allowlist path, documented as "existing clients do not populate the auth field yet"): [6](#0-5) 

...the attacker's forged submission is accepted, consumes the single-use allowlist entry via the replay guard, and the legitimate owner's subsequent (correct, intended) submission of the very same request is rejected with `ErrRequestAlreadySeen`, permanently preventing that authorized action (e.g., deleting/rotating a specific secret) from ever executing, since the on-chain allowlist entry cannot be resubmitted with a fresh expiry without owner action, and the window is single-use per digest.

### Impact Explanation
This lets an unprivileged, unauthenticated actor deny a workflow owner's legitimate, previously-authorized Vault operation (e.g., a scheduled secret rotation/delete), causing operational disruption to CRE workflows relying on Vault secret lifecycle management — directly analogous in effect (front-running to defeat a legitimate, time-windowed privileged action) to disabling the liquidation function in the source report.

### Likelihood Explanation
Exploitability depends on the attacker being able to reconstruct the exact plaintext request that matches a specific on-chain digest. For `vault.secrets.list`/`vault.secrets.delete`, the params are unencrypted and often predictable (well-known owner address, default namespace `"main"`, previously enumerated secret keys via `ListSecretIdentifiers`, and workflow-generated `request_id` conventions), making this feasible in realistic CRE deployments where workflow secret naming and IDs follow observable patterns; it is lower-likelihood against `vault.secrets.create`/`update` because ciphertext is required.

### Recommendation
Bind the on-chain allowlist authorization to sender identity — e.g., require the caller to additionally prove control of the workflow owner key (signature over the request) rather than relying solely on digest possession, or make replay-guard consumption owner-scoped and reversible/re-allowlistable by the true owner, so a race by a non-owner cannot burn the legitimate owner's authorization window.

### Proof of Concept
1. Workflow owner calls `WorkflowRegistry.AllowlistRequest(digest, expiry)` on-chain for an intended `vault.secrets.delete` request (owner address, namespace `"main"`, key `"api-key"`, `request_id="rotate-1"`).
2. Attacker monitors the public `WorkflowRegistry` contract/events and independently reconstructs the identical plaintext JSON-RPC request (owner address is public, namespace/key are conventional/previously observed via a `vault.secrets.list` call).
3. Attacker computes the same digest locally and POSTs the reconstructed request to the vault gateway before the legitimate owner's client does.
4. `allowListBasedAuth.AuthorizeRequest` matches the digest and authorizes it; `RequestReplayGuard.CheckAndRecord` marks the digest as seen.
5. The legitimate owner's subsequent submission of the real request is rejected with `ErrRequestAlreadySeen`, and the owner cannot delete/rotate the secret using that authorization window, matching the "attacker disables a legitimate function by racing an unprotected/unauthenticated path" pattern from the source report.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L34-62)
```go
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
```

**File:** core/capabilities/vault/authorizer.go (L99-119)
```go
func (a *authorizer) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	authResult, err := a.authorizeRequest(ctx, req)
	if err != nil {
		return nil, err
	}
	if authResult == nil {
		err = errors.New("auth mechanism returned nil auth result")
		a.lggr.Errorw("auth mechanism returned nil auth result", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "")
		return nil, err
	}
	if err := a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt()); err != nil {
		a.lggr.Debugw("replay guard rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "", "error", err)
		return nil, err
	}
	if ownerErr := validateSecretOwnersMatchAuthorized(req, authResult.AuthorizedOwner()); ownerErr != nil {
		a.lggr.Errorw("owner binding rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "hasAuth", req.Auth != "", "error", ownerErr)
		return nil, ownerErr
	}
	a.lggr.Debugw("request authorized", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "")
	return authResult, nil
}
```

**File:** core/capabilities/vault/authorizer.go (L121-127)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
```

**File:** core/capabilities/vault/authorizer.go (L173-196)
```go
	case vaulttypes.MethodSecretsDelete:
		if req.Params == nil {
			return errors.New("request params must not be nil")
		}
		var deleteReq vaultcommon.DeleteSecretsRequest
		if err := json.Unmarshal(*req.Params, &deleteReq); err != nil {
			return err
		}
		return validateSecretIdentifierOwnerMismatch(deleteReq.Ids, workflowOwner)
	case vaulttypes.MethodSecretsList:
		if req.Params == nil {
			return errors.New("request params must not be nil")
		}
		var listReq vaultcommon.ListSecretIdentifiersRequest
		if err := json.Unmarshal(*req.Params, &listReq); err != nil {
			return err
		}
		if vaultutils.NormalizeOwner(listReq.Owner) != vaultutils.NormalizeOwner(workflowOwner) {
			return fmt.Errorf("list secrets owner %q does not match authorized workflow owner %q", listReq.Owner, workflowOwner)
		}
		return nil
	default:
		return fmt.Errorf("owner validation not implemented for method %q", req.Method)
	}
```

**File:** core/capabilities/vault/request_replay_guard.go (L35-47)
```go
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
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
