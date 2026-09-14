## Finding [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Metering credits earmarked by `Deduct` are never refunded or recorded as spent when a capability call fails after deduction - ([File: core/services/workflows/v2/capability_executor.go])

### Summary
`callCapability` earmarks (deducts) local execution balance for a capability call via `meterReport.Deduct(...)` *before* invoking the capability, but only calls the corresponding `meterReport.Settle(...)` on the success path. Every failure exit after `Deduct` (capability-call-time-limiter error, user error, system error, generic execute error) returns without ever calling `Settle`, so the earmarked credits are permanently subtracted from the workflow execution's local balance but never refunded and never counted in the billing "spent" total. This directly parallels the Nibiru `call_contract.go` bug class: the success path performs proper reconciliation, but the failure path silently skips it, producing a persistent mismatch between what was actually deducted and what is accounted for.

### Finding Description
In `capability_executor.go`, `meterReport.Deduct(meteringRef, metering.ByDerivedAvailability(...))` is called at [4](#0-3)  before the capability is executed. `Deduct`/`ByDerivedAvailability` immediately calls `r.balance.Minus(limit.Decimal)`, permanently reducing the in-memory execution balance [5](#0-4) .

The only code path that reconciles this earmark is `Report.Settle`, which both refunds the unused difference back to the balance and adds the actually-spent amount to the cumulative "spent" tracker used for billing:
```go
// Refund the difference between what local balance had been earmarked and the actual spend
if err := r.balance.Add(step.Deduction.Sub(spentCredits)); err != nil {
    r.lggr.Info("invariant: spend exceeded reserve")
}
r.balance.AddSpent(spentCredits)
``` [6](#0-5) 

However, in `callCapability`, `Settle` is only invoked on the success path, at the very end of the function:
```go
if meterReport != nil {
    if err = meterReport.Settle(meteringRef, capResp.Metadata); err != nil {
        execLogger.Errorw("failed to set metering for capability request", "err", err)
    }
}
``` [7](#0-6) 

Every failure branch after `Deduct` returns early without calling `Settle`:
- `CapabilityCallTime.WithTimeout` error [8](#0-7) 
- Capability user error, system error, and generic execution error [9](#0-8) 

As a result, whenever a capability call fails after deduction has occurred, the earmarked amount (`step.Deduction`) is neither refunded to `r.balance` nor added to `r.balance.spent`. It is effectively "lost" from the local balance tracker for the remainder of the workflow execution, while `SendReceipt` bills the workflow owner based on `r.balance.GetSpent()` [10](#0-9) , which never reflects this deducted-but-unsettled amount.

### Impact Explanation
This is directly analogous to the referenced gas-accounting bug: the success path performs the "add to cumulative/settle" step but the failure path does not, causing a persistent mismatch between the internal balance ledger and what is actually billed/tracked. Concretely:
- The workflow execution's remaining local balance is permanently reduced by the earmarked-but-never-refunded amount after every failing capability call, which can cause subsequent legitimate capability calls in the same execution to spuriously hit `ErrInsufficientBalance` (a self-inflicted denial of budget within the execution) even though the workflow owner was never actually charged for that spend.
- Simultaneously, the amount is never added via `AddSpent`, so `CreditsConsumed` sent to the billing service in `SubmitWorkflowReceipt` undercounts actual resource usage whenever failures occur after deduction, producing a wrong deduction/billing mismatch consistent with the reported bug class.

This is reachable by any unprivileged workflow owner simply by having a workflow invoke a capability that can fail after the metering deduction step (timeouts, capability errors, etc.), which is a normal and common occurrence, not a privileged or malicious-node condition.

### Likelihood Explanation
High. Capability execution failures (timeouts via `CapabilityCallTime`, capability user/system errors) are routine occurrences in production workflow executions, not edge cases requiring special conditions, so this incorrect accounting will trigger frequently in practice.

### Recommendation
Ensure `meterReport.Settle` (or an equivalent reconciliation/refund call) is invoked on every exit path after `Deduct` succeeds, including the `CapabilityCallTime.WithTimeout` error path and all three error branches in the post-`Execute` error handling, mirroring how the success path settles the earmarked balance. Consider using `defer` immediately after a successful `Deduct` call to guarantee settlement/refund regardless of how `callCapability` returns.

### Proof of Concept
1. Configure a workflow with a billing client so metering is active (`meterReport != nil`).
2. Invoke a capability whose `Execute` call returns an error (e.g., simulate a `caperrors.Error` with `OriginUser`, or force `CapabilityCallTime.WithTimeout` to fail).
3. Observe that `meterReport.Deduct` was called (reducing `r.balance`) at [4](#0-3) , but the corresponding `Settle` call at [7](#0-6)  is skipped because the function returns earlier in the error branch.
4. Inspect `r.balance.Get()` after the failed call: it is reduced by `step.Deduction` and never refunded, while `r.balance.GetSpent()` does not reflect this amount — reproducible directly via `Report.Deduct` followed by a failure that skips `Report.Settle`, as demonstrated by the existing test helpers in `core/services/workflows/metering/metering_test.go` (e.g. `Test_Report_Settle`), which show `Settle` is the sole place performing the refund/`AddSpent` reconciliation.

### Citations

**File:** core/services/workflows/v2/capability_executor.go (L188-210)
```go
	if meterReport != nil {
		// TODO: https://smartcontract-it.atlassian.net/browse/CRE-285 get max spend per step from SDK.
		// TODO: https://smartcontract-it.atlassian.net/browse/CRE-284 parse user max spend for step
		userSpendLimit := decimal.NewNullDecimal(decimal.Zero)
		userSpendLimit.Valid = false

		var openConcurrentCallSlots int
		if openConcurrentCallSlots, err = c.cfg.LocalLimiters.CapabilityConcurrency.Available(ctx); err != nil {
			return nil, err
		}

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
```

**File:** core/services/workflows/v2/capability_executor.go (L245-297)
```go
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

	return &sdkpb.CapabilityResponse{
		Response: &sdkpb.CapabilityResponse_Payload{
			Payload: capResp.Payload,
		},
	}, nil
}
```

**File:** core/services/workflows/metering/metering.go (L370-378)
```go
		step.Deduction = limit.Decimal

		// if in metering mode, exit early without modifying local balance
		if r.meteringMode {
			return []capabilities.SpendLimit{}, nil
		}

		return r.creditToSpendingLimits(info, config, limit.Decimal), r.balance.Minus(limit.Decimal)
	}
```

**File:** core/services/workflows/metering/metering.go (L403-515)
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

	spentCredits := decimal.NewFromInt(0)
	resourceSpends := make(map[string][]ReportStepDetail)

	// Group by resource dimension
	for _, nodeDetail := range metadata.Metering {
		resourceSpends[nodeDetail.SpendUnit] = append(resourceSpends[nodeDetail.SpendUnit], ReportStepDetail{
			Peer2PeerID:          nodeDetail.Peer2PeerID,
			SpendValue:           nodeDetail.SpendValue,
			SpendValueInGasUnits: nodeDetail.SpendValueInGasUnits,
			CRESpendValue:        decimal.Zero,
		})
	}

	// Aggregate node responses to a single number
	for unit, spendDetails := range resourceSpends {
		aggregated := AggregatedStepDetail{
			SpendUnit:  unit,
			SpendValue: decimal.Zero,
		}

		deciVals := []decimal.Decimal{}
		for idx, detail := range spendDetails {
			value, err := r.parseSpendValue(unit, detail)
			if err != nil {
				// throw out invalid values for local balance settlement. they will still be included in metering report.
				continue
			}

			if val, convertErr := r.balance.ConvertToBalance(unit, value); convertErr == nil {
				resourceSpends[unit][idx].CRESpendValue = val
			}

			deciVals = append(deciVals, value)

			if isGasSpendType(unit) && len(deciVals) > 1 {
				r.switchToMeteringMode(fmt.Errorf("multiple executions for single execution unit [%s]: %w", unit, err))
			}
		}

		// TODO: explicitly ignore RPC_EVM spend types for now -
		// this check causes TestEngine_Metering_ValidBillingClient/billing_type_and_capability_settle_spend_type_mismatch ./core/services/workflows/v2
		// to fail because the capability is returning a spend type that isn't gas or compute
		// This should be removed when we have proper support for non-gas/compute spend types
		if unit == "RPC_EVM" {
			continue
		}

		aggregated.SpendValue = medianSpend(deciVals)
		value := aggregated.SpendValue

		// if N is not set, assume 1
		if metadata.CapDON_N == 0 {
			metadata.CapDON_N = 1
		}

		// TODO: indicate in the registry config that a capability is single execution or not
		// https://smartcontract-it.atlassian.net/browse/CRE-1037
		if !isGasSpendType(unit) {
			value = value.Mul(decimal.NewFromUint64(uint64(metadata.CapDON_N)))
		}

		bal, err := r.balance.ConvertToBalance(unit, value)

		if err != nil {
			r.switchToMeteringMode(fmt.Errorf("attempted to Settle [%s]: %w", unit, err))
		} else {
			aggregated.CRESpendValue = bal
			spentCredits = spentCredits.Add(bal)
		}

		step.AggregatedSpends[unit] = aggregated
	}

	step.Spends = resourceSpends
	step.CapdonN = metadata.CapDON_N
	r.steps[ref] = step

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

**File:** core/services/workflows/metering/metering.go (L645-653)
```go
	req := billing.SubmitWorkflowReceiptRequest{
		WorkflowOwner:                 r.labels[platform.KeyWorkflowOwner],
		WorkflowId:                    r.labels[platform.KeyWorkflowID],
		WorkflowExecutionId:           r.labels[platform.KeyWorkflowExecutionID],
		WorkflowRegistryAddress:       r.workflowRegistryAddress,
		WorkflowRegistryChainSelector: r.workflowRegistryChainSelector,
		Metering:                      r.FormatReport(),
		CreditsConsumed:               r.balance.GetSpent().String(),
	}
```
