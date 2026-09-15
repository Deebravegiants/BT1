### Title
Replay guard records request digest before owner-authorization validation completes, enabling DoS via replay-guard poisoning - ([File: core/capabilities/vault/authorizer.go])

### Summary
`authorizer.AuthorizeRequest` in the node-side Vault gateway handler records a request's digest into the replay guard (a state change) before the final authorization check — `validateSecretOwnersMatchAuthorized` — has run and passed. This mirrors the reported bug class ("modifiers/pre-checks should not make state changes before all checks pass"): an effect (marking a digest as "seen") is committed prior to the completion of all validation steps, so a request that is ultimately rejected still permanently poisons the replay-guard state for that exact digest.

### Finding Description
`AuthorizeRequest` performs authorization in the following order:

```go
func (a *authorizer) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	authResult, err := a.authorizeRequest(ctx, req)     // step 1: allowlist/JWT auth
	...
	if err := a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt()); err != nil { // STATE CHANGE
		...
		return nil, err
	}
	if ownerErr := validateSecretOwnersMatchAuthorized(req, authResult.AuthorizedOwner()); ownerErr != nil { // step 2 check, AFTER state change
		...
		return nil, ownerErr
	}
	...
}
``` [1](#0-0) 

`replayGuard.CheckAndRecord` both checks *and* unconditionally records the digest (state change) on success:
```go
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	...
	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}
	g.seen[digest] = expiresAtUnix
	return nil
}
``` [2](#0-1) 

Because the digest is computed from the full JSON-RPC request (method, ID, and params — including the `owner`/secret-identifier fields embedded in params), any caller who can obtain *any* valid allowlist/JWT authorization for themselves can submit a request whose params reference a different (victim) owner. The request passes step 1 (their own identity is validated), the digest gets recorded as "seen" in the replay guard, and only then does `validateSecretOwnersMatchAuthorized` reject the request because the embedded owner doesn't match the authorized identity. The check-effects ordering violation means the digest is already consumed even though authorization for that specific request content never actually succeeded end-to-end.

The comment documenting the pipeline invariant in `gateway_vault_request_processor.go` even states digest checks happen "while params are still digest-safe" and before owner validation, confirming this ordering is intentional but does not account for the digest being recorded on paths that are later rejected: [3](#0-2) 

### Impact Explanation
If an unprivileged/attacker-controlled workflow owner (who has their own valid allowlist entry or JWT) crafts a request whose JSON body exactly matches a legitimate victim request's byte-identical params/method/ID (which are often predictable — e.g., deterministic `request_id`, well-known `owner`, `namespace`, `key`), the attacker can pre-register that exact digest in the replay guard by triggering the owner-mismatch failure path. Any subsequent, legitimate attempt by the actual victim to submit that identical request will be rejected with `ErrRequestAlreadySeen` ("request was already authorized previously") until the digest's `expiresAt` window lapses — a denial-of-service against a specific victim secrets-management operation (create/update/delete/list) with no funds movement but a concrete availability impact on the vault capability.

### Likelihood Explanation
Exploitation requires: (1) the attacker to have their own valid, unprivileged authorization credential (allowlist entry or JWT) for the vault gateway — a normal capability any onboarded workflow owner has; and (2) knowledge/predictability of the victim's exact request bytes (method, request ID, and params). Because request IDs and secret keys are often deterministic/known to a workflow owner's operational tooling, and because the mismatch check runs on every method (`processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, `processListSecretIdentifiersRequest`), the likelihood is moderate — it's a straightforward reachable path through `GatewayHandler.HandleGatewayMessage` → `GatewayVaultRequestProcessor.ProcessRequest` → `authorizeAndStamp` → `authorizer.AuthorizeRequest`.

### Recommendation
Reorder `AuthorizeRequest` so all validation (including `validateSecretOwnersMatchAuthorized`) completes and passes before any state-changing call to `replayGuard.CheckAndRecord`. Concretely, move the owner-validation check ahead of the replay-guard recording, or split `CheckAndRecord` into a non-mutating `Check` (used pre-validation) and a `Record` (invoked only after all checks pass).

### Proof of Concept
1. Attacker obtains a valid allowlist/JWT authorization for their own workflow owner `0xAttacker`.
2. Attacker learns (or predicts) the exact JSON-RPC request that a victim `0xVictim` will send to `vault.secrets.create` (e.g., via observing a previous rejected attempt, shared tooling defaults, or a predictable `request_id`).
3. Attacker submits that identical request body to the gateway/node while authorized only as `0xAttacker`.
4. `authorizer.AuthorizeRequest` succeeds step 1 (attacker's own auth is valid), calls `replayGuard.CheckAndRecord(digest, expiresAt)` which records the digest as seen, then fails `validateSecretOwnersMatchAuthorized` because the params' `owner` field is `0xVictim`, not `0xAttacker`. The overall call returns an "owner binding rejected" error to the attacker.
5. `0xVictim` later submits the legitimate, identical request; `authorizer.AuthorizeRequest` calls `replayGuard.CheckAndRecord` again, finds the digest already present, and returns `ErrRequestAlreadySeen` — the victim's real request is denied until the poisoned entry expires.

### Citations

**File:** core/capabilities/vault/authorizer.go (L99-118)
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L20-34)
```go
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
//
// Owner-scoped limit checks are deferred until after authorization: each new owner tenant
// registered by a scoped limiter spawns a persistent background updater, so checking them
// pre-auth would let unauthenticated callers create unbounded limiter tenants.
```
