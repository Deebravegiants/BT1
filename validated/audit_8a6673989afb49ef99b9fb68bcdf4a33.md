Audit Report

## Title
Incorrect local credit-balance decrement on capability overspend allows workflow quota bypass - ([File: core/services/workflows/metering/metering.go])

## Summary
`Report.Settle` refunds unused earmarked credits by computing `step.Deduction.Sub(spentCredits)` and passing it to `balanceStore.Add`, which explicitly rejects negative amounts and performs no mutation in that case [1](#0-0) . When actual spend exceeds the earmarked `step.Deduction`, this diff is negative, so `Add` is a no-op and only a log line is emitted, while `AddSpent` still unconditionally records the full true spend [2](#0-1) .

## Finding Description
`Settle` is meant to true-up the local balance after a capability call completes: refund the excess if spend was under the earmark, or charge the local balance for the extra amount if spend exceeded the earmark. Only the refund branch works, because it is implemented via a single `Add` call whose sign is not checked before calling it: [3](#0-2)  When `spentCredits > step.Deduction`, `Add` receives a negative amount, hits its `LessThan(decimal.Zero)` guard, returns `ErrInvalidAmount`, and never mutates `bs.balance` [4](#0-3) . Meanwhile `bs.spent` is always incremented by the true `spentCredits` value via `AddSpent`, which feeds into the billing receipt's `CreditsConsumed` field, so the amount ultimately billed/reported for the workflow execution is correct [5](#0-4) . The bug is confined to `bs.balance`, the value read by `getMaxSpendForInvocation` to gate how much can still be spent for subsequent capability calls within the *same* execution [6](#0-5) .

I verified the `balance_store.go` code and the `Settle` snippet exactly as cited; the sign-check omission is real and matches the described mechanics. However, I was unable to locate and review the `Deduct` function and the `ByDerivedAvailability` earmarking logic in this session (searches for `func (r *Report) Deduct` and `ByDerivedAvailability` inside `metering.go` did not resolve, despite one match reported by an initial grep), so I cannot confirm from the code itself how the earmark (`step.Deduction`) is derived, how tightly it is normally expected to bound `spentCredits`, or whether there is a compensating check elsewhere (e.g., a hard total-reserve ceiling checked independently of `bs.balance`) that would prevent the "inflated headroom" from actually enabling extra unauthorized capability invocations.

## Impact Explanation
If the claim's mechanics are accurate (which the code I could read supports), this is a within-execution quota-accounting bug: the tracked local balance is not properly decremented when real spend exceeds the pre-execution estimate, potentially leaving artificially inflated headroom for further capability calls in the same workflow execution. This does not affect the amount actually billed/reported (`CreditsConsumed`/`bs.spent` is unaffected and correct), so there's no fund-movement or billing-record corruption — the only affected value is an in-memory execution-time spend gate. Given that the real spend accounting used for billing is unaffected, and I could not confirm the magnitude, exploitability, or reachability of the "extra capability calls" scenario (I could not verify how `Deduct`/`ByDerivedAvailability` bound realistic overspend deltas, nor find any test coverage exercising this negative-diff branch), I cannot confirm this rises to a concrete, exploitable, in-scope impact (e.g., unauthorized job run or fund movement) rather than a minor internal accounting inconsistency with unclear real-world consequence.

## Likelihood Explanation
Unconfirmed. Triggering requires a capability invocation whose real reported spend organically exceeds its pre-execution earmark — this could occur without attacker action (e.g., gas price fluctuation), but I could not verify from the code how large such deltas typically are, how many extra capability calls (if any) this would actually unlock, or whether other guards (e.g., a global reserve limit checked independently) would still block genuinely unauthorized spend.

## Recommendation
`Settle` should branch explicitly on the sign of `step.Deduction.Sub(spentCredits)`, calling `Add` for the refund case and `Minus`/`MinusAs` for the overspend case, instead of relying on `Add`'s negative-amount rejection.

## Proof of Concept
Not independently verified end-to-end. A Go unit test would need to: (1) call `Deduct` with a `ByDerivedAvailability`-style earmark to set `step.Deduction`, (2) call `Settle` with `spendDetails` producing `spentCredits > step.Deduction`, (3) assert `bs.balance` is decremented by the overage (currently it is not, per [3](#0-2)  and [1](#0-0) ), and (4) demonstrate a subsequent `Deduct`/`getMaxSpendForInvocation` call authorizing spend it should not have. I was unable to construct or confirm step (4) within this session due to incomplete visibility into `Deduct`/`ByDerivedAvailability` and existing test coverage.

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
