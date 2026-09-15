### Title
Metering `Report.Settle` silently fails to deduct excess capability spend when a DON's reported spend exceeds the earmarked reservation - ([File: core/services/workflows/metering/metering.go])

### Summary
`Report.Settle` reconciles the credits earmarked for a capability call (`step.Deduction`, set during `Deduct`) against the actual spend reported by the capability DON (`spentCredits`, taken from `capResp.Metadata.Metering`). Analogous to the reported `YearnV2YieldSource` bug — where a `previousBalance.Sub(currentBalance)` produced a negative/underflowing value instead of the intended top-up — this code computes `step.Deduction.Sub(spentCredits)` and feeds it into `balanceStore.Add`, which explicitly rejects negative amounts. When a capability DON reports spend greater than what was earmarked, the subtraction goes negative, `Add` returns `ErrInvalidAmount`, and the local in-memory balance is **not adjusted at all** — the excess spend is neither deducted from the local balance nor otherwise accounted for beyond a debug log line.

### Finding Description
In `core/services/workflows/metering/metering.go`, `Deduct` reserves (subtracts) `step.Deduction` credits from the local `balanceStore` up front via `balanceStore.Minus` [1](#0-0) . After the capability executes, `Settle` is supposed to refund the unused portion of that earmark back to the balance:

```go
// Refund the difference between what local balance had been earmarked and the actual spend
if err := r.balance.Add(step.Deduction.Sub(spentCredits)); err != nil {
    // invariant: capability should not let spend exceed reserve
    r.lggr.Info("invariant: spend exceeded reserve")
}

r.balance.AddSpent(spentCredits)
``` [2](#0-1) 

`spentCredits` is derived entirely from `metadata.Metering`, i.e., `capResp.Metadata` returned by the external capability's `Execute` call [3](#0-2) , aggregated via `medianSpend` and converted with `ConvertToBalance` [4](#0-3) .

`balanceStore.Add` explicitly refuses negative deltas:
```go
func (bs *balanceStore) Add(amount decimal.Decimal) error {
	...
	if amount.LessThan(decimal.Zero) {
		return ErrInvalidAmount
	}
	bs.balance = bs.balance.Add(amount)
	return nil
}
``` [5](#0-4) 

When `spentCredits > step.Deduction`, `step.Deduction.Sub(spentCredits)` is negative, so `Add` is a complete no-op — the local `balance` is left exactly as it was after the original `Minus(step.Deduction)` call in `Deduct`, and the additional overage (`spentCredits - step.Deduction`) is never subtracted from `r.balance`. The code comment ("invariant: capability should not let spend exceed reserve") shows the authors assumed this could never happen, but nothing in the code path enforces that invariant against a capability response that reports a larger spend than what was reserved.

This differs from the original PoolTogether report only in that Go's `decimal` library doesn't panic/underflow like Solidity's `SafeMath` — instead of a revert, the mis-ordered subtraction silently degrades into a no-op that leaves the local ledger over-crediting the workflow.

### Impact Explanation
The local `balanceStore.balance` is the value used by `getMaxSpendForInvocation` / `ByDerivedAvailability` to gate how many additional credits subsequent capability calls within the *same* workflow execution are allowed to spend [6](#0-5) . If one capability step's DON over-reports spend beyond what was earmarked for it, that overage is never actually deducted from `r.balance`. This inflates the credit balance available for later steps in the same execution, allowing the workflow to consume more total resources/credits within the execution than what was actually reserved from the billing service (`Reserve`). Since `AddSpent` unconditionally accumulates `spentCredits` regardless of whether the local balance was correctly adjusted [7](#0-6) , the final `SendReceipt`/`CreditsConsumed` figure sent to the billing service can end up exceeding the amount originally reserved for the execution (`ReserveCredits`) [8](#0-7) , i.e., the workflow spends more credits than it was granted permission to use, without the safety valve (an error/abort) that the code comment implies should exist.

### Likelihood Explanation
Reaching this path requires a capability DON's aggregated `Metadata.Metering` spend report for a step to exceed the local `Deduction` earmark for that same step. `Deduction` for capability calls is derived from `ByDerivedAvailability` as `available balance / open concurrent call slots` (or a user-specified cap) [9](#0-8) , a value entirely computed client-side and not enforced as a hard ceiling on the capability's actual behavior — a capability (which can be an externally hosted/third-party capability reachable from a workflow) simply reports its own `SpendValue`, which the local node trusts without capping it to the earmarked amount before calling `Settle`. This makes the condition reachable by any workflow/capability combination where the capability's actual resource usage (e.g., gas, compute) legitimately or maliciously exceeds the pre-computed availability estimate — a realistic scenario for capabilities with variable/unpredictable cost (e.g., gas-priced chain writes) rather than requiring an adversarial peer/node compromise.

### Recommendation
In `Report.Settle`, do not silently drop the balance adjustment when `spentCredits > step.Deduction`. Clamp the refund to zero (rather than skip the whole update) and separately deduct the additional overage from `r.balance` (allowing it to go to zero, or explicitly switching to metering mode / hard failure if it would go negative), e.g.:
```go
diff := step.Deduction.Sub(spentCredits)
if diff.IsNegative() {
    // Overage: draw down further from balance instead of no-op.
    if err := r.balance.Minus(diff.Neg()); err != nil {
        r.switchToMeteringMode(fmt.Errorf("spend exceeded reserve: %w", err))
    }
} else if err := r.balance.Add(diff); err != nil {
    r.lggr.Info("invariant: spend exceeded reserve")
}
```
This ensures the in-memory balance used to gate subsequent steps' spend limits is always correctly reduced by the true reported spend, closing the gap that lets a workflow consume more billed credits than were reserved.

### Proof of Concept
1. Start a workflow execution; `Report.Reserve` sets `r.balance` to the reserved credits (e.g., 100).
2. Step A calls `Deduct` via `ByDerivedAvailability`, earmarking e.g. 10 credits (`step.Deduction = 10`), which reduces `r.balance` to 90 via `Minus(10)`.
3. The invoked capability's `Execute` response returns `Metadata.Metering` with a `SpendValue` that converts to 50 credits (exceeding the 10-credit earmark) — this is entirely determined by the (possibly external/third-party) capability implementation, not validated against the earmark before being trusted.
4. `Settle` computes `spentCredits = 50`, `step.Deduction.Sub(spentCredits) = 10 - 50 = -40`.
5. `r.balance.Add(-40)` returns `ErrInvalidAmount`; `r.balance` remains 90 (only reduced by the original 10-credit earmark, not by the additional 40 credits actually spent).
6. `r.balance.AddSpent(50)` records spent=50, but the *available* local balance (90) is 40 credits higher than it should be (should be 50: 100 - 50 actually spent), letting subsequent steps in the same execution spend up to 40 extra credits' worth of resources that were never actually reserved.

### Citations

**File:** core/services/workflows/metering/metering.go (L330-339)
```go

		step.Deduction = bal

		// if in metering mode, exit early without modifying local balance
		if r.meteringMode {
			return []capabilities.SpendLimit{}, nil
		}

		return []capabilities.SpendLimit{}, r.balance.Minus(bal)
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

**File:** core/services/workflows/metering/metering.go (L437-495)
```go
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
```

**File:** core/services/workflows/metering/metering.go (L506-512)
```go
	// Refund the difference between what local balance had been earmarked and the actual spend
	if err := r.balance.Add(step.Deduction.Sub(spentCredits)); err != nil {
		// invariant: capability should not let spend exceed reserve
		r.lggr.Info("invariant: spend exceeded reserve")
	}

	r.balance.AddSpent(spentCredits)
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

**File:** core/services/workflows/v2/capability_executor.go (L286-290)
```go
	if meterReport != nil {
		if err = meterReport.Settle(meteringRef, capResp.Metadata); err != nil {
			execLogger.Errorw("failed to set metering for capability request", "err", err)
		}
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
