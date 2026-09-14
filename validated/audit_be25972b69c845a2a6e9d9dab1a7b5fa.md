## Analog Vulnerability Found

### Title
Capability execution proceeds even when billing/metering deduction fails, allowing quota/balance bypass - (File: core/services/workflows/v2/capability_executor.go)

### Summary
This is a structural analog of the Sherlock M-12 bug class: an accounting subsystem (`AaveProvider`/`BetaProvider` exchange rate, here the CRE metering `balanceStore`/`Report`) can silently fail to enforce/track spend, while the underlying operation (yield generation / capability execution) proceeds unaffected. In `derby`, gamers lose rewards because the rate is wrong but yield still accrues to depositors. In chainlink's workflow engine, when `meterReport.Deduct` fails (including on `ErrInsufficientBalance`), the code only logs the error and continues to execute the capability anyway, so a workflow owner can keep invoking metered (billed) capabilities after exhausting their credit balance.

### Finding Description
`ExecutionHelper.callCapability` calls `meterReport.Deduct` to earmark credits and derive `spendLimits` before invoking a capability: [1](#0-0) 

If `Deduct` returns an error, the code does `c.cfg.Lggr.Errorw(...)` and falls straight through — there is no `return` — into building `capReq` and calling `capability.Execute(execCtx, capReq)`: [2](#0-1) 

`Report.Deduct` can fail with `ErrInsufficientBalance` from the underlying `balanceStore.Minus`/`MinusAs` calls once a workflow has exhausted its allotted credits: [3](#0-2) [4](#0-3) 

Because the error path in `callCapability` doesn't abort, and `spendLimits` may remain empty/unset, the capability is executed with no enforced spend limit and no successful balance deduction — i.e., the workflow effectively gets a free/unmetered capability call instead of being blocked once out of credits.

### Impact Explanation
A workflow owner (an unprivileged client relative to the node/billing service) that has exhausted its credit balance can continue invoking metered capabilities (external HTTP calls, chain writes, consensus, etc.) without paying for them, because the failure of the billing deduction is only logged, not enforced. This is a quota/billing bypass: the entity responsible for tracking spend (`Report`/`balanceStore`) can fail open, letting metered capability execution proceed unconditionally, mirroring the referenced bug class where a broken accounting value (exchange rate returning 1/0) silently decouples reward/charge tracking from the real underlying activity.

### Likelihood Explanation
This does not require any special privilege — any workflow whose reported/derived spend limit calculation returns an error (e.g., insufficient balance, `ErrNoOpenCalls`, or other errors bubbling from `ByDerivedAvailability`) triggers the vulnerable code path on every subsequent capability call for that execution. Given metering/billing is meant to be a hard limit on paid usage, exhausting the balance is an expected, easily reachable state during normal workflow execution.

### Recommendation
In `callCapability`, when `meterReport.Deduct` returns an error (particularly `ErrInsufficientBalance`), abort the capability execution and return an error to the caller instead of only logging and continuing. Ensure `spendLimits` cannot be used to permit unmetered execution when deduction fails.

### Proof of Concept
1. Start a workflow execution with a `Report` created via `NewReport` with a small starting balance/rate card such that credits will be exhausted after a few metered capability calls (see `Test_Report_Deduct`/`ByDerivedAvailability` tests for exact mechanics: [5](#0-4) ).
2. Repeatedly invoke a metered capability from the workflow guest code via `CallCapability` so that `meterReport.Deduct` eventually returns `ErrInsufficientBalance`.
3. Observe in `callCapability` (`core/services/workflows/v2/capability_executor.go:199-209`) that the error is only logged (`c.cfg.Lggr.Errorw(...)`) — execution proceeds to `capability.Execute(execCtx, capReq)` at line 254 regardless, allowing further metered capability calls beyond the allotted/paid balance.

### Citations

**File:** core/services/workflows/v2/capability_executor.go (L185-210)
```go
	meteringRef := strconv.Itoa(int(request.CallbackId))
	spendLimits := []capabilities.SpendLimit{}

	if meterReport != nil {
		// TODO: https://smartcontract-it.atlassian.net/browse/CRE-285 get max spend per step from SDK.
		// TODO: https://smartcontract-it.atlassian.net/browse/CRE-284 parse user max spend for step
		userSpendLimit := decimal.NewNullDecimal(decimal.Zero)
		userSpendLimit.Valid = false

		var openConcurrentCallSlots int
		if openConcurrentCallSlots, err = c.cfg.LocalLimiters.CapabilityConcurrency.Available(ctx); err != nil {
			return nil, err
		}

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
	}
```

**File:** core/services/workflows/v2/capability_executor.go (L212-254)
```go
	capReq := capabilities.CapabilityRequest{
		Payload:      request.Payload,
		Method:       request.Method,
		CapabilityId: request.Id,
		Metadata: capabilities.RequestMetadata{
			WorkflowOwner:            c.cfg.WorkflowOwner,
			WorkflowID:               c.cfg.WorkflowID,
			WorkflowExecutionID:      c.WorkflowExecutionID,
			WorkflowName:             c.cfg.WorkflowName.Hex(),
			WorkflowDonID:            localNode.WorkflowDON.ID,
			WorkflowDonConfigVersion: pinnedWorkflowDonConfigVersion,
			ReferenceID:              strconv.Itoa(int(request.CallbackId)),
			DecodedWorkflowName:      c.cfg.WorkflowName.String(),
			SpendLimits:              spendLimits,
			WorkflowTag:              c.cfg.WorkflowTag,
			ExecutionTimestamp:       c.ExecutionTimestamp,
		},
		Config: values.EmptyMap(),
	}
	var creGetter settings.Getter
	if c.cfg.LocalLimiters != nil {
		creGetter = c.cfg.LocalLimiters.Settings
	}
	propagateOrgIDMeta, _ := cresettings.Default.PropagateOrgIDInRequestMetadata.GetOrDefault(ctx, creGetter)
	if propagateOrgIDMeta && c.orgID != "" {
		capReq.Metadata.OrgID = c.orgID
	}

	execLogger.Debug("Executing capability ...")
	c.metrics.With(platform.KeyCapabilityID, request.Id).IncrementCapabilityInvocationCounter(ctx)
	loggerLabels := c.eventLabels()
	_ = events.EmitCapabilityStartedEvent(ctx, loggerLabels, c.WorkflowExecutionID, request.Id, meteringRef, request.Method)

	execCtx, execCancel, err := c.cfg.LocalLimiters.CapabilityCallTime.WithTimeout(ctx)
	if err != nil {
		return nil, err
	}
	defer execCancel()

	executionStart := c.cfg.Clock.Now()
	c.executionProfile.recordStepStart(meteringRef, request.Id, executionStart)

	capResp, err := capability.Execute(execCtx, capReq)
```

**File:** core/services/workflows/metering/balance_store.go (L130-146)
```go
// Minus lowers the current credit balance.
func (bs *balanceStore) Minus(amount decimal.Decimal) error {
	bs.mu.Lock()
	defer bs.mu.Unlock()

	if amount.LessThan(decimal.Zero) {
		return ErrInvalidAmount
	}

	if amount.GreaterThan(bs.balance) {
		return ErrInsufficientBalance
	}

	bs.balance = bs.balance.Sub(amount)

	return nil
}
```

**File:** core/services/workflows/metering/metering.go (L342-378)
```go
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
```

**File:** core/services/workflows/metering/metering_test.go (L557-576)
```go
	t.Run("returns insufficient balance when not in metering mode", func(t *testing.T) {
		t.Parallel()

		deductValue := decimal.NewFromInt(11_000)
		billingClient := mocks.NewBillingClient(t)
		billingClient.EXPECT().GetWorkflowExecutionRates(mock.Anything, mock.Anything).
			Return(&billing.GetWorkflowExecutionRatesResponse{
				RateCards: successRates,
			}, nil)
		report := newTestReport(t, logger.Nop(), billingClient)

		billingClient.EXPECT().ReserveCredits(mock.Anything, mock.Anything).
			Return(&successReserveResponseWithRates, nil)
		require.NoError(t, report.Reserve(t.Context()))

		_, err := report.Deduct("ref1", ByResource(testUnitA, "", deductValue))
		require.ErrorIs(t, err, ErrInsufficientBalance)

		billingClient.AssertExpectations(t)
	})
```
