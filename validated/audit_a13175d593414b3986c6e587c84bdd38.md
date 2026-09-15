The code confirms the claim exactly as described: `Authorize` calls `isReplay` under an `RLock` (released after the check), then later calls `recordUsage` under a separate `Lock` [1](#0-0) , and `jwtReplayCache.isReplay`/`recordUsage` use independent, non-overlapping lock scopes [2](#0-1) . This is a genuine, non-atomic check-then-act pattern: two goroutines processing the same `jti` concurrently can both pass `isReplay` before either calls `recordUsage`, allowing single-use JWTs to be replayed and both requests to proceed to trigger a workflow execution via `httpTriggerHandler.authorizeRequest` → `HandleUserTriggerRequest` [3](#0-2) . This endpoint is reachable by any unprivileged caller holding a valid signed JWT, satisfying the reachability requirement, and the finding is not excluded by `SECURITY.md`'s exclusion list (no privileged-access, leaked-credential, or test-only exclusion applies here) [4](#0-3) .

Audit Report

## Title
JWT replay-protection check-then-record race in gateway HTTP trigger authorization allows one-time JWT reuse - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

## Summary
`WorkflowMetadataHandler.Authorize` performs replay protection for single-use JWTs via a non-atomic check-then-act sequence: `isReplay(claims.ID)` is checked under a read lock, and only after subsequent authorization checks succeed is `recordUsage(claims.ID)` called under a separate write lock. Two concurrent requests carrying the identical JWT can both pass `isReplay` before either calls `recordUsage`, allowing a JWT intended for single use to authorize two (or more) workflow-execute trigger requests.

## Finding Description
`Authorize` is invoked from `httpTriggerHandler.authorizeRequest` for every inbound `workflow.execute` HTTP trigger request [3](#0-2) . Inside `Authorize`, the JWT is verified, then `isReplay(claims.ID)` is checked; only near the end of the function, after the signer/authorized-key check succeeds, is `recordUsage(claims.ID)` called [1](#0-0) . The underlying cache uses distinct lock scopes for the read (`isReplay`, `RLock`) and write (`recordUsage`, `Lock`) [2](#0-1) , so there is a window between the two calls where a second concurrent request with the same `jti` can pass the check before the first request records usage. This is a genuine TOCTOU race in the replay-guard logic; the check and the mark-as-used write are not performed atomically.

## Impact Explanation
This breaks the single-use guarantee of the JWT replay protection, which exists specifically to prevent a captured/replayed token from triggering more than one workflow execution, as evidenced by the explicit error message returned once a `jti` is detected as reused [5](#0-4) . If exploited, an attacker holding one valid token can, by sending it concurrently, cause two workflow executions to be authorized and dispatched via `HandleUserTriggerRequest`, constituting unauthorized duplicate triggering / gateway request impersonation-adjacent behavior for a token meant to be single-use.

## Likelihood Explanation
Exploitation only requires firing the same captured JWT as two near-simultaneous requests, something any external caller of the HTTP trigger gateway can attempt trivially. The race window is narrow — bounded by the time between the `isReplay` read-lock release and the `recordUsage` write-lock acquisition, which spans the authorized-key lookup — but it is real, deterministically triggerable with sufficiently synchronized concurrent requests, and requires no privileged access, credentials beyond a legitimately obtained/replayed token, or host access.

## Recommendation
Make the check-and-record operation atomic by acquiring a single write lock across both the membership check and the insertion in `jwtReplayCache` (e.g., add a combined `checkAndRecord(jti string) bool` method using one `Lock()`/`Unlock()` critical section), and have `Authorize` call this combined method instead of separate `isReplay`/`recordUsage` calls.

## Proof of Concept
1. Obtain a valid signed JWT for a `workflow.execute` request with a fixed `jti`, as in `TestWorkflowMetadataHandler_Authorize`'s "JWT replay protection" subtest [6](#0-5) .
2. Instead of calling `handler.Authorize` sequentially as in the existing test, invoke it from two goroutines concurrently with the same token/claims.
3. Observe that both calls can return a non-nil `*AuthorizedKey` and `nil` error, since both may execute `isReplay(claims.ID)` before either executes `recordUsage(claims.ID)`, defeating the single-use guarantee.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-107)
```go
func (h *WorkflowMetadataHandler) Authorize(workflowID string, token string, req *jsonrpc.Request[json.RawMessage]) (*gateway.AuthorizedKey, error) {
	claims, signer, err := utils.VerifyRequestJWT(token, *req)
	if err != nil {
		h.lggr.Errorw("Failed to verify JWT", "error", err)
		return nil, err
	}

	if h.jwtCache.isReplay(claims.ID) {
		h.lggr.Warnw("JWT token has already been used", "workflowID", workflowID, "signer", signer.Hex(), "jti", claims.ID)
		return nil, errors.New("JWT token has already been used. Please generate a new one with new id (jti)")
	}

	keys, exists := h.authorizedKeys[workflowID]
	if !exists {
		h.lggr.Errorw("Workflow ID not found in authorized keys", "workflowID", workflowID)
		return nil, fmt.Errorf("workflow ID %s not found", workflowID)
	}
	key := gateway.AuthorizedKey{
		KeyType:   gateway.KeyTypeECDSAEVM,
		PublicKey: strings.ToLower(signer.Hex()),
	}
	if _, exists = keys[key]; !exists {
		h.lggr.Errorw("Signer not found in authorized keys", "signer", signer.Hex())
		return nil, fmt.Errorf("signer '%s' is not authorized for workflow '%s'. Ensure that the signer is registered in the workflow definition", signer.Hex(), workflowID)
	}
	h.jwtCache.recordUsage(claims.ID)

	return &key, nil
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L399-412)
```go
func (cache *jwtReplayCache) isReplay(jti string) bool {
	cache.mu.RLock()
	defer cache.mu.RUnlock()

	_, exists := cache.cache[jti]
	return exists
}

func (cache *jwtReplayCache) recordUsage(jti string) {
	cache.mu.Lock()
	defer cache.mu.Unlock()

	cache.cache[jti] = time.Now()
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-376)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
}
```

**File:** SECURITY.md (L1-65)
```markdown
# Common Vulnerability Exclusion List

## Out of Scope & Rules

These are the default impacts recommended to projects to mark as out of scope for their bug bounty program. The actual list of out-of-scope impacts differs from program to program.

### General

- Impacts requiring attacks that the reporter has already exploited themselves, leading to damage.
- Impacts caused by attacks requiring access to leaked keys/credentials.
- Impacts caused by attacks requiring access to privileged addresses (governance, strategist), except in cases where the contracts are intended to have no privileged access to functions that make the attack possible.
- Impacts relying on attacks involving the depegging of an external stablecoin where the attacker does not directly cause the depegging due to a bug in code.
- Mentions of secrets, access tokens, API keys, private keys, etc. in GitHub will be considered out of scope without proof that they are in use in production.
- Best practice recommendations.
- Feature requests.
- Impacts on test files and configuration files, unless stated otherwise in the bug bounty program.

### Smart Contracts / Blockchain DLT

- Incorrect data supplied by third-party oracles.
- Impacts requiring basic economic and governance attacks (e.g. 51% attack).
- Lack of liquidity impacts.
- Impacts from Sybil attacks.
- Impacts involving centralization risks.

Note: This does not exclude oracle manipulation/flash-loan attacks.

### Websites and Apps

- Theoretical impacts without any proof or demonstration.
- Impacts involving attacks requiring physical access to the victim device.
- Impacts involving attacks requiring access to the local network of the victim.
- Reflected plain text injection (e.g. URL parameters, path, etc.).
- This does not exclude reflected HTML injection with or without JavaScript.
- This does not exclude persistent plain text injection.
- Any impacts involving self-XSS.
- Captcha bypass using OCR without impact demonstration.
- CSRF with no state-modifying security impact (e.g. logout CSRF).
- Impacts related to missing HTTP security headers (such as `X-FRAME-OPTIONS`) or cookie security flags (such as `httponly`) without demonstration of impact.
- Server-side non-confidential information disclosure, such as IPs, server names, and most stack traces.
- Impacts causing only the enumeration or confirmation of the existence of users or tenants.
- Impacts caused by vulnerabilities requiring unprompted, in-app user actions that are not part of the normal app workflows.
- Lack of SSL/TLS best practices.
- Impacts that only require DDoS.
- UX and UI impacts that do not materially disrupt use of the platform.
- Impacts primarily caused by browser/plugin defects.
- Leakage of non-sensitive API keys (e.g. Etherscan, Infura, Alchemy, etc.).
- Any vulnerability exploit requiring browser bugs for exploitation (e.g. CSP bypass).
- SPF/DMARC misconfigured records.
- Missing HTTP headers without demonstrated impact.
- Automated scanner reports without demonstrated impact.
- UI/UX best practice recommendations.
- Non-future-proof NFT rendering.

## Prohibited Activities

The following activities are prohibited by default on bug bounty programs on Immunefi. Projects may add further restrictions to their own program.

- Any testing on mainnet or public testnet deployed code; all testing should be done on local forks of either public testnet or mainnet.
- Any testing with pricing oracles or third-party smart contracts.
- Attempting phishing or other social engineering attacks against employees and/or customers.
- Any testing with third-party systems and applications (e.g. browser extensions), as well as websites (e.g. SSO providers, advertising networks).
- Any denial-of-service attacks that are executed against project assets.
- Automated testing of services that generates significant amounts of traffic.
- Public disclosure of an unpatched vulnerability in an embargoed bounty.
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler_test.go (L1193-1217)
```go
	t.Run("JWT replay protection", func(t *testing.T) {
		params := json.RawMessage(`{"test": "data"}`)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      "test-request-id-replay",
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &params,
		}

		token, err := utils.CreateRequestJWT(*req)
		require.NoError(t, err)

		tokenString, err := token.SignedString(privateKey)
		require.NoError(t, err)

		key, err := handler.Authorize(workflowID, tokenString, req)
		require.NoError(t, err)
		require.NotNil(t, key)

		// Second authorization with same JWT should fail (replay attack)
		key, err = handler.Authorize(workflowID, tokenString, req)
		require.Error(t, err)
		require.Contains(t, err.Error(), "JWT token has already been used. Please generate a new one with new id (jti)")
		require.Nil(t, key)
	})
```
