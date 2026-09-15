Based on my review of the code, the claim is accurate as described in the source.

Audit Report

## Title
Deducted metering balance is never refunded when a capability execution fails - ([File: core/services/workflows/v2/capability_executor.go])

## Summary
In `callCapability`, credits are earmarked from a workflow execution's local metering balance via `meterReport.Deduct(...)` (which internally calls `ByDerivedAvailability` → `r.balance.Minus(...)`) before the target capability is invoked. `meterReport.Settle`, the only function that reconciles the earmarked deduction against actual spend and refunds the unused portion, is only called on the success path; every error-return branch after `capability.Execute` fails skips it entirely.

## Finding Description
`callCapability` deducts from the in-memory balance store before executing the capability: [1](#0-0) 
This calls `ByDerivedAvailability`, which subtracts the earmarked amount directly from `r.balance` via `Minus`: [2](#0-1) 
When `capability.Execute` returns an error — whether a user-origin `caperrors.Error`, a system-origin `caperrors.Error`, or any other error (including timeouts from `CapabilityCallTime.WithTimeout`) — `callCapability` returns immediately in each branch without calling `Settle`: [3](#0-2) 
`Settle` is only invoked after a successful execution: [4](#0-3) 
`Settle` is the sole mechanism that refunds the unused earmark back to the balance (`Deduction - spentCredits`): [5](#0-4) 
Since it is never reached on any capability execution failure, the earmarked amount deducted by `Deduct`/`ByDerivedAvailability` is permanently lost from the in-memory `balance` for the remainder of that workflow execution.

## Impact Explanation
This is a within-execution, in-memory `balanceStore` (created fresh per `Report`/execution via `NewReport` and populated by `Reserve`), used to gate subsequent capability calls in the same execution against `ErrInsufficientBalance`-style checks. A failing capability call (config error, timeout, transient system error, or user error) permanently consumes its earmarked slice of the execution's local credit balance without any corresponding spend being recorded in `step.Spends`/`AggregatedSpends`, and `ByDerivedAvailability` can earmark the entire remaining available balance for a single call when `openConcurrentCallSlots == 1`. This can cause legitimate subsequent capability calls within the same workflow execution to be denied for insufficient balance, and represents an accounting integrity flaw within the metering subsystem's intra-execution bookkeeping. It does not directly demonstrate unauthorized fund movement, node API/auth bypass, key/secret exfiltration, gateway impersonation, or allowlist bypass — the in-scope impact categories listed in the validation rules — since the actual, real-money billing path (`SubmitWorkflowReceipt` submission of aggregated per-node spends) is a separate mechanism from this local, per-execution reservation balance, and the failure mode here manifests as premature exhaustion of an in-memory execution-scoped credit pool rather than a proven external fund-transfer or authorization defect.

## Likelihood Explanation
Highly likely to trigger in normal operation, since capability calls fail for benign reasons (timeouts, transient errors, misconfiguration) routinely, and any workflow that calls a fallible capability with metering enabled will hit this code path.

## Recommendation
Ensure `meterReport.Settle` (or an equivalent refund path) is invoked on every exit from `callCapability` after a successful `Deduct`, e.g., via a `defer` that settles with empty/zero metering metadata when `capability.Execute` errors, so earmarked-but-unspent credits are returned to the execution's local balance.

## Proof of Concept
1. Configure a workflow with metering enabled (`meterReport != nil`, `openConcurrentCallSlots == 1` so a single call earmarks the full available balance).
2. Trigger a capability call that fails (return a `caperrors.Error` with `OriginUser`, or force a timeout via `CapabilityCallTime`).
3. Observe that `callCapability` returns via the `if err != nil` branch at [3](#0-2)  without calling `Settle`.
4. Inspect `meterReport`'s internal `balance` (or attempt a second capability call in the same execution) to confirm the earmarked amount was not refunded and subsequent calls fail with an insufficient-balance condition — this can be implemented as a Go unit test in `core/services/workflows/v2/capability_executor_test.go` or `core/services/workflows/metering/metering_test.go` asserting that `r.balance` after a failed `Execute` equals the value before minus the deduction (no refund), unlike the success path where `Settle` restores `Deduction - spentCredits`.

### Citations

**File:** core/services/workflows/v2/capability_executor.go (L199-209)
```go
		if spendLimits, err = meterReport.Deduct(
			meteringRef,
			metering.ByDerivedAvailability(
				userSpendLimit,
				openConcurrentCallSlots,
				info,
				config.RestrictedConfig,
			),
		); err != nil {
			c.cfg.Lggr.Errorw("could not deduct balance for capability request", "capReq", request.Id, "capReqCallbackID", request.CallbackId, "err", err)
		}
```

**File:** core/services/workflows/v2/capability_executor.go (L260-281)
```go
	if err != nil {
		if capabilityError, ok := errors.AsType[caperrors.Error](err); ok {
			if capabilityError.Origin() == caperrors.OriginUser {
				execLogger.Debugw("Capability execution failed with user error", "userErr", err)
				_ = events.EmitCapabilityFinishedEvent(ctx, loggerLabels, c.WorkflowExecutionID, request.Id, meteringRef, store.StatusCompleted, request.Method, err)
				c.metrics.With(platform.KeyCapabilityID, request.Id, platform.KeyCapabilityErrorCode, capabilityError.Code().String()).IncrementCapabilityUserErrorCounter(ctx)
				return nil, fmt.Errorf("capability execution failed with user error: %w", err)
			}

			execLogger.Debugw("Capability execution failed with system error", "systemErr", err)
			_ = events.EmitCapabilityFinishedEvent(ctx, loggerLabels, c.WorkflowExecutionID, request.Id, meteringRef, store.StatusErrored, request.Method, err)
			c.metrics.With(platform.KeyCapabilityID, request.Id, platform.KeyCapabilityErrorCode, capabilityError.Code().String()).IncrementCapabilityFailureCounter(ctx)
			c.metrics.IncrementTotalWorkflowStepErrorsCounter(ctx)
			return nil, fmt.Errorf("failed to execute capability: %w", err)
		}

		execLogger.Debugw("Capability execution failed", "err", err)
		_ = events.EmitCapabilityFinishedEvent(ctx, loggerLabels, c.WorkflowExecutionID, request.Id, meteringRef, store.StatusErrored, request.Method, err)
		c.metrics.With(platform.KeyCapabilityID, request.Id, platform.KeyCapabilityErrorCode, caperrors.Internal.String()).IncrementCapabilityFailureCounter(ctx)
		c.metrics.IncrementTotalWorkflowStepErrorsCounter(ctx)
		return nil, fmt.Errorf("failed to execute capability: %w", err)
	}
```

**File:** core/services/workflows/v2/capability_executor.go (L283-290)
```go
	execLogger.Debug("Capability execution succeeded")
	_ = events.EmitCapabilityFinishedEvent(ctx, loggerLabels, c.WorkflowExecutionID, request.Id, meteringRef, store.StatusCompleted, request.Method, nil)

	if meterReport != nil {
		if err = meterReport.Settle(meteringRef, capResp.Metadata); err != nil {
			execLogger.Errorw("failed to set metering for capability request", "err", err)
		}
	}
```

**File:** core/services/workflows/metering/metering.go (L371-373)
```go

		// if in metering mode, exit early without modifying local balance
		if r.meteringMode {
```

**File:** core/services/workflows/metering/metering.go (L506-510)
```go
	// Refund the difference between what local balance had been earmarked and the actual spend
	if err := r.balance.Add(step.Deduction.Sub(spentCredits)); err != nil {
		// invariant: capability should not let spend exceed reserve
		r.lggr.Info("invariant: spend exceeded reserve")
	}
```
