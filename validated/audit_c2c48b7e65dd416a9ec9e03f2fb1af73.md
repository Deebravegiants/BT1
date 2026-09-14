### Title
Metering `Report.Settle` fails to charge the local credit balance for the excess when node-reported spend exceeds the earmarked deduction - ([File: core/services/workflows/metering/metering.go])

### Summary
`Report.Settle` refunds "the difference between what local balance had been earmarked and the actual spend" via `r.balance.Add(step.Deduction.Sub(spentCredits))` [1](#0-0)  . `balanceStore.Add` explicitly rejects negative amounts and returns `ErrInvalidAmount` without touching the balance [2](#0-1) . When `spentCredits` (the aggregated, node/capability-reported spend, converted via `ConvertToBalance`) exceeds `step.Deduction` (the amount earmarked in the prior `Deduct` call), the subtraction is negative, `Add` fails, and the error is only logged ("invariant: spend exceeded reserve") — the local balance is left completely untouched instead of being reduced by the excess [3](#0-2) .

### Finding Description
This mirrors the audit bug class exactly: like `_distributeProceeds` handling the case `feesEarned > totalReceived` incorrectly by short-changing the treasury, `Settle` handles the case `spentCredits > step.Deduction` incorrectly by short-changing the local balance ledger. The earmark placed by `Deduct` (via `ByResource`/`ByDerivedAvailability`) reserves an amount up front by subtracting it from `balanceStore.balance` [4](#0-3) . `Settle` is supposed to true up that earmark against the real spend reported by capability DON nodes in `metadata.Metering` (attacker/capability-influenced `SpendValue` data) [5](#0-4) . If the real spend is larger than what was earmarked, the code should additionally deduct the shortfall from the balance so the workflow owner's remaining credit reflects the true state. Instead, `Add` with a negative argument is a no-op error, so the balance simply keeps the (too-generous) amount left over from the original earmark subtraction — the excess spend is never removed from `balance`. Meanwhile `r.balance.AddSpent(spentCredits)` still unconditionally records the *full* `spentCredits` value for reporting purposes regardless of whether the balance itself was actually decremented for that amount [6](#0-5) , so the internal “spent” bookkeeping and the actual `balance` value diverge whenever this invariant is violated.

### Impact Explanation
The practical effect is that subsequent `Deduct` calls within the same workflow execution (`ByResource`, `ByDerivedAvailability`) check availability against a `balance` value that is higher than it should be, because it was never reduced by the true excess spend of a prior step. This lets execution continue spending against credit that has already effectively been consumed by real capability node usage, i.e. an accounting/quota-bypass within a single workflow execution's credit-tracking mechanism, all driven by data coming from `capabilities.ResponseMetadata.Metering` supplied through the capability/gateway pipeline rather than a privileged source.

### Likelihood Explanation
This requires only that a single Settle step's aggregated spend value exceed its earmarked `Deduction` — plausible whenever `ByDerivedAvailability`'s max-spend estimate under-predicts actual node-reported usage, or when unit conversion rounding pushes `spentCredits` slightly above `step.Deduction`. The code comment itself documents this as a known, expected "invariant" violation path (`"invariant: spend exceeded reserve"`), indicating the authors were aware the condition can occur but chose only to log it rather than correctly true up the ledger.

### Recommendation
When `spentCredits.GreaterThan(step.Deduction)`, compute the excess (`spentCredits.Sub(step.Deduction)`) and call `r.balance.Minus(excess)` (clamped at zero balance / entering metering mode on insufficient balance) instead of calling `Add` with a negative delta and silently swallowing the resulting error, analogous to the audit's fix of deducting the fee shortfall from the refund rather than ignoring it.

### Proof of Concept
Not directly exploitable as a standalone PoC without a running workflow engine; the flow is: `Deduct("stepX", ByDerivedAvailability(...))` earmarks `D` credits and reduces `balance` by `D` → `Settle("stepX", metadata)` where the aggregated `spentCredits` (derived from `metadata.Metering[...].SpendValue`, reported by capability DON nodes) is computed to be greater than `D` → `r.balance.Add(D.Sub(spentCredits))` receives a negative argument → `Add` returns `ErrInvalidAmount` → only logged, `balance` unchanged → a later `Deduct` in the same execution session succeeds against a balance that should already have been fully consumed by the prior step's real spend [3](#0-2) [2](#0-1) .

### Citations

**File:** core/services/workflows/metering/metering.go (L308-339)
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
```

**File:** core/services/workflows/metering/metering.go (L424-495)
```go
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
