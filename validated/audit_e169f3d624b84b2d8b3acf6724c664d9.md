### Title
Request impersonation via public-digest-only authorization in AllowListBasedAuth (Vault gateway) - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
The Vault DON's `AllowListBasedAuth.AuthorizeRequest` grants a caller the identity of a workflow owner solely by matching a `Digest()` computed from **public** request content (method + params) against a publicly-queryable on-chain allowlist. No signature over the submitted bytes, and no secret bound to the caller, is ever checked in this path. Anyone who can reproduce or capture the exact plaintext request that a legitimate owner intends to submit can send it to the gateway first and be authorized as that owner — the authorization is "public in, public out," structurally the same class of failure as the SecondFi incident, where per-signature authority was derivable entirely from public transaction data. [1](#0-0) 

### Finding Description
`allowListBasedAuth.AuthorizeRequest` computes `requestDigest, _ := req.Digest()` — a hash over the JSON-RPC `Method` and `Params`, both fully public, attacker-visible values — and checks it against `workflowRegistrySyncer.GetAllowlistedRequests(ctx)`, a list that is populated from an on-chain `WorkflowRegistry` contract readable by anyone. [2](#0-1) 

If a match is found, the function returns an `AuthResult` whose `workflowOwner` is simply `allowlistedRequest.Owner` — the address that originally called `AllowlistRequest` on-chain — with **no verification that the current caller is that address**, and no signature check at all: [3](#0-2) 

Compare this to the alternate path, `jwtBasedAuth.AuthorizeRequest`, which cryptographically binds the request digest to an OAuth-issued, signature-verified JWT (`claims.RequestDigest`, `TenantID`, scopes, etc.) before trusting it: [4](#0-3) 

The generic `Authorizer` wrapping both mechanisms only adds a single-use replay guard (`replayGuard.CheckAndRecord`) and an owner-field consistency check on the request body — neither of which requires proof of who actually possesses the owner's private key: [5](#0-4) 

The on-chain `AllowlistRequest(digest, expiry)` call (made by the legitimate owner to pre-authorize a specific request) publishes only a 32-byte digest, not the underlying plaintext. That is by design meant to keep the request body confidential until submission. But once the plaintext request is transmitted to the gateway (over HTTP, via test/integration helpers such as `ExecuteSecrets`/`storeConfidentialWorkflowSecret`), whoever obtains that plaintext — through network interception, logging, a compromised relay, or simply racing the legitimate client to the gateway endpoint — can submit it themselves and be treated as the owner, exactly like the SecondFi flaw where possession of a single previously-public signature was sufficient to reconstruct signing authority. [6](#0-5) 

### Impact Explanation
An attacker who obtains (via network capture, log access, or a race condition before the legitimate request is submitted) the exact plaintext of an allowlisted Vault JSON-RPC request can replay it to the gateway and be authorized as the real workflow owner for that single request — enabling unauthorized `vault.secrets.create/update/delete/list` operations (secret disclosure, overwrite, or deletion) attributed to another organization's workflow owner. This is a genuine authentication/authorization-bypass and request-impersonation risk in the unprivileged, internet-facing gateway path, consistent with the required "concrete authentication or role bypass... request impersonation" criteria.

### Likelihood Explanation
Exploitation requires either intercepting the plaintext request in transit/at rest before its single legitimate use, or winning a race to submit an identical request first — this is not a trivially remote-guessable bug (params typically include a client-generated `RequestId`/UUID that resists blind guessing), but it is architecturally weaker than the JWT path because it relies on confidentiality-of-transport rather than cryptographic proof-of-possession. Any leak point (logs, proxies, browser devtools, a malicious/compromised gateway operator relaying to nodes) is sufficient to trigger impersonation, and the code explicitly documents this fallback ("Requests without req.Auth continue using the allowlist-based path for backwards compatibility") as still active in production for clients that haven't adopted JWT auth. [7](#0-6) 

### Recommendation
- Require that every allowlist-based Vault request also carry a cryptographic signature (e.g., over the request digest) from the workflow owner's key, verified by the gateway/handler before granting `AuthorizedOwner`, rather than trusting digest-match alone.
- Treat `AllowListBasedAuth` as a legacy/deprecated path and prioritize migrating all clients to `JWTBasedAuth`, which binds digests to signed, replay-protected tokens.
- Ensure gateway access logs and any intermediate proxies never persist or expose full request bodies for allowlisted Vault methods, and enforce TLS end-to-end to reduce interception surface.

### Proof of Concept
1. Owner `O` computes `digest = req.Digest()` for a `vault.secrets.list` request (`Method="vault.secrets.list"`, `Params={Namespace:"main", Owner:O}`) and calls `WorkflowRegistry.AllowlistRequest(digest, expiry)` on-chain — this digest is now publicly readable via `GetAllowlistedRequests`.
2. Before `O`'s client submits the actual JSON-RPC body to the gateway, an attacker who has captured that exact plaintext (e.g., via a compromised proxy, browser network tab, or log line) submits it to the gateway first.
3. `allowListBasedAuth.AuthorizeRequest` recomputes the same digest from the attacker-submitted public `Method`/`Params`, finds it in the on-chain allowlist, and returns `AuthResult{workflowOwner: O}` — granting the attacker `O`'s identity for that Vault operation, with no signature check ever performed. [8](#0-7)

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L32-77)
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
}
```

**File:** core/capabilities/vault/jwt_based_auth.go (L187-217)
```go
// AuthorizeRequest verifies JWTBasedAuth state and token claims, and returns a common AuthResult.
func (v *jwtBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	claims, err := v.validateToken(ctx, req.Auth)
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth token validation failed", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("invalid JWT auth token: %w", err)
	}

	if scopeErr := enforceVaultJWTOAuthScopes(req.Method, claims.OAuthScopes); scopeErr != nil {
		v.lggr.Debugw("JWTBasedAuth OAuth scope rejected request", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "scopes", claims.OAuthScopes, "error", scopeErr)
		return nil, fmt.Errorf("invalid JWT auth token: %w", scopeErr)
	}

	if claims.TenantID == 0 {
		return nil, ErrMissingTenantID
	}
	if claims.TenantID != v.expectedTenantID {
		v.lggr.Debugw("JWT tenant id does not match job spec auth0 tenantID", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "claimsTenantID", claims.TenantID, "expectedTenantID", v.expectedTenantID)
		return nil, fmt.Errorf("%w: jwt tenant id %d expected tenant id %d", ErrJWTTenantIDJobSpecMismatch, claims.TenantID, v.expectedTenantID)
	}

	requestDigest, err := req.Digest()
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth failed to compute request digest", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "workflowOwner", claims.WorkflowOwner, "error", err)
		return nil, fmt.Errorf("failed to compute request digest: %w", err)
	}

	if !strings.EqualFold(requestDigest, claims.RequestDigest) {
		v.lggr.Debugw("JWTBasedAuth request digest mismatch", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "workflowOwner", claims.WorkflowOwner, "computedDigest", requestDigest, "claimedDigest", claims.RequestDigest)
		return nil, fmt.Errorf("request digest mismatch: computed=%s claimed=%s", requestDigest, claims.RequestDigest)
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

**File:** core/capabilities/vault/authorizer.go (L121-128)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
}
```

**File:** system-tests/lib/cre/workflow/secrets.go (L152-238)
```go
}

