### Title
Unauthenticated request-digest front-running can permanently freeze a legitimate user's Vault request via the replay guard - (File: core/capabilities/vault/request_replay_guard.go)

### Summary
The Vault authorization pipeline dedupes requests purely by a content-derived `digest` (method + params), independent of which caller submitted it or whether that caller's authorization is actually valid for a *different* concurrent submission. `RequestReplayGuard.CheckAndRecord` marks a digest as "seen" as soon as *any* request with that digest is authorized, and every subsequent request sharing the same digest is rejected with `ErrRequestAlreadySeen` until the recorded expiry passes.

### Finding Description
`authorizer.AuthorizeRequest` computes an `AuthResult` (owner, digest, expiry) from either the AllowList path or the JWT path, then unconditionally calls `a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt())` [1](#0-0) . The replay guard is a simple map keyed by digest string; the first caller to get their digest recorded "wins", and every following request with the identical digest is rejected until the stored expiry passes [2](#0-1) .

For the AllowList path, the authorized digest comes from a set of on-chain/registry allowlisted requests (`allowlistedRequest.RequestDigest`, `allowlistedRequest.ExpiryTimestamp`) that are fetched and matched by `AuthorizeRequest` in `allowListBasedAuth` [3](#0-2) . Because the allowlist is a registry-visible structure that legitimate users must publish (an owner, method, params digest, and expiry) in order for their own later request to be authorized, an unprivileged party who can observe that registry entry (or predict the deterministic digest from known method/params) can submit a syntactically well-formed request that hashes to the *same* digest before the legitimate owner's real request arrives at the gateway. This is directly analogous to the reported bug class: an attacker front-runs a state-changing, timestamp/marker-setting call (there `depositProfitTokenForUsers` setting `lastProfitTime`; here `CheckAndRecord` setting the digest as "seen") that a legitimate, permissionless second actor's action depends on, thereby locking that dependent actor out until the marker's validity window naturally expires.

Concretely: `req.Digest()` is derived purely from the request's method + params (content), not from the caller's identity or the specific auth material used to authorize it [4](#0-3) . As long as an attacker can construct or replay a request whose digest matches an allowlisted (or otherwise soon-to-be-submitted) legitimate request, and get it authorized (which is possible if the allowlist entry itself is public/knowable, since the allowlist authorization only checks digest + expiry + owner match, not secrecy of the digest), the attacker's call reaches `CheckAndRecord` first and consumes the digest slot, causing `ErrRequestAlreadySeen` to be returned when the legitimate request with the identical digest is subsequently processed by the real owner/workflow node [5](#0-4) .

### Impact Explanation
If exploitable, this denies service to a specific legitimate Vault operation (e.g., secrets create/update/list/delete for a given workflow owner) for the duration of the authorization's validity window, since the replay guard entry blocks any further attempt with the same digest until `expiresAtUnix` passes and `clearExpiredLocked` reclaims it [6](#0-5) . This mirrors the reported impact of freezing a legitimate permissionless action (there, profit withdrawal; here, a Vault secrets operation) via a race on a shared, non-caller-scoped state marker.

### Likelihood Explanation
This requires that the digest used for authorization is either predictable or observable to an unprivileged third party ahead of the legitimate submission (e.g., visibility into the on-chain/registry allowlist entry, or a predictable `request_id`/params combination) and that the attacker can reach the same authorization path (AllowList-based, since JWT-based binds the digest to signed claims tied to the org/workflow owner, which is harder to forge). I could not fully confirm from the available index whether the on-chain allowlist entries (digest + expiry + owner) are readable by arbitrary unprivileged callers before the real request is submitted, nor whether `findAllowlistedItemWithRetry` enforces any additional caller-binding beyond digest match. This uncertainty limits confidence in likelihood — it is plausible but unverified whether an attacker without any privileged position can obtain the digest ahead of time and construct an authorizable payload matching it.

### Recommendation
Scope the replay guard key to (digest, authorized owner) rather than digest alone, or bind replay-guard consumption to the same caller/session that will submit the real payload, so an unrelated party cannot pre-consume a digest slot on behalf of another owner's pending request. Additionally, consider requiring that `CheckAndRecord` only accept digests where the request's owner-binding (`validateSecretOwnersMatchAuthorized`) has already been validated for that specific submission, preventing a decoupled front-run from consuming the shared digest namespace.

### Proof of Concept
Not able to construct a concrete end-to-end PoC from the indexed code alone — this would require confirming (1) that the on-chain/registry allowlist entry (digest/expiry/owner) is visible to third parties prior to the real request submission, and (2) that `findAllowlistedItemWithRetry` in `allow_list_based_auth.go` does not further bind the digest to the specific submitting session. A Devin session with full repo/registry access would be needed to validate whether the allowlist digest is realistically obtainable by an unprivileged attacker before the legitimate request is processed.

### Citations

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

**File:** core/capabilities/vault/request_replay_guard.go (L49-64)
```go
// ClearExpired removes all entries whose expiry timestamp is in the past.
// Call this to eagerly reclaim memory even when CheckAndRecord is not invoked.
func (g *RequestReplayGuard) ClearExpired() {
	g.mu.Lock()
	defer g.mu.Unlock()
	g.clearExpiredLocked()
}

func (g *RequestReplayGuard) clearExpiredLocked() {
	now := g.nowFunc().UTC().Unix()
	for digest, expiry := range g.seen {
		if now > expiry {
			delete(g.seen, digest)
		}
	}
}
```

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L1-30)
```go
package vault

import (
	"context"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"strings"

	"github.com/smartcontractkit/tdh2/go/tdh2/tdh2easy"

	vaultcommon "github.com/smartcontractkit/chainlink-common/pkg/capabilities/actions/vault"
	jsonrpc "github.com/smartcontractkit/chainlink-common/pkg/jsonrpc2"
	"github.com/smartcontractkit/chainlink-common/pkg/logger"
	"github.com/smartcontractkit/chainlink/v2/core/capabilities/vault/vaulttypes"
	"github.com/smartcontractkit/chainlink/v2/core/capabilities/vault/vaultutils"
)

// GatewayVaultRequestProcessor orchestrates the shared gateway-routed vault JSON-RPC pipeline
// used by the gateway public handler and the node-side gateway connector handler.
//
// Pipeline invariant:
//
//	ValidateStructureBeforeAuth → AuthorizeRequest → Prefix ID → StampAuthorizedParams → ValidateOwnerScopedLimits
//	    (no param mutation)        (on raw bytes)               (namespace + request_id)      (ciphertext size)
//
// AuthorizeRequest runs while params are still digest-safe. It also applies the replay guard
// (digest deduplication) and validates that payload owners match the authorized workflow owner
// before this processor rewrites the request ID or stamps params.
```
