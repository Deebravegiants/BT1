Analysis of the metering/balance accounting code reveals an analogous sign-handling bug to the Llama `totalQuantity` issue: the code computes a difference correctly but silently drops the "decrease" case instead of applying it, causing the tracked value to end up wrong (never correctly decremented when it should be).

### Title
Incorrect local credit-balance decrement on capability overspend allows workflow quota bypass - ([File: core/services/workflows/metering/metering.go])

### Summary
`Report.Settle` refunds unused earmarked credits by computing `step.Deduction.Sub(spentCredits)` and passing the result to `balanceStore.Add`. `Add` rejects any negative amount with `ErrInvalidAmount` and performs no balance mutation in that case [1](#0-0) . When actual capability spend (`spentCredits`) exceeds the amount earmarked at `Deduct` time (`step.Deduction`), the difference is negative, `Add` is a no-op, and the error is only logged, never decrementing the local balance for the overage [2](#0-1) .

### Finding Description
Just like the Llama `_setRoleHolder` bug — where `quantityDiff` was computed with a magnitude-only subtraction but then always *added* regardless of whether the true change was an increase or a decrease — this code computes a signed difference (`Deduction - spentCredits`) that is meant to represent either a refund (positive, spend under budget) or an implicit additional charge (negative, spend over budget), but only the "increase" (refund) branch is actually implemented. The "decrease" branch (charging the local balance for the overage) is effectively dropped because `balanceStore.Add` validates `amount.LessThan(decimal.Zero)` and returns early without mutating `bs.balance`: [3](#0-2) 

Meanwhile `AddSpent` unconditionally records the *true* `spentCredits` (not capped to `Deduction`) into `bs.spent`, which is what eventually gets reported via `SubmitWorkflowReceipt`/`CreditsConsumed` [4](#0-3) [5](#0-4) . But the local `bs.balance`, which is the value consulted by `getMaxSpendForInvocation` to gate how much can still be spent in the *current* workflow execution, is only ever decremented by the (smaller) earmarked `Deduction`, never by the true overspend: [6](#0-5) 

The effect: whenever a capability invocation's actual reported spend exceeds what was earmarked for it (e.g. `ByDerivedAvailability`'s pre-execution estimate turning out lower than the real cost), the workflow's remaining local credit balance is left higher than it should truly be. Subsequent `Deduct` calls in the same execution see an inflated available balance and can authorize further capability calls that should have been blocked.

### Impact Explanation
This is a quota/spend-limit bypass within a single workflow execution: a workflow owner (an otherwise unprivileged CRE actor who merely registers/runs a workflow) can consume more capability invocations than their reserved credit allocation should allow, because the internal balance tracker fails to apply the "decrease" side of the diff when overspend occurs. It does not grant secret/key disclosure or authentication bypass, but it is a concrete violation of the fund/quota-accounting invariant ("capability should not let spend exceed reserve" — the exact invariant the code's own comment references at line 508-509).

### Likelihood Explanation
Triggering this requires a capability invocation whose actual reported spend (after execution) exceeds the amount earmarked via `Deduct` before execution — plausible whenever costs are estimated ahead of time (`ByDerivedAvailability`) and real usage varies (e.g., gas price/computation cost fluctuation) or a capability node over-reports spend. No special privilege is needed; any workflow execution that hits this condition organically triggers the under-decrement.

### Recommendation
`Settle` should not rely on `Add` silently rejecting negative refunds. Explicitly branch on the sign of `step.Deduction.Sub(spentCredits)`: call `Add` for the positive (refund) case and call `Minus`/`MinusAs` for the negative (overspend) case, mirroring the corrected Llama pattern of separate increase/decrease handling rather than a single always-add operation.

### Proof of Concept
1. A workflow step calls `Deduct(ref, ByDerivedAvailability(...))`, earmarking `Deduction = 10` credits (`balance.Minus(10)` executes, reducing local balance by 10).
2. The capability actually reports spend metadata that, after conversion, yields `spentCredits = 15` (exceeds the earmark).
3. `Settle` computes `step.Deduction.Sub(spentCredits) = 10 - 15 = -5` and calls `r.balance.Add(-5)`, which returns `ErrInvalidAmount` and performs no mutation [1](#0-0) ; only `r.lggr.Info("invariant: spend exceeded reserve")` is logged.
4. `r.balance.AddSpent(15)` still records the full 15 as "spent" for billing receipt purposes, but the local `bs.balance` was only ever reduced by the original 10 — 5 credits' worth of actual usage is unaccounted for in the local balance, leaving 5 extra credits of headroom for further `Deduct` calls in the same execution that should not have been available.

### Citations

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

**File:** core/services/workflows/metering/metering.go (L506-514)
```go
	// Refund the difference between what local balance had been earmarked and the actual spend
	if err := r.balance.Add(step.Deduction.Sub(spentCredits)); err != nil {
		// invariant: capability should not let spend exceed reserve
		r.lggr.Info("invariant: spend exceeded reserve")
	}

	r.balance.AddSpent(spentCredits)

	return nil
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

**File:** core/services/workflows/metering/metering.go (L826-853)
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
```
