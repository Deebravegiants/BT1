### Title
Public Vault gateway endpoint lets an unprivileged caller pre-consume an allowlisted request digest, blocking the legitimate owner's Vault operation - ([File: core/capabilities/vault/authorizer.go])

### Summary
The Chainlink Vault capability's allowlist-based authorization path treats a request's content-derived digest as a single-use "nonce." Any caller who can reproduce the exact JSON-RPC request bytes that hash to an on-chain allowlisted digest can submit that request through the unauthenticated public gateway endpoint and burn the allowlist slot via the replay guard, before the legitimate workflow owner's real request arrives — denying the intended operation. This mirrors the `checkOrder`/`_useNonce` griefing pattern in the referenced report, where an externally reachable function consumes a one-time-use value that gates a legitimate operation.

### Finding Description
Vault requests reach the gateway through `handler.HandleJSONRPCUserMessage`, which is the public, unauthenticated entry point for `vault.secrets.*` methods: [1](#0-0) 

For allowlist-based requests (no `req.Auth` JWT), authorization is delegated to `allowListBasedAuth.AuthorizeRequest`, which only checks that the request's content-derived digest matches a digest previously registered on-chain (`WorkflowRegistryOwnerAllowlistedRequest`) and has not expired — it does not verify that the caller submitting the JSON-RPC request over the gateway is the actual owner: [2](#0-1) 

The generic `Authorizer` then treats the digest as a one-time-use nonce via `RequestReplayGuard.CheckAndRecord`, which errors with `ErrRequestAlreadySeen` if the same digest was already recorded: [3](#0-2) [4](#0-3) 

This is structurally identical to `CrabNetting._useNonce`: consuming the identifier (nonce/digest) succeeds on the *first* caller to present the matching value, regardless of whether that caller is the intended party. In `CrabNetting`, any address could call `checkOrder` to consume a victim's nonce ahead of time. Here, any unauthenticated client of the public gateway can attempt to submit content that hashes to a soon-to-be- or already-allowlisted digest; for methods like `vault.secrets.list` and `vault.secrets.delete`, the params consist of publicly known/derivable fields (owner address, namespace, secret key) and a caller/client-chosen `request_id` string embedded in params — none of which are secret or cryptographically bound to the actual sender's identity on this path (unlike the JWT path, which requires a signed token whose claims must match the digest, per `jwt_based_auth.go:187-233`). If an attacker can predict or observe the exact request bytes (e.g., a predictable/sequential `request_id`, or by intercepting the request in transit before it lands, or simply guessing common values), they can pre-submit it to the public gateway, causing `CheckAndRecord` to consume the slot for the real owner.

### Impact Explanation
A successful pre-consumption denies the legitimate workflow owner's Vault secrets management operation (create/update/delete/list) once their allowlisted window is in play, forcing them to re-register a new allowlisted digest on-chain (an on-chain transaction with real cost/delay) and retry. This is a griefing/denial-of-service on a security-sensitive capability (Vault secrets), directly analogous in severity class to the reported Auction-blocking issue — it doesn't move funds directly, but blocks intended privileged operations for the legitimate actor using only unprivileged, unauthenticated access to the public gateway.

### Likelihood Explanation
Exploitability depends on the attacker's ability to reproduce byte-identical request content for an allowlisted digest before the legitimate request is submitted. For write-once/short race windows this may be difficult in general, but for predictable client `request_id` schemes or observed/re-broadcastable requests it is straightforward, and no privileged credential or role is required — the endpoint is intentionally public and unauthenticated for allowlist-based requests. This is a genuine design gap (the allowlist path lacks per-request non-repudiation, unlike the JWT path) rather than a purely theoretical concern.

### Recommendation
- Bind allowlist-authorized requests to a proof-of-origin (e.g., require a signature over the exact request from the owner's key, similar to the JWT path's signed digest claim) rather than accepting any caller who reproduces matching bytes.
- Alternatively, scope the replay guard consumption to be keyed by (digest, first successful *forwarding* to nodes) only after basic sender-liveness/session checks, and/or allow the legitimate owner to invalidate/reset a griefed slot without needing to fully re-register on-chain.
- Rate-limit and require per-caller session/auth even on the "allowlist" path before performing digest matching, so anonymous guesses can't cheaply race legitimate requests.

### Proof of Concept
1. Workflow owner registers an allowlisted request digest on-chain via `WorkflowRegistry` for a future `vault.secrets.delete` request with known `owner`, `namespace: "main"`, `key: "k"`, and a `request_id` the owner intends to reuse (e.g., a fixed or predictable string).
2. Before the owner submits the actual JSON-RPC request, an attacker submits an identical `vault.secrets.delete` request (same method, id, params) directly to the public gateway endpoint (`handler.HandleJSONRPCUserMessage`).
3. `allowListBasedAuth.AuthorizeRequest` finds the digest allowlisted and returns success; `authorizer.AuthorizeRequest` calls `replayGuard.CheckAndRecord(digest, expiresAt)`, which succeeds and records the digest as seen — the attacker's spurious request is processed/forwarded.
4. The legitimate owner then submits the real request with the same digest; `replayGuard.CheckAndRecord` now returns `ErrRequestAlreadySeen`, and the owner's request is rejected with "request not authorized: request was already authorized previously", exactly mirroring `checkOrder` consuming `nonces[trader][nonce]` ahead of the legitimate order in `CrabNetting`.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L394-434)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
		if cachedPublicKey == nil {
			// Not found in cache. Fetch from nodes.
			ar, err := h.newActiveRequest(req, callback)
			if err != nil {
				h.lggr.Errorw("failed to create new activeRequest", "error", err)
				return err
			}
			return h.handlePublicKeyGet(ctx, ar)
		}
		h.lggr.Debugw("returning cached public key response")
		return h.handlePublicKeyGetSynchronously(ctx, req, publicKeyResponseBytes, callback)
	}

	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
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

**File:** core/capabilities/vault/request_replay_guard.go (L30-47)
```go
// CheckAndRecord returns ErrRequestAlreadySeen if the digest was previously
// recorded and has not yet expired. Otherwise it records the digest with
// the given expiry timestamp (unix seconds, UTC).
//
// Expired entries are cleaned up on every call.
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
