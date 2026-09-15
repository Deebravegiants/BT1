### Title
Metering `Settle` fails to enforce credit reservation, allowing workflow spend to exceed the reserved credit limit - ([File: core/services/workflows/metering/metering.go])

### Summary
The Rubicon `enforceReserveRatio` bug checked a resource-utilization invariant only *before* the action (placing trades) and never re-validated it *after* the action executed, letting strategists overrun the reserve. Chainlink's workflow metering `Report.Settle` exhibits the same check-before-but-not-after pattern: `Deduct` validates and earmarks credits against the reserved balance up front, but `Settle` — which reconciles actual capability spend against that earmark — does not enforce the invariant that spend cannot exceed the reservation. When it does, the balance is simply pushed further into deficit and an informational log line is emitted; no error is returned and no downstream billing/consumption limit is enforced.

### Finding Description
`Report.Deduct` (`core/services/workflows/metering/metering.go:384-401`) earmarks universal credits for a capability step via `ByResource`/`ByDerivedAvailability`, which call `balanceStore.Minus` (`core/services/workflows/metering/balance_store.go:131-146`). `Minus` correctly rejects an earmark if it would exceed the current balance, returning `ErrInsufficientBalance`. This is the "before" check, analogous to Rubicon's `enforceReserveRatio` gate at the start of `placeMarketMakingTrades`.

After the capability actually executes, `Report.Settle` (`core/services/workflows/metering/metering.go:407-515`) computes the real `spentCredits` from node-reported `ResponseMetadata.Metering` and reconciles it against the amount earmarked in `step.Deduction`:

```go
// Refund the difference between what local balance had been earmarked and the actual spend
if err := r.balance.Add(step.Deduction.Sub(spentCredits)); err != nil {
    // invariant: capability should not let spend exceed reserve
    r.lggr.Info("invariant: spend exceeded reserve")
}
r.balance.AddSpent(spentCredits)
``` [1](#0-0) 

`balanceStore.Add` (`core/services/workflows/metering/balance_store.go:172-183`) only rejects a *negative* argument; it never rejects the case where `step.Deduction.Sub(spentCredits)` is negative (i.e., actual spend > earmarked deduction). In that scenario `Add` simply increases the balance by a negative number, i.e., it decrements the balance below what was validated at `Deduct` time, and the "invariant" branch is dead code for this purpose (the error path in `Add` only triggers on `ErrInvalidAmount`, not on overspend). The overspend is only surfaced as an `Info`-level log line — no error is returned to the workflow engine, no execution is halted, and no correction/claw-back against the billing service occurs at this layer.

This is confirmed by the test explicitly named for this behavior:
```go
t.Run("does not error when spend exceeds reservation", func(t *testing.T) {
    ...
    _, err := report.Deduct("ref1", ByResource(testUnitA, "", decimal.NewFromInt(1)))
    require.NoError(t, err)
    require.NoError(t, report.Settle("ref1", steps)) // spend of 2 > deduction of 1
    assert.Len(t, logs.All(), 1)
})
``` [2](#0-1) 

The subsequent local balance is what gates future `Deduct` calls for later steps in the same workflow execution (`ByResource`/`ByDerivedAvailability` call `r.balance.Minus`) — same as Rubicon's per-trade `enforceReserveRatio` gate being checked once at the top but never re-validated against the true post-trade state.

### Impact Explanation
Because the reservation invariant ("spend must not exceed reserve") is enforced only informationally, a single capability step (or its DON members reporting inflated `SpendValue`) can consume more credits than were reserved for the entire workflow execution. Subsequent steps continue to be evaluated against a balance that has silently gone negative/inconsistent, and the final `SubmitWorkflowReceipt` records whatever `spent` accumulated — i.e., a workflow can be billed for (or effectively consume) more credits than `ReserveCredits` authorized from the billing service, without the local accounting or the balance mechanism stopping it. This directly parallels the LP-fund overutilization impact in the Rubicon report: the security control meant to cap consumption is checked pre-action but not re-verified post-action, so real consumption can exceed the authorized/reserved amount.

### Likelihood Explanation
This is reachable purely from data influenced by workflow/capability execution — node-reported `ResponseMetadata.Metering` values feed `spentCredits` in `Settle`, and any capability (including third-party or DON-reported capability responses) that reports a spend value larger than the amount earmarked in `Deduct` triggers this path deterministically; the existing unit test demonstrates the condition occurs in normal (non-adversarial) operation without failing.

### Recommendation
In `Report.Settle`, treat `spentCredits > step.Deduction` as a hard error (or at minimum a per-execution invariant that halts further `Deduct` calls / marks the report as over-budget) rather than only logging at `Info` level. `balanceStore.Add` should reject/report the underflow condition distinctly (e.g., detect that `step.Deduction.Sub(spentCredits)` is negative before calling `Add`, and escalate to the engine so it can stop invoking further capabilities and/or report the overage to the billing service) instead of silently absorbing the negative delta into the balance.

### Proof of Concept
The existing test at `core/services/workflows/metering/metering_test.go:887-912` is itself a proof of concept: it reserves credits, `Deduct`s an earmark of `1` credit, then `Settle`s with a reported spend of `2` credits (double the reservation) and asserts `require.NoError(t, report.Settle(...))` — i.e., the overspend beyond the reservation succeeds without error, only producing one log line, confirming the reservation limit is not enforced at settlement time.

### Citations

**File:** core/services/workflows/metering/metering.go (L506-512)
```go
	// Refund the difference between what local balance had been earmarked and the actual spend
	if err := r.balance.Add(step.Deduction.Sub(spentCredits)); err != nil {
		// invariant: capability should not let spend exceed reserve
		r.lggr.Info("invariant: spend exceeded reserve")
	}

	r.balance.AddSpent(spentCredits)
```

**File:** core/services/workflows/metering/metering_test.go (L887-912)
```go
	t.Run("does not error when spend exceeds reservation", func(t *testing.T) {
		t.Parallel()

		billingClient := mocks.NewBillingClient(t)
		lggr, logs := logger.TestObserved(t, zapcore.InfoLevel)
		billingClient.EXPECT().GetWorkflowExecutionRates(mock.Anything, mock.Anything).
			Return(&billing.GetWorkflowExecutionRatesResponse{
				RateCards: successRates,
			}, nil)
		report := newTestReport(t, lggr, billingClient)

		billingClient.EXPECT().ReserveCredits(mock.Anything, mock.Anything).
			Return(&successReserveResponseWithRates, nil)
		require.NoError(t, report.Reserve(t.Context()))

		steps := capabilities.ResponseMetadata{Metering: []capabilities.MeteringNodeDetail{
			{Peer2PeerID: "xyz", SpendUnit: testUnitA, SpendValue: "2"},
		}}

		_, err := report.Deduct("ref1", ByResource(testUnitA, "", decimal.NewFromInt(1)))
		require.NoError(t, err)

		require.NoError(t, report.Settle("ref1", steps))
		assert.Len(t, logs.All(), 1)
		billingClient.AssertExpectations(t)
	})
```
