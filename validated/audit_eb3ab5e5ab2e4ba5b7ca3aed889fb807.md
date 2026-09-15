Confirmed root-cause: in `callCapability`, when `meterReport.Deduct(...)` returns an error (e.g. `ErrInsufficientBalance`), the code only logs the error via `c.cfg.Lggr.Errorw(...)` and continues execution instead of aborting the capability call. `spendLimits` remains the empty `[]capabilities.SpendLimit{}` initialized on line 186, and the request proceeds to `capability.Execute(...)` with no spend limit and without local balance ever having been decremented.

### Title
Metering deduction failure does not block capability execution, allowing unlimited capability spend after balance exhaustion - (File: core/services/workflows/v2/capability_executor.go)

### Summary
`callCapability` treats a failed `Report.Deduct` call (local credit-balance reservation) as non-fatal: it logs the error and still executes the requested capability with no enforced spend limit.

### Finding Description
`meterReport.Deduct` is meant to earmark local universal-credit balance before a capability is invoked [1](#0-0) . `ByDerivedAvailability`, the `DeductOpt` used here, computes a spend limit and calls `r.balance.Minus(limit.Decimal)`, which returns `ErrInsufficientBalance` and leaves the balance untouched when the deduction would exceed available credits [2](#0-1) [3](#0-2) .

In `callCapability`, `spendLimits` is pre-initialized to an empty slice, and the error returned by `Deduct` is only logged, not propagated or used to short-circuit the request: [4](#0-3) 

Regardless of whether `Deduct` succeeds or fails, execution falls through to build `capReq` (using whatever `spendLimits` happens to be — empty on failure) and call `capability.Execute(execCtx, capReq)` [5](#0-4) .

This mirrors the reported bug class: an accounting/limiting value (`amountToBuyLeftUSD` in the report; here the deducted balance / spend-limit state) is not correctly propagated on an error/alternate path, so downstream logic proceeds as if accounting succeeded. Here, a workflow whose local credit balance is exhausted (or whose spend-type/ratio configuration triggers `ErrRatiosAndTypesNoMatch`, `ErrInvalidRatios`, etc., inside `creditToSpendingLimits`) still gets its capability call executed with an empty `spendLimits`, i.e., no cap on downstream resource spend is communicated to the capability DON at all.

### Impact Explanation
A workflow owner (an unprivileged CRE workflow-execution actor, reachable simply by triggering their own workflow's execution) can continue invoking metered capabilities after their local balance is insufficient. Since `Deduct` failing means `r.balance.Minus` was never actually applied, and the subsequent `Settle` step still uses `step.Deduction` (the *attempted* limit, not zero) to compute the refund (`r.balance.Add(step.Deduction.Sub(spentCredits))`) [6](#0-5) , this also introduces balance drift: the balance can be inflated or under-charged relative to actual capability spend because `step.Deduction` was recorded despite the reservation never having taken effect. Net effect: unauthorized/uncapped capability invocations (a quota/fund-accounting bypass) and corrupted downstream credit accounting used for billing (`SubmitWorkflowReceipt`) [7](#0-6) .

### Likelihood Explanation
High under any condition that makes `Deduct` fail — most simply, insufficient local balance from ordinary usage — since it requires no special privilege, network condition, or malicious peer; a legitimate but low-balance workflow owner triggering a normal execution reaches this path.

### Recommendation
On `Deduct` failure, abort the capability call (return an error, e.g. `caperrors.NewPublicUserError` with a limit-exceeded/insufficient-funds code) instead of logging and continuing with empty `spendLimits`. Additionally, ensure `Settle`'s refund/accounting uses the actual applied `Deduction` (zero when `Minus` failed) rather than the attempted limit, so balance is never adjusted based on a reservation that was never taken.

### Proof of Concept
1. Configure a workflow with a billing client returning a small credit balance via `ReserveCredits` (e.g., 0 or near-0 credits), matching test patterns like `successZeroReserveResponseWithRates` [8](#0-7) .
2. Trigger workflow execution such that `ExecutionHelper.CallCapability` → `callCapability` is invoked for a metered capability [9](#0-8) .
3. `meterReport.Deduct(..., metering.ByDerivedAvailability(...))` returns `ErrInsufficientBalance` because `r.balance.Minus` fails [10](#0-9) [3](#0-2) .
4. Observe that `callCapability` still logs and proceeds to call `capability.Execute` with `spendLimits = []capabilities.SpendLimit{}` [11](#0-10) , i.e. the capability is executed for free / without any enforced limit despite insufficient balance — repeatable indefinitely.

### Citations

**File:** core/services/workflows/metering/metering.go (L342-379)
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
}
```

**File:** core/services/workflows/metering/metering.go (L381-401)
```go
// Deduct earmarks an amount of local universal credit balance. The amount provided is expected to be in native units.
// An option of 0 indicates a max spend should be derived from user limits and concurrent call slots. We expect to only
// set this value once - an error is returned if a step would be overwritten.
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

**File:** core/services/workflows/metering/metering.go (L632-653)
```go
func (r *Report) SendReceipt(ctx context.Context) error {
	if !r.reserved {
		return ErrNoReserve
	}

	if r.client == nil {
		return ErrNoBillingClient
	}

	r.metrics.UpdateWorkflowMeteringModeGauge(ctx, r.isMeteringMode())

	// TODO: https://smartcontract-it.atlassian.net/browse/CRE-427 more robust check of billing service health

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

**File:** core/services/workflows/v2/capability_executor.go (L142-260)
```go
func (c *ExecutionHelper) callCapability(ctx context.Context, request *sdkpb.CapabilityRequest) (*sdkpb.CapabilityResponse, error) {
	execLogger := c.logger().With("workflowExecutionID", c.WorkflowExecutionID, "capabilityID", request.Id, "callbackID", request.CallbackId, "method", request.Method)
	// TODO (CAPPL-735): use request.Metadata.WorkflowExecutionId to associate the call with a specific execution
	capability, err := c.cfg.CapRegistry.GetExecutable(ctx, request.Id)
	if err != nil {
		return nil, fmt.Errorf("action capability not found: %w, ", err)
	}

	info, err := capability.Info(ctx)
	if err != nil {
		return nil, fmt.Errorf("capability info not found: %w", err)
	}

	if isSystemCapability(info.ID) {
		return nil, fmt.Errorf("capability %q is system-only and cannot be called from a workflow", info.ID)
	}

	localNode := c.localNode.Load()

	// If the capability info is missing a DON, then
	// the capability is local, and we should use the localNode's DON ID.
	var donID uint32
	if !info.IsLocal {
		if info.DON == nil {
			return nil, fmt.Errorf("remote capability info is missing DON field, ID: %s", info.ID)
		}
		donID = info.DON.ID
	} else {
		donID = localNode.WorkflowDON.ID
	}

	config, err := c.cfg.CapRegistry.ConfigForCapability(ctx, info.ID, donID)
	if err != nil {
		// not explicitly an error case and more relevant (helpful) logging occurs in the metering package
		// debug level should be sufficient here
		execLogger.Debugw("capability config not found", "err", err)
	}

	meterReport, ok := c.meterReports.Get(c.WorkflowExecutionID)
	if !ok {
		execLogger.Error("no metering report found")
	}

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
	executionEnd := c.cfg.Clock.Now()
	executionDuration := executionEnd.Sub(executionStart)
	c.executionProfile.recordStepEnd(meteringRef, executionEnd, err != nil)

	c.metrics.With(platform.KeyCapabilityID, request.Id).UpdateCapabilityExecutionDurationHistogram(ctx, int64(executionDuration.Seconds()))
	if err != nil {
```

**File:** core/services/workflows/metering/metering_test.go (L1764-1798)
```go
	t.Run("happy path with zero reserve and insufficient balance does not block workflow execution", func(t *testing.T) {
		t.Parallel()

		billingClient := mocks.NewBillingClient(t)
		billingClient.EXPECT().GetWorkflowExecutionRates(mock.Anything, mock.Anything).
			Return(&billing.GetWorkflowExecutionRatesResponse{
				RateCards: successRates,
			}, nil)
		billingClient.EXPECT().ReserveCredits(mock.Anything, mock.Anything).
			Return(&successZeroReserveResponseWithRates, nil)

		report := newTestReport(t, logger.Nop(), billingClient)

		require.NoError(t, report.Reserve(t.Context()))

		// Deduct and Settle a few times to consume credits
		// Each deduction of 2 units of compute consumes 1 credit (rate: 2 units per credit)
		_, err := report.Deduct("step1", ByResource(testUnitA, "", decimal.NewFromInt(2)))
		require.ErrorIs(t, err, ErrInsufficientBalance) // insufficient balance does not block workflow execution
		require.NoError(t, report.Settle("step1", capabilities.ResponseMetadata{Metering: []capabilities.MeteringNodeDetail{
			{Peer2PeerID: "node1", SpendUnit: testUnitA, SpendValue: "2"},
		}}))

		_, err = report.Deduct("step2", ByResource(testUnitA, "", decimal.NewFromInt(4)))
		require.ErrorIs(t, err, ErrInsufficientBalance)
		require.NoError(t, report.Settle("step2", capabilities.ResponseMetadata{Metering: []capabilities.MeteringNodeDetail{
			{Peer2PeerID: "node2", SpendUnit: testUnitA, SpendValue: "4"},
		}}))

		_, err = report.Deduct("step3", ByResource(testUnitA, "", decimal.NewFromInt(2)))
		require.ErrorIs(t, err, ErrInsufficientBalance)
		require.NoError(t, report.Settle("step3", capabilities.ResponseMetadata{Metering: []capabilities.MeteringNodeDetail{
			{Peer2PeerID: "node3", SpendUnit: testUnitA, SpendValue: "2"},
		}}))

```
