### Title
Overspend by a capability step silently fails to deduct from the local credit balance, letting a workflow exceed its billing reservation - (File: core/services/workflows/metering/metering.go)

### Summary
`Report.Settle()` in `core/services/workflows/metering/metering.go` refunds the unused earmarked balance back into the local `balanceStore` after a capability step completes, computed as `step.Deduction.Sub(spentCredits)`. This mirrors the Stargate bug class: an accounting variable (`balanceStore.balance`) is assumed to always be correctly reconciled after every action, but the code path that performs the reconciliation silently no-ops when the delta is negative, leaving the tracked balance permanently overstated relative to true spend.

### Finding Description
`Deduct()` reduces the local balance by the earmarked `Deduction` amount via `balanceStore.Minus()` [1](#0-0) . Later, `Settle()` is supposed to true-up the local balance for the actual observed spend reported by capability DON nodes (`metadata.Metering`), by adding back the difference between what was earmarked and what was actually spent: [2](#0-1) 

`balanceStore.Add()` explicitly rejects negative amounts and returns `ErrInvalidAmount` without changing state: [3](#0-2) 

So whenever the aggregated `spentCredits` for a step exceeds the `Deduction` that was earmarked for it (i.e., a capability step, or an inflated/malformed spend report from a capability DON node, reports spending more than its own `SpendLimit` allowed), `step.Deduction.Sub(spentCredits)` is negative, `Add()` fails, and the code just logs `"invariant: spend exceeded reserve"` and moves on — the local balance is **not** decremented by the excess. The true total spend is still correctly tracked separately via `r.balance.AddSpent(spentCredits)` [4](#0-3)  (used for the final billing receipt), but the *local* `balance` field used to gate further in-execution spending is left artificially higher than it should be.

Because `ByDerivedAvailability`/`getMaxSpendForInvocation` derive subsequent per-step spend limits directly from `r.balance.Get()` [5](#0-4) , an inflated local balance lets later steps in the same workflow execution be granted larger spend limits than the true remaining reservation actually allows.

### Impact Explanation
This is reachable from an ordinary workflow owner's own workflow execution — no privileged access is required to trigger it, only a capability step (potentially one whose spend report can be influenced, e.g. by node/DON behavior beyond the earmarked `SpendLimit`) that returns `spentCredits > Deduction` for a step. The result is that the node-local credit-limit enforcement that is supposed to bound total spend to what was reserved from the billing service (`ReserveCredits`) can be bypassed for later steps within the same execution, since the "remaining budget" the engine consults is not corrected downward for the overspend. This is a quota/fund-accounting bypass: total spend authorized during an execution can exceed the amount actually reserved, even though the true consumed amount is still reported to the billing backend via `SubmitWorkflowReceipt`.

### Likelihood Explanation
The condition only requires one step's aggregated `spentCredits` (median of node-reported spend values) to exceed its earmarked `Deduction`. This is a soft invariant maintained by capability behavior/config, not enforced anywhere prior to `Settle()`, so any misbehaving/misconfigured capability, or one where `ByDerivedAvailability`/`ByResource` under-earmarks relative to what nodes end up reporting, will trip this path. The existing log message `"invariant: spend exceeded reserve"` shows the maintainers are aware this can happen but treat it as a logging-only event rather than a corrective one.

### Recommendation
When `step.Deduction.Sub(spentCredits)` is negative, explicitly deduct the excess from the local balance (e.g. via `balanceStore.Minus()` with the absolute value, floored at zero, or by clamping the balance to zero) instead of silently no-op'ing on `Add()`'s validation error, so that subsequent `getMaxSpendForInvocation`/`ByDerivedAvailability` calls always see a balance that reflects true remaining reservation.

### Proof of Concept
1. A workflow reserves N credits via `Reserve()`.
2. `Deduct()` earmarks `D` credits for a capability step, decrementing local balance by `D`.
3. The capability (or a subset of DON nodes reporting metering data) returns `metadata.Metering` values whose aggregated `spentCredits > D`.
4. `Settle()` computes `D - spentCredits < 0`; `balance.Add()` returns `ErrInvalidAmount`, balance is left unchanged (only decremented by `D`, not by the true `spentCredits`).
5. `r.balance.AddSpent(spentCredits)` still records the correct total for the billing receipt, but `r.balance.Get()` used by later `Deduct()` calls is now higher than the workflow's true remaining reserved budget, letting subsequent steps be granted spend limits that, in total, exceed the amount actually reserved with the billing service.

### Citations

**File:** core/services/workflows/metering/metering.go (L336-339)
```go
		}

		return []capabilities.SpendLimit{}, r.balance.Minus(bal)
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

**File:** core/services/workflows/metering/metering.go (L844-853)
```go
	}

	// Split the available local balance between the number of concurrent calls that can still be made
	spendLimit := r.balance.Get().Div(decimal.NewFromInt(int64(openConcurrentCallSlots)))

	if userSpendLimit.Valid {
		spendLimit = decimal.Min(spendLimit, userSpendLimit.Decimal)
	}

	return decimal.NewNullDecimal(spendLimit), nil
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
