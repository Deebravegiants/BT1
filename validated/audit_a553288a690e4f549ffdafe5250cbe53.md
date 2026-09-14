### Title
Silent failure of credit balance debit on capability overspend allows quota bypass in CRE workflow metering - ([File: core/services/workflows/metering/metering.go])

### Summary
The Tokemak `LMPDebt.sol` bug compared a current value to a recorded baseline to decide whether a "loss" existed, but failed to correctly account for/limit the discrepancy, effectively writing off a loss and letting withdrawals bypass the intended restriction. The analogous flaw in the CRE workflow metering code is in `Report.Settle`, where the local credit balance is supposed to be corrected downward when a capability's actual spend exceeds its earmarked deduction, but the correction is silently dropped whenever the balance-store `Add` guard rejects the (negative) amount, leaving the tracked balance artificially inflated and available for further spend.

### Finding Description
`Report.Settle` earmarks credits per step (`step.Deduction`) via `Deduct`, then reconciles the earmark against the actual spend (`spentCredits`) reported by capability nodes: [1](#0-0) 

```go
// Refund the difference between what local balance had been earmarked and the actual spend
if err := r.balance.Add(step.Deduction.Sub(spentCredits)); err != nil {
    // invariant: capability should not let spend exceed reserve
    r.lggr.Info("invariant: spend exceeded reserve")
}
r.balance.AddSpent(spentCredits)
```

`balanceStore.Add` requires the amount to be non-negative: [2](#0-1) 

If `spentCredits > step.Deduction` (i.e., the node-reported spend for that step exceeded what was earmarked/deducted), `step.Deduction.Sub(spentCredits)` is negative, `Add` returns `ErrInvalidAmount`, and — critically — the balance is **not modified at all**. The code only logs an info-level message ("invariant: spend exceeded reserve") and continues. This is structurally identical to the Tokemak bug: a case that should reduce the tracked value (a "loss"/overspend) is instead silently dropped because the guard condition wasn't designed to handle that branch, so the tracked balance keeps showing the pre-overspend value.

The consequence is that `r.balance.Get()` — which feeds `getMaxSpendForInvocation` and thus the spend limits (`ByDerivedAvailability`) handed to subsequent capability calls within the same workflow execution — remains higher than it truly should be: [3](#0-2) 

Only `AddSpent` (a separate running total used purely for the final billing receipt) is updated, so the true consumption is eventually reported to the billing service via `SendReceipt`/`CreditsConsumed`, but *not before* the current, still-executing workflow can use the inflated local balance to authorize additional capability calls beyond the amount that was actually reserved with the billing service in `Reserve`.

This metering path is reachable from unprivileged, internet-facing requests: an external caller invokes an HTTP Trigger through the gateway (`httpTriggerHandler.HandleUserTriggerRequest`), which authenticates via JWT and authorizes/rate-limits the request: [4](#0-3) 

but does not itself account for the actual per-capability credit spend — that happens later inside the DON's workflow engine (`Engine`/`ExecutionHelper` in `core/services/workflows/v2`), which calls `metering.Report.Deduct`/`Settle` per capability invocation using this same `balanceStore`.

### Impact Explanation
Because the local balance is not decremented correctly when a capability step overspends its deduction, subsequent `Deduct` calls in the same workflow execution compute spend limits from an inflated `r.balance`. This allows a workflow execution — triggered by an unprivileged/external caller via the internet-facing HTTP trigger gateway — to authorize more resource consumption (compute, gas, HTTP action calls, etc.) across the remaining steps of the execution than the credits actually reserved with the billing service permit. This is a quota-bypass class issue: the local enforcement mechanism intended to cap spend within a reserved credit budget can be defeated by a single overspending step, and the discrepancy is only reconciled after the fact at `SendReceipt` time, when the workflow (and its resource usage) has already completed.

### Likelihood Explanation
Triggering this requires only that a capability's node-reported spend for a step exceed the amount that was earmarked for it via `Deduct` — this is plausible whenever the earmarked deduction underestimates real usage (e.g., variable-cost operations, gas price fluctuation, `ByDerivedAvailability` splitting available balance across concurrent slots) and does not require any privileged access; it is driven purely by capability responses during normal, externally triggered workflow execution flow.

### Recommendation
In `Report.Settle`, do not rely on `balanceStore.Add` silently no-op'ing on a negative net. Explicitly branch on whether `spentCredits` exceeds `step.Deduction`: if it does, subtract the excess from the balance (clamping at zero and/or switching the report to metering/fail-safe mode) rather than only logging an informational message. This ensures the local balance used to gate subsequent `Deduct` calls always reflects true remaining credits, mirroring correct PnL tracking instead of writing off the overspend.

### Proof of Concept
1. A workflow is triggered externally via the HTTP Trigger gateway handler (`httpTriggerHandler.HandleUserTriggerRequest`), reserving a fixed credit budget via `Report.Reserve`.
2. Step A calls `Deduct` with `ByResource`/`ByDerivedAvailability`, earmarking `D` credits (`step.Deduction = D`).
3. The capability executes and reports `SpendValue` in `Settle` such that the aggregated `spentCredits > D` (e.g., due to gas price spike or concurrent-slot division underestimating usage).
4. In `Settle`, `step.Deduction.Sub(spentCredits)` is negative; `r.balance.Add(negative)` returns `ErrInvalidAmount` and the balance is left unchanged (still reflecting the state *before* Step A's true cost was applied), while `AddSpent(spentCredits)` only updates the separate `spent` counter used for the end-of-execution receipt.
5. Step B calls `Deduct` again; `getMaxSpendForInvocation` computes its limit from `r.balance.Get()`, which is still inflated relative to true remaining credits, allowing Step B (and further steps) to be granted spend limits that, combined with Step A's real overspend, exceed the credits originally reserved with the billing service — the discrepancy is only visible to billing after `SendReceipt` is called at the end of execution.

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

**File:** core/services/workflows/metering/metering.go (L846-853)
```go
	// Split the available local balance between the number of concurrent calls that can still be made
	spendLimit := r.balance.Get().Div(decimal.NewFromInt(int64(openConcurrentCallSlots)))

	if userSpendLimit.Valid {
		spendLimit = decimal.Min(spendLimit, userSpendLimit.Decimal)
	}

	return decimal.NewNullDecimal(spendLimit), nil
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}
```
