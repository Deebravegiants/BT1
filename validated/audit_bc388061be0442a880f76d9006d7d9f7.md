This confirms the mechanism concretely: `capability.Info()` returns `SpendTypes`, which can be defined by any capability (including custom/community capabilities registered by a workflow owner), and `capability.Execute()` returns `capabilities.ResponseMetadata.Metering[].SpendUnit`, which is fully attacker-controlled data returned by the executed capability itself — not validated against the billing service's rate card before it triggers `switchToMeteringMode`. [1](#0-0) 

### Title
Workflow metering silently disables all future billing for an execution when a capability reports an unrecognized spend type - ([File: core/services/workflows/metering/metering.go])

### Summary
The metering "fail open" logic in `ByResource`/`ByDerivedAvailability` calls `switchToMeteringMode` on *any* error returned by `balance.ConvertToBalance`, including the common/expected case of an unrecognized spend-type unit. Once `meteringMode` is set, all subsequent `Deduct` calls in that execution skip balance decrement entirely, i.e. every further capability invocation in the workflow execution becomes free of charge. This mirrors the reported MemoryGrow bug class: a specific, easily-triggerable input condition (a spend unit missing from the rate card, or the explicitly special-cased `"RPC_EVM"` unit) escapes the normal pricing/metering code path and lets a workflow author consume node resources far below the intended cost.

