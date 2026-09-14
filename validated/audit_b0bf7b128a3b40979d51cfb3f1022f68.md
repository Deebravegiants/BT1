### Title
Metering `Settle` Fails to Deduct Balance When Capability Spend Exceeds Earmarked Reservation - (File: core/services/workflows/metering/metering.go)

### Summary
The CRE workflow engine's metering system reserves ("earmarks") a maximum credit amount per capability call step via `Deduct`, then reconciles the earmarked amount against actual capability-reported spend via `Settle`. When actual spend exceeds the earmarked deduction for a step, the code attempting to apply the difference back to the balance silently no-ops instead of properly debiting the overage, leaving the workflow's credit balance under-charged for the excess spend — directly analogous to the PoolTogether finding where a missing "claimed <= allotted" check let more value be paid out than was allocated.

### Finding Description
`Report.Settle` computes `spentCredits` from capability-reported `metadata.Metering` node details (attacker/capability-influenced data reported after `CallCapability` executes) and then attempts to true-up the local balance: [1](#0-0) 

```go
// Refund the difference between what local balance had been earmarked and the actual spend
if err := r.balance.Add(step.Deduction.Sub(spentCredits)); err != nil {
    // invariant: capability should not let spend exceed reserve
    r.lggr.Info("invariant: spend exceeded reserve")
}

r.balance.AddSpent(spentCredits)
```

`step.Deduction` is the amount earmarked (removed from balance) by the earlier `Deduct` call. The intent is: if actual spend is less than the earmark, refund the unused portion (`Deduction - spentCredits` is positive, `Add` succeeds); if spend is greater than the earmark, the difference is negative and should be additionally subtracted from balance. However, `balanceStore.Add` explicitly rejects negative amounts: [2](#0-1) 

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

So whenever `spentCredits > step.Deduction`, `Add` returns `ErrInvalidAmount`, the balance is left completely unmodified for that step (the overage is never subtracted), and the code merely logs an informational message. Meanwhile, `r.balance.AddSpent(spentCredits)` still records the full (uncapped) spend for reporting purposes, but the actual deductible `balance` used for subsequent `Deduct` calls in the same execution (and for future `GetAs`/insufficient-balance checks) is never reduced by the overage.

### Impact Explanation
This missing/ineffective check mirrors the "no `<=` allotted balance" bug class: a workflow execution can consume more universal credits than were reserved for a given capability step without the excess ever being debited from the tracked balance. Because `balanceStore.Minus`/`MinusAs` (used by subsequent `Deduct` calls in `ByResource`/`ByDerivedAvailability`) only check the in-memory `balance` field, an execution that racks up under-charged overages on early steps will have an inflated balance available for later steps, letting the workflow perform additional capability calls it should not have credit for. This can lead to a workflow spending materially more in aggregate DON/capability resources than the user's `ReserveCredits`-granted allotment, effectively bypassing the credit/billing budget enforced by `Reserve`/`Deduct`/`Settle`.

### Likelihood Explanation
Reachable on every standard workflow execution path: any workflow trigger (attacker-reachable if the workflow accepts unprivileged/external trigger input) invoking a capability via `ExecutionHelper.CallCapability` → `meterReport.Deduct` → capability `Execute` → `meterReport.Settle` will hit this code path whenever a capability's self-reported per-node spend (`capabilities.ResponseMetadata.Metering`) exceeds the earmarked `SpendLimit` passed to it. Since spend metadata originates from capability responses (potentially from third-party/less-trusted capability DONs), a capability that reports (intentionally or due to its own bug) spend above the granted `SpendLimit` will trigger this silently-ineffective branch on every call, without the engine ever enforcing the intended debit or aborting the execution. [3](#0-2) 

### Recommendation
In `Report.Settle`, when `spentCredits.GreaterThan(step.Deduction)`, explicitly call `r.balance.Minus(spentCredits.Sub(step.Deduction))` (or equivalent) to actually debit the overage rather than relying on `Add` with a negative value and swallowing the resulting error. Additionally consider treating an over-spend beyond the earmarked reservation as an error/metering-mode trigger condition rather than a mere log line, so that repeated overages cannot be used to accumulate free credit across a workflow execution.

### Proof of Concept
1. Workflow reserves credits via `Reserve` (`balance = X`).
2. `Deduct` earmarks `D` credits for a capability call, `balance -= D`.
3. Capability executes and reports `ResponseMetadata.Metering` spend values summing (after aggregation) to `S > D`.
4. `Settle` computes `spentCredits = S`, attempts `r.balance.Add(D - S)` where `D - S` is negative → `ErrInvalidAmount` returned → balance is left as `X - D` (not `X - S` as it should be).
5. `r.balance.AddSpent(S)` records the full spend in the report, but the deductible `balance` field retains `D - S` worth of un-debited credit, which remains available for subsequent `Deduct` calls in the same execution, allowing further capability calls beyond the true remaining allotment.

### Citations

**File:** core/services/workflows/metering/metering.go (L501-514)
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
