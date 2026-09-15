## Finding: `writeMethodsEnabled` gate blocks `MethodSecretsDelete`, preventing users from removing/redacting their own secrets

### Title
Vault secret deletion is blocked by the same operator write-gate that governs create/update, preventing legitimate secret redaction - (File: `core/services/gateway/handlers/vault/handler.go`)

### Summary
The Sherlock finding flags that `claimERC20Prize`/`claimETHPrize` are gated by `whenNotPaused`, so an admin pause can block users from ever accessing rewards they're rightfully owed. The analogous class of bug — a global admin/operator switch blocking a user's ability to act on their own already-committed asset/data — exists in the CRE Vault gateway handler: `handleSecretsDelete` is gated behind the same `writeMethodsEnabled` limiter used for `handleSecretsCreate`/`handleSecretsUpdate`.

### Finding Description
`newHandlerWithAuthorizer` constructs a single gate limiter, `writeMethodsEnabled`, from the `GatewayVaultManagementEnabled` setting: [1](#0-0) 

This single gate is then checked identically in all three write-method handlers — `handleSecretsCreate`, `handleSecretsUpdate`, and `handleSecretsDelete` — before any of them are allowed to fan out to vault nodes: [2](#0-1) 

Unlike `claimERC20Prize`/`claimETHPrize` (which are pure "withdraw what you're owed" operations with no destructive side effect on system state), `DeleteSecrets` is the *only* mechanism by which a workflow owner can redact or remove sensitive secret material they previously stored in the Vault. Because deletion is lumped into the same `create/update/delete` gate, disabling `GatewayVaultManagementEnabled` (an operator-level toggle, analogous to the contract's `pause()`) blocks not just new writes but also a user's ability to remove already-stored secrets: [3](#0-2) 

### Impact Explanation
If an operator disables vault write methods (e.g., during an incident, maintenance, or a misconfiguration), any user who needs to delete a compromised or unwanted secret cannot do so — the secret remains persisted and retrievable via `MethodSecretsList`/reads by workflows, exactly the scenario the original report warns about (funds/assets a user is rightfully owed becoming inaccessible due to an admin-controlled pause). This is a legitimate, unprivileged-client-reachable path: any vault user hitting the gateway's `vault.secrets.delete` method is subject to this gate.

### Likelihood Explanation
The gate is toggled by the deployment/operator's settings (`cresettings.Default.GatewayVaultManagementEnabled`), so any time write methods are disabled for maintenance or safety reasons on create/update, delete is silently disabled as a side effect too — this is a design coupling issue, not something requiring an attacker, making it likely to occur in normal operational scenarios (e.g., incident response where an operator wants to halt new secret creation while still allowing cleanup/deletion).

### Recommendation
Decouple `handleSecretsDelete` from the `writeMethodsEnabled` gate (or provide a separate, narrower gate) so that secret deletion/redaction remains available to users even when create/update is administratively disabled, mirroring the original recommendation to remove `whenNotPaused` from the claim functions so that a pause cannot block users from accessing what is already theirs.

### Proof of Concept
1. Operator sets `GatewayVaultManagementEnabled` to disabled via `cresettings`.
2. `newHandlerWithAuthorizer` builds `writeMethodsEnabled` as a gate limiter that denies all calls (`core/services/gateway/handlers/vault/handler.go:236-239`).
3. A vault user sends a `vault.secrets.delete` request through the gateway.
4. `handleSecretsDelete` calls `h.writeMethodsEnabled.AllowErr(ctx)`, receives `limits.ErrorNotAllowed{}`, and returns `UnsupportedMethodError` — the delete never reaches `fanOutToVaultNodes`, so the secret cannot be removed (`core/services/gateway/handlers/vault/handler.go:643-656`).

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L236-239)
```go
	writeMethodsEnabled, err := limits.MakeGateLimiter(limitsFactory, cresettings.Default.GatewayVaultManagementEnabled)
	if err != nil {
		return nil, fmt.Errorf("could not create vault mgmt limiter: %w", err)
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L643-656)
```go
func (h *handler) handleSecretsDelete(ctx context.Context, ar *activeRequest) error {
	l := logger.With(h.lggr, "method", ar.req.Method, "requestID", ar.req.ID)

	err := h.writeMethodsEnabled.AllowErr(ctx)
	if errors.Is(err, limits.ErrorNotAllowed{}) {
		l.Warnw("secrets write method called but write methods are disabled", "error", err)
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.UnsupportedMethodError, errors.New("vault write methods(create/update/delete) are disabled: "+err.Error()), nil))
	} else if err != nil {
		l.Errorw("error checking if write methods are enabled", "error", err)
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, errors.New("error checking if write methods are enabled: "+err.Error()), nil))
	}

	return h.fanOutToVaultNodes(ctx, l, ar)
}
```