### Finding Description
`ByResource` unconditionally flips the whole execution into `meteringMode` whenever `ConvertToBalance` returns an error: [2](#0-1) 

`convertToBalance` returns `ErrResourceTypeNotFound` for any spend type/unit string not present in the billing-service-supplied rate card: [3](#0-2) 

Once `meteringMode` is true, `Deduct` (via both `ByResource` and `ByDerivedAvailability`) returns early without decrementing the local credit balance for *every subsequent step of that execution*: [4](#0-3) [5](#0-4) 

Additionally, `Settle` explicitly and permanently ignores `"RPC_EVM"` spend units from local balance settlement (a hardcoded bypass, acknowledged in code as a stopgap): [6](#0-5) 

The `SpendUnit`/`SpendTypes` values that drive this logic originate from the executed capability itself (`capability.Info().SpendTypes` and `capabilities.ResponseMetadata.Metering[].SpendUnit`), which are passed straight into the metering report without being validated against the rate card at declaration time: [1](#0-0) 

This was reproduced by the project's own test, which shows that an ordinary mismatch between a capability's reported spend unit and the billing rate card silently flips `meteringMode` to `true` for the rest of the execution: [7](#0-6) 

### Impact Explanation
An unprivileged workflow owner who triggers workflow executions (e.g. via the internet-facing HTTP trigger gateway, `httpTriggerHandler.HandleUserTriggerRequest`) can register or invoke any capability — including a workflow-supplied/community capability — that reports even one metering unit not present in the current billing rate card (or the hardcoded `"RPC_EVM"` unit). Doing so switches the entire in-flight execution's `Report` into `meteringMode`, after which *all* subsequent capability calls in that execution proceed without any credit deduction check (`getMaxSpendForInvocation` short-circuits to "unlimited", `Deduct` skips `balance.Minus`). This lets a malicious actor drive arbitrarily expensive, resource-intensive capability calls (compute, network, gas-metered on-chain writes) on the DON at effectively zero cost for the remainder of the execution — directly analogous to the reported MemoryGrow underpricing enabling cheap resource exhaustion of validators/nodes.

### Likelihood Explanation
Likely and easily reachable: any workflow owner controls which capabilities their workflow calls and, for capabilities not tightly restricted, can trivially cause a spend-unit/rate-card mismatch (a known, already-observed condition per the code comment "TODO: explicitly ignore RPC_EVM spend types for now" and the associated test). No special privileges beyond being a workflow owner/tenant are required, and the condition is deterministic and repeatable per execution.

### Recommendation
- Do not treat "spend unit missing from rate card" as a blanket trigger for disabling metering for the rest of the execution; instead fail closed for that specific step (deny/charge a conservative default) while leaving metering active for all other steps/spend types.
- Remove or properly implement billing support for `"RPC_EVM"` spend units rather than unconditionally skipping their settlement.
- Validate a capability's declared `SpendTypes` against the current rate card at capability registration/config time, rejecting or flagging capabilities whose spend types cannot be priced, instead of discovering the mismatch at execution time.
- Add fuzz/property testing around `Report.Deduct`/`Settle` with adversarial `SpendUnit` values to ensure metering mode cannot be forced by a single non-billable capability call.

### Proof of Concept
1. A workflow owner registers/uses a capability (or a capability declares in `Info()`) a `SpendType`/`Execute()` `ResponseMetadata.Metering[].SpendUnit` such as `"RPC_EVM"` or any unit not present in the billing service's rate card returned to `NewReport`.
2. The workflow is triggered (e.g. through the gateway's HTTP trigger flow), the engine calls `ExecutionHelper.callCapability`, which calls `meterReport.Deduct(..., metering.ByDerivedAvailability(...))`.
3. `ConvertToBalance` returns `ErrResourceTypeNotFound` (or the unit is `"RPC_EVM"`), causing `switchToMeteringMode` to set `r.meteringMode = true`.
4. Every subsequent capability call in the same execution's `Deduct`/`Settle` now bypasses `balance.Minus`/`ConvertToBalance` charge accumulation, as shown in `metering.go` lines 333-339, 372-378, and 463-469 — allowing unmetered, effectively free invocation of expensive capabilities for the rest of that execution.

### Citations

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

**File:** core/services/workflows/metering/metering.go (L325-339)
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
	}
```

**File:** core/services/workflows/metering/metering.go (L372-378)
```go
		// if in metering mode, exit early without modifying local balance
		if r.meteringMode {
			return []capabilities.SpendLimit{}, nil
		}

		return r.creditToSpendingLimits(info, config, limit.Decimal), r.balance.Minus(limit.Decimal)
	}
```

**File:** core/services/workflows/metering/metering.go (L463-469)
```go
		// TODO: explicitly ignore RPC_EVM spend types for now -
		// this check causes TestEngine_Metering_ValidBillingClient/billing_type_and_capability_settle_spend_type_mismatch ./core/services/workflows/v2
		// to fail because the capability is returning a spend type that isn't gas or compute
		// This should be removed when we have proper support for non-gas/compute spend types
		if unit == "RPC_EVM" {
			continue
		}
```

**File:** core/services/workflows/metering/balance_store.go (L49-66)
```go
func (bs *balanceStore) convertToBalance(fromResourceType string, amount decimal.Decimal) (decimal.Decimal, error) {
	rate, ok := bs.conversions[fromResourceType]
	if !ok {
		return amount, ErrResourceTypeNotFound
	}

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

**File:** core/services/workflows/v2/engine_test.go (L1404-1458)
```go
			Return(capabilities.CapabilityResponse{
				Metadata: capabilities.ResponseMetadata{
					Metering: []capabilities.MeteringNodeDetail{
						{
							Peer2PeerID: "local",
							// SpendUnit does not match units from billing or ratios
							SpendUnit:  "COMPUTE",
							SpendValue: "100",
						},
						{
							Peer2PeerID: "local",
							SpendUnit:   billing.ResourceType_RESOURCE_TYPE_NETWORK.String(),
							SpendValue:  "1000",
						},
					},
				},
			}, nil).Once()

		// Mock workflow execution that calls the metered capability
		module.EXPECT().
			Execute(matches.AnyContext, mock.Anything, mock.Anything).
			Run(func(ctx context.Context, request *sdkpb.ExecuteRequest, executor host.ExecutionHelper) {
				// Simulate calling the slow capability from within the workflow
				_, errCap := executor.CallCapability(ctx, &sdkpb.CapabilityRequest{
					Id:         "metered-capability-2",
					Method:     "execute",
					CallbackId: 1,
					Payload:    nil,
				})

				require.NoError(t, errCap)
			}).Return(nil, nil).Once()

		// Trigger the execution
		mockTriggerEvent := capabilities.TriggerEvent{
			TriggerType: "basic-trigger@1.0.0",
			ID:          "metering_capability_test_4",
			Payload:     nil,
		}

		eventCh <- capabilities.TriggerResponse{
			Event: mockTriggerEvent,
		}

		// Wait for execution to finish with error status
		executionID := <-executionFinishedCh
		wantExecID := wantExecutionID(t, cfg.WorkflowID, mockTriggerEvent.ID, 0)

		require.Equal(t, wantExecID, executionID)
		capability.AssertExpectations(t)

		logged := logs.TakeAll()
		require.Len(t, logged, 1)
		assert.Contains(t, logged[0].Message, "metering mode")
	})
```
