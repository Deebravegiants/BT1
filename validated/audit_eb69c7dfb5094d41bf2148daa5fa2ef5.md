## Title
Gas spend value rounding in `balanceStore.convertToBalance` can round metering deductions to zero, allowing free/unbilled capability invocations (spam) - ([File: core/services/workflows/metering/balance_store.go])

### Summary
The Kairos `ClaimFacet.sol` bug lets interest round down to zero when `mininterestsToRepay` calculations hit precision loss, enabling a spam attack with no real cost to the attacker. The Chainlink CRE metering subsystem has an analogous rounding path: `balanceStore.convertToBalance` rounds gas-denominated spend to a fixed decimal precision before it is deducted from a workflow's credit balance, and `Report.Settle` uses the very same rounding function both to earmark/refund credits and to compute `spentCredits` that is reported to the billing service. When a capability's actual gas spend, once converted through the rate card, rounds down to zero at `defaultDecimalPrecision` (10 decimal places), the workflow's credit balance is never decremented and the reported `CreditsConsumed` also stays at zero.

### Finding Description
`convertToBalance` performs the gas-unit conversion and rounds the result: [1](#0-0) 

`defaultDecimalPrecision` is fixed at 10: [2](#0-1) 

`Report.Settle` uses `ConvertToBalance` twice for the same purpose — once per-node value (`resourceSpends[unit][idx].CRESpendValue`) and once for the aggregated `spentCredits` that actually gets subtracted from and refunded to the local balance and reported to billing: [3](#0-2) 

The refund logic then returns the full earmarked `Deduction` back to the balance whenever `spentCredits` is (or rounds to) zero: [4](#0-3) 

Because `spentCredits` (via `ConvertToBalance`) rounds down to zero whenever `amount.Div(rate)` is smaller than `0.5 * 10^-10`, a capability invocation whose native gas usage converts to a credit amount below that threshold is effectively free: the earmarked credit is refunded in full, and the amount reported via `SubmitWorkflowReceiptRequest.CreditsConsumed` (`r.balance.GetSpent().String()`) reflects no consumption: [5](#0-4) 

This mirrors the reported bug class exactly: a legitimate, unprivileged accounting-relevant calculation (`interests`/credits owed) can be driven to zero through repeated small-value operations, and nothing checks for or rejects the "rounds to zero" case before treating the transaction as fully settled.

### Impact Explanation
A workflow owner (an authenticated but otherwise unprivileged CRE tenant with respect to the billing subsystem) can structure capability calls — e.g. many small/cheap gas-metered invocations, or a capability that reports tiny `SpendValueInGasUnits` per call — such that each individual settlement rounds to zero credits. Repeating this indefinitely lets the workflow consume real DON/capability node compute and gas-metering resources ("spam") while never depleting its reserved balance and never triggering `ErrInsufficientFunding`/insufficient-balance protections, and while reporting zero consumed credits to the billing service. This is a quota/billing bypass with a fund/resource impact — the primary difference from a pure display bug is that it lets the actor evade the system's economic anti-spam mechanism entirely.

### Likelihood Explanation
Exploitability depends on the configured gas token rate card (`GAS.<chainSelector>` conversion rate) versus the granularity of gas usage reported per capability call — a high `unitsPerCredit` rate combined with small individual gas usages readily produces sub-`10^-10`-credit deductions. Since rate cards are operator/billing-service configured and not attacker controlled directly, likelihood is moderate: it requires a favorable rate configuration, but no special privilege beyond being able to run workflows and invoke gas-metered capabilities repeatedly, which is standard tenant behavior.

### Recommendation
- In `convertToBalance`/`convertFromBalance`, reject or floor-adjust conversions that would round a non-zero input down to exactly zero credits (e.g., charge a minimum non-zero credit unit instead of silently rounding away).
- Track cumulative sub-precision remainders across settlements (similar to an accumulator) so repeated small charges eventually cross the precision threshold and get billed, rather than being discarded on every call.
- Add an explicit invariant check/alert when `spentCredits` is zero but the underlying native spend value was non-zero, to detect and cap this class of rounding-based free invocation before refunding the full `Deduction`.

### Proof of Concept
1. Configure (or have the billing service return) a gas rate card with a large `unitsPerCredit` value for a given chain selector (`GAS.<chainSelector>`), e.g. an extremely high number of gas units per credit.
2. Deploy/run a workflow that repeatedly invokes a gas-metered capability with a small, fixed gas cost per call (`SpendValueInGasUnits` small relative to the rate).
3. On each `Report.Settle` call, `r.balance.ConvertToBalance(unit, value)` computes `value.Div(rate).Round(10)`, which evaluates to `0` for sufficiently small `value`/large `rate`.
4. `spentCredits` accumulates zero across every invocation; the refund logic (`r.balance.Add(step.Deduction.Sub(spentCredits))`) returns the entire earmarked deduction back to the local balance every time, so the workflow's credit balance is never depleted.
5. `SendReceipt` reports `CreditsConsumed: "0"` to the billing service via `SubmitWorkflowReceiptRequest`, despite the workflow having performed unbounded numbers of real capability invocations.

### Citations

**File:** core/services/workflows/metering/balance_store.go (L55-66)
```go
	// Special case for gas as gas token conversions are provided in amount per credit.
	// Other rates are provided as the inverse.
	if isGasSpendType(fromResourceType) {
		if rate.IsZero() {
			return decimal.Zero, nil
		}

		return amount.Div(rate).Round(defaultDecimalPrecision), nil
	}

	return amount.Mul(rate), nil
}
```

**File:** core/services/workflows/metering/metering.go (L32-36)
```go
const (
	RatiosKey = "spendRatios"
	// the default decimal precision is a fixed number defined in the billing service. if this gets changed
	// in the billing service project, the value here needs to change.
	defaultDecimalPrecision = 10 // one thousandth of a dollar
```

**File:** core/services/workflows/metering/metering.go (L452-495)
```go
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

**File:** core/services/workflows/metering/metering.go (L505-514)
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
