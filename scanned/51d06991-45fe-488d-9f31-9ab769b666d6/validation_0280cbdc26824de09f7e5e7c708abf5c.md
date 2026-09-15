This confirms the analog. The `AllowListBasedAuth.AuthorizeRequest` function authorizes any JSON-RPC request whose exact digest matches a `WorkflowRegistryOwnerAllowlistedRequest` entry on-chain — regardless of who actually submits it [1](#0-0) . Because the allowlisting transaction (and its `RequestDigest`) is public on-chain data, once it is confirmed (or even while pending), any unprivileged actor can compute the exact same JSON-RPC request bytes and submit them to the gateway's public `HandleJSONRPCUserMessage` endpoint before the legitimate workflow owner does [2](#0-1) . The shared `RequestReplayGuard` records the digest as "seen" on first successful authorization and rejects any subsequent attempt with that same digest via `ErrRequestAlreadySeen`, regardless of who submitted the first one [3](#0-2) [4](#0-3) .

### Title
Unprivileged actor can front-run AllowListBasedAuth digest to permanently deny a legitimate Vault request - (File: core/capabilities/vault/authorizer.go, core/capabilities/vault/allow_list_based_auth.go)

### Summary
The Vault gateway's `AllowListBasedAuth` flow authorizes a request purely by matching the request's content digest against an on-chain allowlist entry (`WorkflowRegistryOwnerAllowlistedRequest`), without binding the request to the actual submitter identity beyond that digest match. Because the allowlist entry (and thus the exact digest that will be accepted) is public on-chain data, any unprivileged client can front-run the legitimate workflow owner by submitting the identical request bytes to the gateway's public JSON-RPC endpoint first.

### Finding Description
`allowListBasedAuth.AuthorizeRequest` computes `req.Digest()` from the raw request and checks it against `WorkflowRegistrySyncer.GetAllowlistedRequests`, returning success for anyone whose request digest matches an allowlisted entry [1](#0-0) . There is no requirement that the caller possess a private key or session tied to the owner — matching bytes is sufficient, since the on-chain allowlist entry is public. Once authorized, `authorizer.AuthorizeRequest` immediately calls `a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt())`, which will reject *any* future request bearing the same digest with `ErrRequestAlreadySeen`, until the allowlist entry's `ExpiryTimestamp` passes [3](#0-2) [5](#0-4) . Because the allowlist entry that determines the digest is published on-chain (visible to any observer before or as soon as it's mined), an attacker who reconstructs the exact JSON-RPC request bytes (method, params, ID) that the owner intends to send can submit that same request to the public gateway endpoint `HandleJSONRPCUserMessage` first [2](#0-1) . This causes the gateway (and independently each node, which runs its own instance of the same authorizer/replay-guard pipeline via `GatewayVaultRequestProcessor`) to consume the digest, so when the legitimate owner's real request with the identical digest arrives, it is rejected outright with "request was already authorized previously" — even though the attacker's spoofed submission never produced any usable secret result for the attacker (it may fail downstream for unrelated reasons, but the replay slot is already burned).

This mirrors the Angstrom `PermitSubmitterHook` bug class: a signature/authorization artifact that is publicly observable (there, the ERC-20 permit signature; here, the on-chain allowlist digest) can be "used up" by any unprivileged third party before the intended, legitimate actor's transaction/request lands, causing the legitimate action to revert/fail.

### Impact Explanation
This is a denial-of-service / griefing vector against a specific workflow owner's Vault secrets operations (create/update/delete/list). An attacker with no privileges beyond internet access to the gateway can prevent a workflow owner from ever successfully executing an on-chain-allowlisted Vault request for the duration of the allowlist expiry window, since the digest-based replay guard is a hard, permanent-until-expiry rejection with no owner/session binding to distinguish the legitimate submitter from the attacker [6](#0-5) . This does not by itself grant the attacker access to secrets (owner-scoped validation in `validateSecretOwnersMatchAuthorized` still binds params to the allowlisted owner), but it does block/deny the legitimate flow, which is exactly the "medium risk" griefing/DoS impact class described in the report.

### Likelihood Explanation
Exploitability depends on the attacker being able to reconstruct byte-identical request params (which include encrypted secret payloads, IDs, namespaces, etc.) before the real request is submitted — this is nontrivial in practice since the JSON-RPC request body is not itself published on-chain, only the digest is. The report's TrustSecurity "Permission denied" pattern requires attacker knowledge of the exact signed payload, which is a meaningful precondition. Given this precondition (e.g., if the request content becomes known via monitoring of the workflow registry allowlist transaction submission, logs, or other side channels before it's relayed to the gateway), the front-run itself is straightforward and requires no special privilege — just a faster JSON-RPC submission to the public gateway endpoint.

### Recommendation
Bind `AllowListBasedAuth` authorization (and the replay guard) not just to the request digest but to a verified proof of the submitter's identity (e.g., require the request to be signed/authenticated similarly to the JWT-based path), so an attacker who merely learns/replicates the public digest cannot consume the authorization slot on behalf of the legitimate owner. Alternatively, scope the replay guard key to `(digest, first-successful-owner-match)` combined with a sender-provided proof, and/or make the on-chain allowlist confirmation itself sufficiently owner-bound (e.g., requiring the request payload to be submitted from a channel authenticated to the owner) before the digest is considered "consumable," analogous to wrapping `permit()` in try/catch in the original report — i.e., don't let a third party's replay of public authorization data cause the legitimate request to be treated as already-consumed.

### Proof of Concept
1. Workflow owner submits (or is about to submit) an on-chain transaction that adds a `WorkflowRegistryOwnerAllowlistedRequest` entry with `RequestDigest = D` for a specific Vault `SecretsCreate` request they intend to send.
2. Attacker observes/derives the exact JSON-RPC request bytes whose `req.Digest()` equals `D` (e.g., via visibility into the pending transaction data, logs, or other means the attacker has access to) and POSTs that exact request to the gateway's public JSON-RPC vault endpoint (`HandleJSONRPCUserMessage`) before the real owner's client does.
3. `allowListBasedAuth.AuthorizeRequest` matches digest `D` against the confirmed allowlist entry and succeeds; `authorizer.AuthorizeRequest` then calls `replayGuard.CheckAndRecord(D, expiry)`, marking `D` as seen [3](#0-2) .
4. When the legitimate owner's client subsequently submits the identical request (same digest `D`), `CheckAndRecord` returns `ErrRequestAlreadySeen`, and the owner's genuine request is rejected until the allowlist entry's `ExpiryTimestamp` passes [4](#0-3) .

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L34-76)
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

**File:** core/capabilities/vault/authorizer.go (L99-112)
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
```

**File:** core/capabilities/vault/request_replay_guard.go (L9-47)
```go
var ErrRequestAlreadySeen = errors.New("request was already authorized previously")

// RequestReplayGuard prevents replay of already-processed requests by tracking
// request digests with expiry timestamps. It is safe for concurrent use.
//
// Used by both the AllowListBasedAuth flow and the JWTBasedAuth flow to ensure
// that a given request digest is only accepted once.
type RequestReplayGuard struct {
	mu      sync.Mutex
	seen    map[string]int64 // digest → unix expiry timestamp
	nowFunc func() time.Time // injectable for testing
}

// NewRequestReplayGuard creates a replay guard for authorized Vault requests.
func NewRequestReplayGuard() *RequestReplayGuard {
	return &RequestReplayGuard{
		seen:    make(map[string]int64),
		nowFunc: time.Now,
	}
}

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
