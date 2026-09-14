### Title
Metering `Report.Settle()` fails to debit local credit balance when actual capability spend exceeds the earmarked deduction, creating phantom balance for subsequent workflow steps - (File: `core/services/workflows/metering/metering.go`)

### Summary
This is a direct structural analog of the reported bug class: an accounting invariant ("actual spend should never exceed the pre-earmarked amount") is assumed to always hold, and the code only has a corrective branch for the case where the invariant holds or is violated in the "safe" direction. When it is violated in the unsafe direction, no downward correction is applied and the local credit balance is left artificially inflated, exactly mirroring how `effectiveBond` is never corrected downward in the Autonolas report.

### Finding Description
`Report.Deduct()` earmarks (reserves) a maximum spend amount from the local in-memory `balanceStore` before a capability executes, via `balance.Minus(bal)` (e.g. in `ByResource` and `ByDerivedAvailability`). [1](#0-0) 

When the capability's real spend is reported back via `Settle()`, the code computes the median real spend across nodes (`spentCredits`) and then attempts to "true up" the local balance by returning the *unused* portion of the earmark:
```go
// Refund the difference between what local balance had been earmarked and the actual spend
if err := r.balance.Add(step.Deduction.Sub(spentCredits)); err != nil {
    // invariant: capability should not let spend exceed reserve
    r.lggr.Info("invariant: spend exceeded reserve")
}
r.balance.AddSpent(spentCredits)
``` [2](#0-1) 

This logic implicitly assumes `spentCredits <= step.Deduction` always ("this has to be always true" — the same assumption as in the Tokenomics report). When a capability's real, node-reported spend (`spentCredits`) exceeds the earmarked `step.Deduction` — e.g. a slow/expensive external call, a misbehaving/compromised capability node reporting an inflated `SpendValue`, or simply a capability that ignores its spend limit — `step.Deduction.Sub(spentCredits)` is negative. `balanceStore.Add()` rejects any negative amount outright:
```go
func (bs *balanceStore) Add(amount decimal.Decimal) error {
    ...
    if amount.LessThan(decimal.Zero) {
        return ErrInvalidAmount
    }
    bs.balance = bs.balance.Add(amount)
    return nil
}
``` [3](#0-2) 

There is no `else`/fallback branch that instead calls `balance.Minus()` for the overage. The error is logged and swallowed, and — critically — **the local balance is never debited for the excess spend**. Since `Deduct()` had already subtracted the (smaller) earmark amount at reservation time, and the actual overage is never additionally subtracted, the local `balanceStore.balance` ends up higher than it truthfully should be after this step, i.e. a phantom credit surplus persists for the remainder of the workflow execution.

### Impact Explanation
Subsequent `Deduct()` calls in the same execution (via `ByDerivedAvailability` → `getMaxSpendForInvocation`) compute per-step spend limits directly from `r.balance.Get()`: [4](#0-3) 
Because the balance was not correctly debited downward after an overspend, later steps in the same workflow execution can be granted larger spend limits than the organization's actual reserved credit allowance would justify, allowing the workflow to consume (and ultimately be billed for, via `AddSpent`/`CreditsConsumed` in `SendReceipt`) more resources within a single execution than the `ReserveCredits` call authorized. This is a quota-bypass class issue analogous to the phantom-bond issue in the report: a one-directional correction that only self-heals in the "safe" direction, silently leaving unresolved overage in the "unsafe" direction.

### Likelihood Explanation
This path is reached automatically whenever any capability node reports a spend value exceeding its earmarked deduction — no special privilege is required to trigger it beyond normal workflow execution (which any workflow owner can do). It only requires one step's real spend to exceed its derived limit, which can occur from ordinary variance in node-reported spend or a misbehaving node, making it plausible in normal operation rather than requiring an unlikely edge condition.

### Recommendation
Add an explicit corrective branch so that when `spentCredits > step.Deduction`, the excess is deducted from the balance (allowing it to go as low as zero, with any true insufficiency surfaced rather than silently dropped), instead of only logging and skipping the correction:
```go
diff := step.Deduction.Sub(spentCredits)
if diff.IsNegative() {
    if err := r.balance.Minus(diff.Neg()); err != nil {
        r.lggr.Warnw("invariant violated: spend exceeded reserve and could not be fully debited", "err", err)
    }
} else if err := r.balance.Add(diff); err != nil {
    r.lggr.Info("invariant: spend exceeded reserve")
}
```

### Proof of Concept
1. Start a workflow `Report`, call `Reserve()` to seed a starting balance.
2. Call `Deduct(ref, ByResource(spendType, capID, smallAmount))`, which earmarks `smallAmount` credits and subtracts it from `balance`.
3. Call `Settle(ref, metadata)` with `metadata.Metering` entries whose aggregated/median spend value converts to a `spentCredits` value greater than `smallAmount`.
4. Observe that `balance.Add(step.Deduction.Sub(spentCredits))` returns `ErrInvalidAmount` (since the argument is negative), the error is only logged, and `balance.Get()` is not reduced by the overage — leaving the local balance higher than the true remaining reserve.
5. A subsequent `Deduct(ref2, ByDerivedAvailability(...))` call will derive its spend limit from this inflated balance, granting more spend capacity than the organization's actual reserved credits. [2](#0-1) [3](#0-2)

### Citations

**File:** core/services/workflows/metering/metering.go (L325-338)
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

**File:** core/services/workflows/metering/metering.go (L846-853)
```go
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
