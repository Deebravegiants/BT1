### Title
Vault gateway blocks secret deletion when write methods are disabled, preventing users from removing at-risk secrets - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The Vault gateway handler gates `handleSecretsCreate`, `handleSecretsUpdate`, and `handleSecretsDelete` behind the same `writeMethodsEnabled` kill-switch check, treating secret deletion identically to secret creation/update. This mirrors the reported Seawater/Superposition bug class where a "disabled" flag meant to stop new deposits also incorrectly blocked withdrawals — here, an operator-level "disable vault writes" switch also blocks users from deleting (removing) their own secrets.

### Finding Description
`handleSecretsCreate`, `handleSecretsUpdate`, and `handleSecretsDelete` in the gateway vault handler each independently call `h.writeMethodsEnabled.AllowErr(ctx)` before processing the request, returning an `UnsupportedMethodError` ("vault write methods(create/update/delete) are disabled") when the switch is off: [1](#0-0) 

Unlike the `MethodSecretsList` handler, which performs no such check and always fans out to vault nodes: [2](#0-1) 

Deletion is a data-removal operation, conceptually analogous to "removing liquidity" in the Seawater report: it reduces the state exposed by the system rather than adding new secret material. Grouping delete together with create/update under a single `writeMethodsEnabled` guard means that whenever an operator flips this switch off — e.g., during an incident, migration, or a suspected compromise of the vault's encryption/master key — users lose the ability to delete their own secrets exactly when they are most likely to want to do so (to limit exposure of secrets they believe may be at risk).

I could not locate the definition/wiring of `writeMethodsEnabled` (its `limits.Factory`/settings source) in the available index, so I cannot confirm additional context such as default value, config knob name, or intended semantics (e.g., whether it is meant purely as a create/update killswitch that should never have included delete). This should be verified in a full checkout.

### Impact Explanation
When the write-methods switch is disabled, users cannot delete their own secrets via the gateway, even though deletion does not introduce new secret material and should generally remain available as a mitigation path (analogous to users needing to withdraw liquidity from a paused pool). If the switch is disabled during an incident where existing secrets are considered compromised or at risk, affected users have no way to proactively remove them from the vault DON's committed state until the switch is re-enabled.

### Likelihood Explanation
The condition is triggered any time an operator disables vault write methods, which per the code comment is intended to cover create/update/delete uniformly. Given the switch is explicitly documented as covering "create/update/delete", this is a deliberate design decision rather than an accidental omission, but it produces the same emergency-access problem described in the reference report: unprivileged callers are locked out of a removal-type action during exactly the window when the flag is likely to be toggled off.

### Recommendation
Reconsider whether `MethodSecretsDelete` should be gated by the same `writeMethodsEnabled` check as create/update. If the intent of the switch is to stop new/updated secret material from entering the system (e.g., due to a compromised master key or storage issue), `handleSecretsDelete` should be exempted from this check — mirroring the Seawater recommendation to only enforce the "enabled" gate on additive operations, not on removal/exit operations. At minimum, document the intended behavior and confirm with the vault design owners whether blocking deletes during an incident is a deliberate risk-acceptance decision.

### Proof of Concept
1. An operator/admin disables vault write methods (`writeMethodsEnabled` becomes `false`, cause not fully verifiable from indexed code).
2. A workflow owner sends a `MethodSecretsDelete` JSON-RPC request through the gateway to remove a secret they believe is at risk.
3. `handleSecretsDelete` calls `h.writeMethodsEnabled.AllowErr(ctx)`, which returns `limits.ErrorNotAllowed`.
4. The handler responds with `api.UnsupportedMethodError` and the message "vault write methods(create/update/delete) are disabled", refusing to forward the delete to vault nodes: [3](#0-2) 
5. The user's secret remains stored and retrievable while the write-disable switch is active, with no available path to remove it.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L613-656)
```go
func (h *handler) handleSecretsCreate(ctx context.Context, ar *activeRequest) error {
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

func (h *handler) handleSecretsUpdate(ctx context.Context, ar *activeRequest) error {
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

**File:** core/services/gateway/handlers/vault/handler.go (L658-661)
```go
func (h *handler) handleSecretsList(ctx context.Context, ar *activeRequest) error {
	l := logger.With(h.lggr, "method", ar.req.Method, "requestID", ar.req.ID)
	return h.fanOutToVaultNodes(ctx, l, ar)
}
```
