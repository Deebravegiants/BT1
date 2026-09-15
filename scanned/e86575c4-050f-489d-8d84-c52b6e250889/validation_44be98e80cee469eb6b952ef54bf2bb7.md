Based on my analysis, I found a legitimate analog: a rounding-to-zero issue in the CRE metering/billing subsystem's gas-to-credit conversion, structurally identical to the reported `GPToke.addWETHRewards` bug class.

### Title
Rounding Down to Zero in Gas-to-Credit Conversion Allows Billing Quota Bypass - (File: core/services/workflows/metering/balance_store.go)

### Summary
The `balanceStore.convertToBalance` function in the CRE workflow metering system converts raw gas-spend amounts into universal credits by dividing by a conversion rate and rounding to a fixed decimal precision. When the resulting quotient is smaller than the smallest representable unit at that precision, it silently truncates to zero, exactly mirroring the `accRewardPerShare` rounding-to-zero bug class from the reported issue, except here the truncation causes real resource usage to go unbilled rather than causing rewards to freeze.

### Finding Description
In `convertToBalance`, gas-denominated spend amounts are converted using: [1](#0-0) 

`amount.Div(rate).Round(defaultDecimalPrecision)` truncates any quotient smaller than `10^-defaultDecimalPrecision` to exactly zero. `defaultDecimalPrecision` is a fixed constant: [2](#0-1) 

This conversion is invoked from `Report.Settle`, which is called once per capability-invocation step during a workflow execution, using node-reported `SpendValue`/`SpendValueInGasUnits` fields that are aggregated via median and then converted to credits: [3](#0-2) 

Because `Settle` is invoked once per step reference (`ref`) per workflow execution, and workflows can contain arbitrarily many steps/capability calls, a workflow owner (an authenticated but otherwise unprivileged actor who merely registers/runs a workflow) can structure a workflow with many capability invocations, each reporting a gas spend amount just below the rounding threshold relative to the configured `GasTokensPerCredit` rate. Each individual `Settle` call converts that spend to `0` credits, so `spentCredits` accumulated in `r.balance.AddSpent(spentCredits)` and the refunded/deducted amounts never reflect the true aggregate gas cost, even though real capability/gas resources are being consumed on the DON's behalf.

This is the direct code-pattern analog of the reported issue: instead of `accRewardPerShare += amount * REWARD_FACTOR / supply` silently adding zero when `amount` is small relative to `supply`, `convertToBalance` silently converts to zero credits when `amount` is small relative to `rate`, and there is no minimum-nonzero-charge guard analogous to the report's suggested `require(accRewardPerShareToAdd != 0)`.

### Impact Explanation
Repeated fragmentation of gas spend into sub-threshold increments lets a workflow owner consume gas-metered capability resources without being charged, since each `Settle` call converts to exactly `0` credits at the reporting/billing layer. Over many steps or executions this results in systematic under-billing — real infrastructure/gas costs are incurred but never deducted from the workflow's reserved credit balance nor reported to the billing service via `SubmitWorkflowReceipt`'s `CreditsConsumed` field. This constitutes a quota/billing bypass reachable purely by controlling how a workflow's steps report spend, without any privileged access.

### Likelihood Explanation
Likelihood is moderate: it requires the attacker/workflow owner to control or influence the granularity of reported `SpendValue`/`SpendValueInGasUnits` per step (e.g., by splitting work across many low-cost capability calls) and requires the configured `GasTokensPerCredit` rate to make individual per-call gas costs fall below the `1e-10` credit threshold, which is plausible for very cheap gas capability calls or chains with large per-credit gas token denominations.

### Recommendation
Apply the same fix pattern recommended in the source report:
1. Increase precision or avoid intermediate rounding until the final aggregate spend is computed, rather than rounding per-step, per-unit conversions to zero, or
2. Add an explicit check in `convertToBalance` so that when `amount` is non-zero but converts to a zero credit result at `defaultDecimalPrecision`, the amount is instead accumulated in a sub-precision remainder pool (carried forward) rather than dropped, ensuring cumulative gas spend is never systematically undercharged.

### Proof of Concept
Given `defaultDecimalPrecision = 10` and a gas rate (e.g., `GasTokensPerCredit` for a chain) such that `rate = 5e18` (gas units per credit), any single step reporting `SpendValueInGasUnits` less than `5e18 * 1e-10 = 5e8` wei will produce:
```
amount.Div(rate).Round(10) == 0
```
in `convertToBalance` ( [4](#0-3) ), yielding `bal == 0` in `Settle` ( [5](#0-4) ), which is then added to `spentCredits` without deducting the actual balance corresponding to the gas consumed. A workflow with N such steps consumes N * (sub-threshold gas amount) of real resources while contributing `0` to `CreditsConsumed` in the final `SubmitWorkflowReceipt` call ( [6](#0-5) ).

### Citations

**File:** core/services/workflows/metering/balance_store.go (L55-63)
```go
	// Special case for gas as gas token conversions are provided in amount per credit.
	// Other rates are provided as the inverse.
	if isGasSpendType(fromResourceType) {
		if rate.IsZero() {
			return decimal.Zero, nil
		}

		return amount.Div(rate).Round(defaultDecimalPrecision), nil
	}
```

**File:** core/services/workflows/metering/metering.go (L32-37)
```go
const (
	RatiosKey = "spendRatios"
	// the default decimal precision is a fixed number defined in the billing service. if this gets changed
	// in the billing service project, the value here needs to change.
	defaultDecimalPrecision = 10 // one thousandth of a dollar

```

**File:** core/services/workflows/metering/metering.go (L481-495)
```go
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
