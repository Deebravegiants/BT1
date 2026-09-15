### Title
Metering balance is not decremented when actual capability spend exceeds the earmarked deduction, allowing per-execution credit-limit bypass - (File: `core/services/workflows/metering/metering.go`)

### Summary
`Report.Settle` reconciles the local in-execution credit balance after a capability step completes by refunding the difference between what was earmarked (`step.Deduction`) and what was actually spent (`spentCredits`), computed as `step.Deduction.Sub(spentCredits)` and passed to `balanceStore.Add`. `balanceStore.Add` rejects any negative amount with `ErrInvalidAmount`. When the DON-reported spend for a step exceeds the amount that was earmarked for it, the resulting value is negative, `Add` fails, and `Settle` only logs `"invariant: spend exceeded reserve"` — it never reduces the local balance for the excess spend [1](#0-0) . This is structurally the same class of bug as the referenced report: a value used to update accounting state (`_usdm`/spend) is computed on one basis while the tracked state (`details[_id].debt`/`balanceStore.balance`) is computed/adjusted on a different, inconsistent basis, and the mismatch is silently swallowed instead of being corrected, defeating the intended limit/accounting control.

### Finding Description
`Report.Deduct` earmarks a maximum spend for a step via `ByResource` or `ByDerivedAvailability`, which calls `r.balance.Minus(...)` to reserve credits up front [2](#0-1) .

After the capability responds, `Report.Settle` aggregates the actual per-node reported spend into `spentCredits` from `metadata.Metering` (data supplied by DON node responses for the invoked capability), converts it to credits, and then attempts to true-up the local balance:

```go
if err := r.balance.Add(step.Deduction.Sub(spentCredits)); err != nil {
    // invariant: capability should not let spend exceed reserve
    r.lggr.Info("invariant: spend exceeded reserve")
}
r.balance.AddSpent(spentCredits)
``` [3](#0-2) 

`balanceStore.Add` explicitly rejects negative deltas:
```go
func (bs *balanceStore) Add(amount decimal.Decimal) error {
    ...
    if amount.LessThan(decimal.Zero) {
        return ErrInvalidAmount
    }
    bs.balance = bs.balance.Add(amount)
    return nil
}
``` [4](#0-3) 

So whenever `spentCredits > step.Deduction` (i.e., the real resource usage reported for the step is larger than what was reserved for it — plausible any time `ByDerivedAvailability`'s limit calculation under-estimates true usage, or spend units/ratios diverge from actual node behavior), `bs.balance` is left unchanged instead of being decreased by the true cost of the step. The code path only logs a warning and moves on, exactly mirroring the reported Mochi bug where a mismatched subtrahend causes the intended state update to be skipped/aborted rather than corrected.

### Impact Explanation
Because `r.balance` (the in-execution "remaining credit" tracker) is not reduced for the overage, subsequent `Deduct` calls in the same workflow execution (via `ByDerivedAvailability`, which derives per-step spend limits from the current remaining balance) will be granted limits based on an artificially inflated remaining balance. This lets a single workflow execution authorize more downstream capability spend than the credits actually reserved for it via `Reserve`/`ReserveCredits` should allow — a local quota/limit-enforcement bypass within the metering subsystem that is supposed to bound per-step and cumulative spend for a workflow owner's execution.

### Likelihood Explanation
This does not require a malicious node; it only requires that reported/derived spend for any step legitimately exceed its earmarked deduction, which can occur due to normal variance between `ByDerivedAvailability`'s limit estimate and actual multi-node reported usage, or unit/ratio conversion rounding. The failure mode is silent (just an info log), so it is unlikely to be caught operationally, and it is reachable purely through normal workflow execution triggered by a workflow owner (e.g. via the HTTP trigger path into the gateway/engine), without any privileged access.

### Recommendation
When `step.Deduction.Sub(spentCredits)` is negative, `Settle` should still deduct the shortfall from the balance (e.g., call `balance.Minus` on the absolute overage, or clamp the balance at zero) instead of doing nothing, so that the local credit-limit enforcement used by subsequent `Deduct` calls always reflects true cumulative spend. At minimum, entering metering mode (as is already done for other invariant violations) rather than silently continuing with a stale/incorrect balance would prevent the limit-bypass window.

### Proof of Concept
1. Start a workflow execution with `Reserve` succeeding and a finite credit balance.
2. For a given step, call `Deduct("ref1", ByDerivedAvailability(...))`, which earmarks/`Minus`es a limited `step.Deduction` from the balance.
3. Simulate capability node responses in `ResponseMetadata.Metering` whose aggregated/converted spend value exceeds `step.Deduction`.
4. Call `Settle("ref1", metadata)` — observe that `r.balance.Add(step.Deduction.Sub(spentCredits))` returns `ErrInvalidAmount`, the error is only logged, and `r.balance.Get()` still reflects the pre-overage (higher) balance while `AddSpent` correctly records the true higher spend, i.e., the enforcement-facing `balance` and the accounting-facing `spent` diverge.
5. A subsequent `Deduct` call for the next step in the same execution will compute its `ByDerivedAvailability` limit off the inflated `balance`, permitting more spend than the original reservation should allow. [5](#0-4)

### Citations

**File:** core/services/workflows/metering/metering.go (L308-379)
```go
// ByResource returns a DeductOpt that earmarks a specified amount of local universal credit balance for a given spend
// type.
func ByResource(
	spendType, capabilityID string,
	amount decimal.Decimal,
) func(string, *Report) ([]capabilities.SpendLimit, error) {
	return func(ref string, r *Report) ([]capabilities.SpendLimit, error) {
		step := ReportStep{
			CapabilityID:     capabilityID,
			Deduction:        decimal.Zero,
			AggregatedSpends: make(map[string]AggregatedStepDetail),
		}

		defer func() {
			r.steps[ref] = step
		}()

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
}

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

**File:** core/services/workflows/metering/metering.go (L384-401)
```go
func (r *Report) Deduct(ref string, opt DeductOpt) ([]capabilities.SpendLimit, error) {
	r.mu.Lock()
	defer r.mu.Unlock()

	if !r.reserved {
		return nil, ErrNoReserve
	}

	if opt == nil {
		return nil, ErrDeductOptionRequired
	}

	if _, ok := r.steps[ref]; ok {
		return nil, ErrStepDeductExists
	}

	return opt(ref, r)
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

**File:** core/services/workflows/metering/balance_store.go (L172-183)
```go
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
