### Title
Silent Failure to Deduct Overspend in Workflow Metering `Report.Settle` Allows Local Credit Balance to Exceed Actual Reserved Funds - (File: `core/services/workflows/metering/metering.go`)

### Summary
`Report.Settle` computes the difference between the amount earmarked for a capability step (`step.Deduction`) and the actual reported spend (`spentCredits`), then attempts to return any unused earmark to the local balance via `r.balance.Add(step.Deduction.Sub(spentCredits))`. When actual spend exceeds the earmark, this difference is negative. `balanceStore.Add` rejects negative amounts with `ErrInvalidAmount`, and `Settle` only logs this as an informational message instead of deducting the overspend or failing safely, so the local credit balance is never reduced for the excess. [1](#0-0) [2](#0-1) 

### Finding Description
`Report.Deduct` earmarks credits from the local `balanceStore` for a capability invocation via `r.balance.Minus(bal)` (or `ByDerivedAvailability`'s `r.balance.Minus(limit.Decimal)`). [3](#0-2) [4](#0-3) 

After the capability executes, `Report.Settle` is called with the response's actual `ResponseMetadata.Metering` spend details, which are aggregated into `spentCredits`. It then attempts to refund the unused portion of the earmark:

```go
// Refund the difference between what local balance had been earmarked and the actual spend
if err := r.balance.Add(step.Deduction.Sub(spentCredits)); err != nil {
    // invariant: capability should not let spend exceed reserve
    r.lggr.Info("invariant: spend exceeded reserve")
}
```

If `spentCredits > step.Deduction` (actual usage reported by the capability/DON exceeds the earmark), `step.Deduction.Sub(spentCredits)` is negative. `balanceStore.Add` explicitly rejects negative amounts:

```go
func (bs *balanceStore) Add(amount decimal.Decimal) error {
    ...
    if amount.LessThan(decimal.Zero) {
        return ErrInvalidAmount
    }
    bs.balance = bs.balance.Add(amount)
    return nil
}
```

Because the error is swallowed with only a log line, the local `balance` is never decremented by the excess spend. Since `r.balance.Get()` directly drives `getMaxSpendForInvocation`, which computes the credit budget available for subsequent capability calls in the same workflow execution, the local balance ends up artificially inflated relative to what was actually consumed. [5](#0-4) 

This breaks the intended invariant "capability should not let spend exceed reserve": rather than failing closed (switching to metering mode) or correctly deducting the overspend, the code fails open, silently leaving extra apparent balance for further `Deduct` calls within the same execution.

### Impact Explanation
A capability/DON response that reports `SpendValue`/`SpendValueInGasUnits` metering data exceeding the amount earmarked for that step causes the local credit-balance accounting to desynchronize from actual consumption. Subsequent `Deduct` calls in the same workflow execution (via `ByResource` or `ByDerivedAvailability`) will see a higher available balance than truly remains, allowing further capability invocations to be authorized beyond the credits that were actually reserved from the billing service for that execution (`Reserve`/`ReserveCredits`). This is a quota-bypass in the per-execution credit-enforcement path: it lets a workflow execution draw more capability calls/resources than its reserved credit limit permits, even though the correct total (`GetSpent`) is still eventually reported in the receipt. [6](#0-5) 

### Likelihood Explanation
Reaching this path only requires a normal workflow execution flow: `Reserve` → repeated `Deduct`/`Settle` cycles per capability step, which is the standard v2 engine metering loop for every workflow execution triggered by a workflow owner. Any capability invocation (including capabilities whose reported spend can be influenced by execution parameters or by a capability implementation returning inflated `SpendValue`) that settles with `spentCredits` greater than its earmarked `Deduction` triggers the silent failure automatically — no privileged access or special conditions are needed beyond normal workflow execution.

### Recommendation
In `Report.Settle`, handle the overspend case explicitly instead of only logging on `Add` failure:
- If `spentCredits > step.Deduction`, deduct the excess directly from the balance (e.g., call `r.balance.Minus(spentCredits.Sub(step.Deduction))`), or
- Treat this condition as fatal for local accounting purposes and call `r.switchToMeteringMode(...)` so the report stops relying on a now-untrustworthy local balance, consistent with the fail-safe pattern already used elsewhere in this file.

Either fix ensures `r.balance` accurately reflects real remaining reserved credits, preventing subsequent `Deduct` calls from being incorrectly authorized.

### Proof of Concept
1. Workflow execution calls `Report.Reserve` and is granted a fixed local credit balance.
2. `Report.Deduct("stepA", ByResource(...))` earmarks `X` credits, reducing `balance` by `X` via `Minus`.
3. The capability response for `stepA` reports `ResponseMetadata.Metering` with an aggregated spend `Y > X` (e.g., a capability/DON reports higher `SpendValue` than what was earmarked).
4. `Report.Settle("stepA", metadata)` computes `spentCredits = Y` and calls `r.balance.Add(X.Sub(Y))`, i.e., `Add(negative)`, which returns `ErrInvalidAmount` and is only logged — `balance` is left unchanged instead of being reduced by `Y - X`.
5. A subsequent `Report.Deduct("stepB", ByDerivedAvailability(...))` reads `r.balance.Get()` (still inflated by `Y - X`), permitting `stepB` to reserve more credits than the workflow's actual remaining reserved budget allows. [7](#0-6)

### Citations

**File:** core/services/workflows/metering/metering.go (L325-339)
```go
		bal, err := r.balance.ConvertToBalance(spendType, amount)
		if err != nil {
			// Fail open, continue optimistically
			r.switchToMeteringMode(fmt.Errorf("failed to convert to balance [%s]: %w", spendType, err))
		}

		step.Deduction = bal

		// if in metering mode, exit early without modifying local balance
		if r.meteringMode {
			return []capabilities.SpendLimit{}, nil
		}

		return []capabilities.SpendLimit{}, r.balance.Minus(bal)
	}
```

**File:** core/services/workflows/metering/metering.go (L361-379)
```go
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

**File:** core/services/workflows/metering/metering.go (L403-514)
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
```

**File:** core/services/workflows/metering/metering.go (L632-653)
```go
func (r *Report) SendReceipt(ctx context.Context) error {
	if !r.reserved {
		return ErrNoReserve
	}

	if r.client == nil {
		return ErrNoBillingClient
	}

	r.metrics.UpdateWorkflowMeteringModeGauge(ctx, r.isMeteringMode())

	// TODO: https://smartcontract-it.atlassian.net/browse/CRE-427 more robust check of billing service health

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

**File:** core/services/workflows/metering/metering.go (L826-854)
```go
func (r *Report) getMaxSpendForInvocation(
	userSpendLimit decimal.NullDecimal,
	openConcurrentCallSlots int,
) (decimal.NullDecimal, error) {
	nullCapSpendLimit := decimal.NewNullDecimal(decimal.Zero)
	nullCapSpendLimit.Valid = false

	if openConcurrentCallSlots == 0 {
		// invariant: this should be managed by the consumer (engine)
		return nullCapSpendLimit, ErrNoOpenCalls
	}

	if !r.reserved {
		return nullCapSpendLimit, ErrNoReserve
	}

	if r.meteringMode {
		return nullCapSpendLimit, nil
	}

	// Split the available local balance between the number of concurrent calls that can still be made
	spendLimit := r.balance.Get().Div(decimal.NewFromInt(int64(openConcurrentCallSlots)))

	if userSpendLimit.Valid {
		spendLimit = decimal.Min(spendLimit, userSpendLimit.Decimal)
	}

	return decimal.NewNullDecimal(spendLimit), nil
}
```

**File:** core/services/workflows/metering/balance_store.go (L171-183)
```go
// Add increases the current credit balance.
func (bs *balanceStore) Add(amount decimal.Decimal) error {
	bs.mu.Lock()
	defer bs.mu.Unlock()

	if amount.LessThan(decimal.Zero) {
		return ErrInvalidAmount
	}

	bs.balance = bs.balance.Add(amount)

	return nil
}
```
