### Title
Deducted metering balance is never refunded when a capability execution fails - ([File: core/services/workflows/v2/capability_executor.go])

### Summary
In `callCapability`, the workflow engine earmarks (subtracts) credits from a workflow's local metering balance via `meterReport.Deduct(...)` *before* invoking the target capability. `Settle`, the only code path that reconciles the earmarked amount back against actual spend, is only called on the success path. If `capability.Execute` returns an error, the function returns early and `meterReport.Settle` is never called, so the deducted credits are permanently lost even though no capability work was billed/performed — the same "decrement state even though the downstream action failed" pattern as the referenced Aleph Zero Bridge finding on `pocket_money_balance`.

### Finding Description
`callCapability` deducts from the workflow's credit balance before executing the capability: [1](#0-0) 

This calls into `ByDerivedAvailability`, which immediately calls `r.balance.Minus(limit.Decimal)`, subtracting the earmarked amount from the in-memory balance store: [2](#0-1) 

The capability is then executed, and if it returns an error (either a `caperrors.Error` of user or system origin, or any other error), the function returns immediately without calling `Settle`: [3](#0-2) 

`Settle` — the only function that computes the real spend and refunds the difference between the earmarked deduction and the actual spend — is only invoked in the success path after `capability.Execute` returns without error: [4](#0-3) 

The refund logic itself lives in `Settle`, confirming that only `Settle` restores unused earmarked balance: [5](#0-4) 

Because `Settle` is never reached on any execution failure of the capability, the amount deducted by `Deduct`/`ByDerivedAvailability` is never returned to the workflow's balance. This mirrors the reported bug class exactly: a balance-affecting operation is decremented unconditionally, while the corresponding downstream action (in Hats: fund transfer; here: capability execution/billing) can fail without the state change being reverted.

### Impact Explanation
Every failed capability call (a capability configuration error, a rate-limited/timed-out call, a transient system error from a capability, or any user error returned by a capability) permanently burns the earmarked credits for that call from the workflow's local balance, without the corresponding capability work being metered or billed via `SubmitWorkflowReceipt`/`Settle`. Since `ByDerivedAvailability` can earmark "all of available balance" for a single slot (as shown by the metering tests), a single failing capability call can consume a workflow's entire remaining credit balance, causing subsequent legitimate capability calls in the same execution to fail with `ErrInsufficientBalance`, or causing over-billing/wrongful balance loss to the workflow owner. This is a fund/accounting integrity issue reachable by any workflow owner whose workflow calls a capability that can fail (including capabilities not fully controlled by the owner, e.g. timeouts or transient system errors), i.e., reachable from normal, unprivileged workflow execution — not requiring a malicious node or operator action.

### Likelihood Explanation
High. Capability calls fail routinely in production for benign reasons (timeouts via `CapabilityCallTime.WithTimeout`, transient system errors, capability-specific rate limits, user input errors). Every one of these ordinary failure conditions triggers the unrefunded-deduction path, since the early `return nil, err` in the error-handling block at lines 260-281 unconditionally skips the `Settle` call.

### Recommendation
Ensure `meterReport.Settle` (or an explicit refund of the earmarked amount) is invoked on every exit path of `callCapability`, not just the success path — e.g., via a `defer` guarded by whether `Deduct` succeeded, calling `Settle` with an empty/zero `ResponseMetadata` (or a dedicated "cancel/refund" method on `Report`) whenever `capability.Execute` returns an error, so the full earmarked deduction is returned to the local balance when no metered spend actually occurred.

### Proof of Concept
1. A workflow calls a capability with metering enabled (`meterReport != nil`), reserved balance > 0.
2. `callCapability` calls `meterReport.Deduct(meteringRef, metering.ByDerivedAvailability(...))`, which subtracts a portion (or all, if `openConcurrentCallSlots == 1`) of the available balance from `r.balance` via `Minus`.
3. `capability.Execute` fails for any reason (e.g., the capability capability returns a `caperrors.Error` with `OriginUser`, simulating a bad user configuration, or simply times out).
4. Execution enters the `if err != nil` branch (lines 260-281) and returns without ever calling `meterReport.Settle`.
5. Inspecting `meterReport.balance` after the call shows the earmarked amount has been permanently subtracted; no corresponding `ReportStep.Spends` were recorded, and no refund of the unused earmark ever occurs before `SendReceipt` totals up `CreditsConsumed`, which will over-report/consume credits versus true resource usage. [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** core/services/workflows/v2/capability_executor.go (L199-290)
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
	}

	capReq := capabilities.CapabilityRequest{
		Payload:      request.Payload,
		Method:       request.Method,
		CapabilityId: request.Id,
		Metadata: capabilities.RequestMetadata{
			WorkflowOwner:            c.cfg.WorkflowOwner,
			WorkflowID:               c.cfg.WorkflowID,
			WorkflowExecutionID:      c.WorkflowExecutionID,
			WorkflowName:             c.cfg.WorkflowName.Hex(),
			WorkflowDonID:            localNode.WorkflowDON.ID,
			WorkflowDonConfigVersion: pinnedWorkflowDonConfigVersion,
			ReferenceID:              strconv.Itoa(int(request.CallbackId)),
			DecodedWorkflowName:      c.cfg.WorkflowName.String(),
			SpendLimits:              spendLimits,
			WorkflowTag:              c.cfg.WorkflowTag,
			ExecutionTimestamp:       c.ExecutionTimestamp,
		},
		Config: values.EmptyMap(),
	}
	var creGetter settings.Getter
	if c.cfg.LocalLimiters != nil {
		creGetter = c.cfg.LocalLimiters.Settings
	}
	propagateOrgIDMeta, _ := cresettings.Default.PropagateOrgIDInRequestMetadata.GetOrDefault(ctx, creGetter)
	if propagateOrgIDMeta && c.orgID != "" {
		capReq.Metadata.OrgID = c.orgID
	}

	execLogger.Debug("Executing capability ...")
	c.metrics.With(platform.KeyCapabilityID, request.Id).IncrementCapabilityInvocationCounter(ctx)
	loggerLabels := c.eventLabels()
	_ = events.EmitCapabilityStartedEvent(ctx, loggerLabels, c.WorkflowExecutionID, request.Id, meteringRef, request.Method)

	execCtx, execCancel, err := c.cfg.LocalLimiters.CapabilityCallTime.WithTimeout(ctx)
	if err != nil {
		return nil, err
	}
	defer execCancel()

	executionStart := c.cfg.Clock.Now()
	c.executionProfile.recordStepStart(meteringRef, request.Id, executionStart)

	capResp, err := capability.Execute(execCtx, capReq)
	executionEnd := c.cfg.Clock.Now()
	executionDuration := executionEnd.Sub(executionStart)
	c.executionProfile.recordStepEnd(meteringRef, executionEnd, err != nil)

	c.metrics.With(platform.KeyCapabilityID, request.Id).UpdateCapabilityExecutionDurationHistogram(ctx, int64(executionDuration.Seconds()))
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

	execLogger.Debug("Capability execution succeeded")
	_ = events.EmitCapabilityFinishedEvent(ctx, loggerLabels, c.WorkflowExecutionID, request.Id, meteringRef, store.StatusCompleted, request.Method, nil)

	if meterReport != nil {
		if err = meterReport.Settle(meteringRef, capResp.Metadata); err != nil {
			execLogger.Errorw("failed to set metering for capability request", "err", err)
		}
	}
```

**File:** core/services/workflows/metering/metering.go (L342-379)
```go
// ByDerivedAvailability returns a DeductOpt that derives the maximum spend limit based on the user spend limit and
// the number of open concurrent call slots.
func ByDerivedAvailability(
	userSpendLimit decimal.NullDecimal,
	openConcurrentCallSlots int,
	info capabilities.CapabilityInfo,
	config *values.Map,
) func(string, *Report) ([]capabilities.SpendLimit, error) {
	return func(ref string, r *Report) ([]capabilities.SpendLimit, error) {
		step := ReportStep{
			CapabilityID:     info.ID,
			Deduction:        decimal.Zero,
			AggregatedSpends: make(map[string]AggregatedStepDetail),
		}

		defer func() {
			r.steps[ref] = step
		}()

		limit, err := r.getMaxSpendForInvocation(userSpendLimit, openConcurrentCallSlots)
		if err != nil {
			return nil, err
		}

		if !limit.Valid {
			return []capabilities.SpendLimit{}, nil
		}

		step.Deduction = limit.Decimal

		// if in metering mode, exit early without modifying local balance
		if r.meteringMode {
			return []capabilities.SpendLimit{}, nil
		}

		return r.creditToSpendingLimits(info, config, limit.Decimal), r.balance.Minus(limit.Decimal)
	}
}
```

**File:** core/services/workflows/metering/metering.go (L403-422)
```go
// Settle handles the actual spends that each node used for a given capability invocation in the engine,
// by returning earmarked local balance to the available to use pool and adding the spend to the metering report.
// The Deduct method must be called before Settle.
// We expect to only set this value once - an error is returned if a step would be overwritten.
func (r *Report) Settle(ref string, metadata capabilities.ResponseMetadata) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if !r.reserved {
		return ErrNoReserve
	}

	step, ok := r.steps[ref]
	if !ok {
		return ErrNoDeduct
	}

	if step.Spends != nil {
		return ErrStepSpendExists
	}
```

**File:** core/services/workflows/metering/metering.go (L501-515)
```go
	// if in metering mode, exit early without modifying local balance
	if r.meteringMode {
		return nil
	}

	// Refund the difference between what local balance had been earmarked and the actual spend
	if err := r.balance.Add(step.Deduction.Sub(spentCredits)); err != nil {
		// invariant: capability should not let spend exceed reserve
		r.lggr.Info("invariant: spend exceeded reserve")
	}

	r.balance.AddSpent(spentCredits)

	return nil
}
```