// ExecuteSecrets reads the encrypted secrets JSON file produced by PrepareSecrets,
// allowlists the vault request in the workflow registry, and sends the secrets to the vault gateway.
func ExecuteSecrets(ctx context.Context, encryptedSecretsJSONPath, gatewayURL string, sethClient *seth.Client, workflowRegistryAddress common.Address) error {
	data, err := os.ReadFile(encryptedSecretsJSONPath)
	if err != nil {
		return errors.Wrap(err, "failed to read encrypted secrets file")
	}

	var encryptedSecrets []*vault_helpers.EncryptedSecret
	if err = json.Unmarshal(data, &encryptedSecrets); err != nil {
		return errors.Wrap(err, "failed to unmarshal encrypted secrets")
	}

	uniqueRequestID := uuid.New().String()
	createSecretsRequest := vault_helpers.CreateSecretsRequest{
		RequestId:        uniqueRequestID,
		EncryptedSecrets: encryptedSecrets,
	}

	requestBody, err := json.Marshal(&createSecretsRequest)
	if err != nil {
		return errors.Wrap(err, "failed to marshal create secrets request")
	}
	requestBodyJSON := json.RawMessage(requestBody)

	jsonRequest := jsonrpc.Request[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      uniqueRequestID,
		Method:  vaulttypes.MethodSecretsCreate,
		Params:  &requestBodyJSON,
	}

	requestDigest, err := jsonRequest.Digest()
	if err != nil {
		return errors.Wrap(err, "failed to compute request digest")
	}

	requestDigestBytes, err := hex.DecodeString(requestDigest)
	if err != nil {
		return errors.Wrap(err, "failed to decode request digest hex")
	}
	if len(requestDigestBytes) != 32 {
		return errors.Errorf("invalid request digest length: got %d bytes, want 32", len(requestDigestBytes))
	}

	var reqDigestBytes [32]byte
	copy(reqDigestBytes[:], requestDigestBytes)

	wfReg, err := workflow_registry_v2_wrapper.NewWorkflowRegistry(workflowRegistryAddress, sethClient.Client)
	if err != nil {
		return errors.Wrap(err, "failed to instantiate workflow registry v2 wrapper")
	}

	expiry := uint32(time.Now().Add(time.Hour).Unix()) //nolint:gosec // G115: timestamp fits uint32 until year 2106
	_, decErr := sethClient.Decode(wfReg.AllowlistRequest(sethClient.NewTXOpts(), reqDigestBytes, expiry))
	if decErr != nil {
		return errors.Wrap(decErr, "failed to allowlist vault request in workflow registry")
	}

	fmt.Printf("\n✅ Vault request allowlisted in workflow registry\n")

	reqBody, err := json.Marshal(jsonRequest)
	if err != nil {
		return errors.Wrap(err, "failed to marshal JSON-RPC request")
	}

	statusCode, respBody, sendErr := cre.SendToVaultGateway(ctx, gatewayURL, reqBody)
	if sendErr != nil {
		return errors.Wrap(sendErr, "failed to send request to vault gateway")
	}
	if statusCode != http.StatusOK {
		return fmt.Errorf("vault gateway responded with status %d: %s", statusCode, string(respBody))
	}

	var jsonResponse jsonrpc.Response[json.RawMessage]
	if err := json.Unmarshal(respBody, &jsonResponse); err != nil {
		return errors.Wrap(err, "failed to unmarshal vault gateway response")
	}

	if jsonResponse.Error != nil && jsonResponse.Error.Error() != "" {
		return fmt.Errorf("vault gateway returned error: %s", jsonResponse.Error.Error())
	}

	return nil
}
```
