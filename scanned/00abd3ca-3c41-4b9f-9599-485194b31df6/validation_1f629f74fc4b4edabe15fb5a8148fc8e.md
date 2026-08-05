## Verdict: Confirmed for the barrier logic; entry path via `pallet_xcm::execute` in `yet-another-parachain` specifically is unverified (likely blocked)

### Title
`DenyReserveTransferToRelayChain` deny-filter is bypassed when the denied instruction is nested inside `SetAppendix`/`SetErrorHandler`/`ExecuteWithOrigin` unless wrapped in `DenyRecursively` - (File: `polkadot/xcm/xcm-builder/src/barriers.rs`)

### Summary
`DenyReserveTransferToRelayChain::deny_execution` only scans the top-level instruction slice passed to it and never inspects the nested `Xcm` programs carried inside `SetAppendix`, `SetErrorHandler`, or `ExecuteWithOrigin`. The `XcmExecutor::execute` entry point invokes `Config::Barrier::should_execute` exactly once, on the outer message, before beginning the run loop; the appendix/error-handler XCM is only extracted and executed later via `vm.take_appendix()`/`vm.take_error_handler()` without any further barrier re-evaluation. This is confirmed by the codebase's own test, which explicitly shows the plain (non-recursive) `DenyThenTry<DenyReserveTransferToRelayChain, AllowAll>` returns `Ok` when the denied `DepositReserveAsset{dest: Parent, ..}` is wrapped in `SetAppendix`.

### Finding Description
- `DenyReserveTransferToRelayChain::deny_execution` (`polkadot/xcm/xcm-builder/src/barriers.rs:555-591`) does `message.matcher().match_next_inst_while(...)` over the flat instruction slice, matching `InitiateReserveWithdraw`, `DepositReserveAsset`, `TransferReserveAsset` targeting `parents:1, interior: Here`. It has no `SetAppendix`/`SetErrorHandler`/`ExecuteWithOrigin` arm, so those instructions fall through to `_ => Ok(ControlFlow::Continue(()))` without inspecting their embedded `Xcm<RuntimeCall>` payload. [1](#0-0) 
- `DenyThenTry::should_execute` runs `Deny::deny_execution` once on the top-level `message` and then `Allow::should_execute`. [2](#0-1) 
- `XcmExecutor::execute` calls `Config::Barrier::should_execute` a single time on the outer `message` before the processing loop begins; `SetAppendix`/`SetErrorHandler` contents are only executed afterward via `vm.take_error_handler()` / `vm.take_appendix()`, with no re-invocation of the barrier on the nested program. [3](#0-2) 
- `SetAppendix`/`SetErrorHandler` instruction handling simply stores the nested `Xcm` in `self.appendix`/`self.error_handler` registers for later execution, with no filtering. [4](#0-3) 
- `DenyRecursively<Inner>` was specifically built to fix this gap by walking into `SetAppendix`/`SetErrorHandler`/`ExecuteWithOrigin` nested XCMs recursively (with a recursion-depth guard). [5](#0-4) 
- The repository's own unit test proves the bypass for the non-recursive variant: `DenyThenTry<DenyReserveTransferToRelayChain, AllowAll>::should_execute` returns `Ok` (allowed) when a denied `DepositReserveAsset{dest: Location::parent(), ..}` is wrapped in `SetAppendix`, while the same message is denied by `DenyThenTry<DenyRecursively<DenyReserveTransferToRelayChain>, AllowAll>`. [6](#0-5) 
- `yet-another-parachain`'s `Barrier` type is configured as `TrailingSetTopicAsId<DenyThenTry<DenyReserveTransferToRelayChain, (...)>>` — i.e., the plain, non-recursive deny filter, matching the vulnerable configuration described in the question. [7](#0-6) 

However, on the specific reachable-path claim ("attacker submits via `pallet_xcm::execute`"), `yet-another-parachain`'s `pallet_xcm::Config` sets `type XcmExecuteFilter = Nothing;` with an explicit comment "Disable dispatchable execute on the XCM pallet." [8](#0-7) 
This filter is checked by `pallet_xcm::execute`'s dispatch logic before any XCM is handed to the executor. I was not able to fully confirm in this session (tool budget exhausted) whether `Nothing` unconditionally rejects the extrinsic for all messages, but by construction `Contains` for `Nothing` always returns `false`, meaning the `execute` call should be rejected for any local XCM before the barrier is ever reached. If that holds, the `pallet_xcm::execute` path specifically is not exploitable on `yet-another-parachain` — though other runtimes using the same `DenyThenTry<DenyReserveTransferToRelayChain, ...>` pattern with an enabled `XcmExecuteFilter` (or reachable via XCM messages sent from another chain and executed locally, e.g. via `Transact`/nested program delivered over HRMP/XCMP where a barrier check happens on the receiving chain) would not have this mitigating factor and remain exploitable through the barrier logic itself.

### Impact Explanation
Where the local `Barrier` is `DenyThenTry<DenyReserveTransferToRelayChain, Allow>` without `DenyRecursively`, and where the local chain can be caused to execute an attacker-supplied XCM program (via `pallet_xcm::execute` if permitted, or as the local leg of a message routed/received from elsewhere), an attacker can hide `InitiateReserveWithdraw`/`DepositReserveAsset`/`TransferReserveAsset` targeting `Location::parent()` inside `SetAppendix` or `SetErrorHandler` and have it execute despite the deny-filter being present, defeating the explicit security control referenced by the barrier's own doc comment (`paritytech/polkadot#5233`).

### Likelihood Explanation
The bypass in the barrier logic itself is proven deterministically by the existing repository test (no mocks needed, pure logic). Feasibility of a live exploit is entirely gated by whether the runtime's `pallet_xcm::execute` (or an equivalent locally-executed entry point) is reachable by an unprivileged signed account, which is runtime-specific — in `yet-another-parachain`, `XcmExecuteFilter = Nothing` appears to close this off, so the "as seen in yet-another-parachain" precondition claiming direct reachability via `pallet_xcm::execute` is not substantiated by the code path I could review, though the underlying barrier weakness is real and reachable in any configuration that uses `DenyReserveTransferToRelayChain` without `DenyRecursively` and permits local XCM execution.

### Recommendation
Wrap `DenyReserveTransferToRelayChain` in `DenyRecursively` wherever it's used as a security control against relay-chain reserve transfers, i.e. change `DenyThenTry<DenyReserveTransferToRelayChain, Allow>` to `DenyThenTry<DenyRecursively<DenyReserveTransferToRelayChain>, Allow>` in every runtime that has this barrier, including `yet-another-parachain`, and audit any runtime with `XcmExecuteFilter != Nothing` for this exact bypass.

### Proof of Concept
This is already demonstrated in-repo by `deny_recursively_then_try_works` in `polkadot/xcm/xcm-builder/src/tests/barriers.rs`:
- Assert `DenyThenTry<DenyReserveTransferToRelayChain, AllowAll>::should_execute` on `Xcm([SetAppendix(Xcm([DepositReserveAsset{dest: Parent, ..}]))])` returns `Ok(())` (bypass).
- Assert `DenyThenTry<DenyRecursively<DenyReserveTransferToRelayChain>, AllowAll>::should_execute` on the same message returns `Err(_)` (correctly denied). [9](#0-8) 
For a runtime-level integration test, use an `xcm-emulator`/`xcm-simulator` scenario against a runtime whose `Barrier` uses the plain (non-recursive) form and whose `XcmExecuteFilter` permits local execution: submit `pallet_xcm::execute` with `Xcm([SetAppendix(Xcm([DepositReserveAsset{ dest: Location::parent(), .. }]))])` from a signed account and assert the appendix executes (reserve withdrawal to the relay chain succeeds) rather than the extrinsic failing with `XcmError::Barrier`.

### Citations

**File:** polkadot/xcm/xcm-builder/src/barriers.rs (L542-551)
```rust
	fn should_execute<RuntimeCall>(
		origin: &Location,
		message: &mut [Instruction<RuntimeCall>],
		max_weight: Weight,
		properties: &mut Properties,
	) -> Result<(), ProcessMessageError> {
		Deny::deny_execution(origin, message, max_weight, properties)?;
		Allow::should_execute(origin, message, max_weight, properties)
	}
}
```

**File:** polkadot/xcm/xcm-builder/src/barriers.rs (L562-587)
```rust
		message.matcher().match_next_inst_while(
			|_| true,
			|inst| match inst {
				InitiateReserveWithdraw {
					reserve: Location { parents: 1, interior: Here },
					..
				} |
				DepositReserveAsset { dest: Location { parents: 1, interior: Here }, .. } |
				TransferReserveAsset { dest: Location { parents: 1, interior: Here }, .. } => {
					Err(ProcessMessageError::Unsupported) // Deny
				},

				// An unexpected reserve transfer has arrived from the Relay Chain. Generally,
				// `IsReserve` should not allow this, but we just log it here.
				ReserveAssetDeposited { .. }
					if matches!(origin, Location { parents: 1, interior: Here }) =>
				{
					tracing::debug!(
						target: "xcm::barriers",
						"Unexpected ReserveAssetDeposited from the Relay Chain",
					);
					Ok(ControlFlow::Continue(()))
				},

				_ => Ok(ControlFlow::Continue(())),
			},
```

**File:** polkadot/xcm/xcm-builder/src/barriers.rs (L648-683)
```rust
impl<Inner: DenyExecution> DenyExecution for DenyRecursively<Inner> {
	/// Denies execution of restricted local nested XCM instructions.
	///
	/// This checks for `SetAppendix`, `SetErrorHandler`, and `ExecuteWithOrigin` instruction
	/// applying the deny filter **recursively** to any nested XCMs found.
	fn deny_execution<RuntimeCall>(
		origin: &Location,
		instructions: &mut [Instruction<RuntimeCall>],
		max_weight: Weight,
		properties: &mut Properties,
	) -> Result<(), ProcessMessageError> {
		// First, check if the top-level message should be denied.
		Inner::deny_execution(origin, instructions, max_weight, properties).inspect_err(|e| {
			tracing::debug!(
				target: "xcm::barriers",
				"DenyRecursively::Inner denied execution, origin: {:?}, instructions: {:?}, max_weight: {:?}, properties: {:?}, error: {:?}",
				origin, instructions, max_weight, properties, e
			);
		})?;

		// If the top-level check passes, check nested instructions recursively.
		instructions.matcher().match_next_inst_while(
			|_| true,
			|inst| match inst {
				SetAppendix(nested_xcm) |
				SetErrorHandler(nested_xcm) |
				ExecuteWithOrigin { xcm: nested_xcm, .. } => Self::deny_recursively::<RuntimeCall>(
					origin, nested_xcm, max_weight, properties,
				),
				_ => Ok(ControlFlow::Continue(())),
			},
		)?;

		// Permit everything else
		Ok(())
	}
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L274-313)
```rust
		if let Err(e) = Config::Barrier::should_execute(
			&origin,
			message.inner_mut(),
			xcm_weight,
			&mut properties,
		) {
			tracing::trace!(
				target: "xcm::execute",
				?origin,
				?message,
				?properties,
				error = ?e,
				"Barrier blocked execution",
			);

			return Outcome::Incomplete {
				used: xcm_weight, // Weight consumed before the error
				error: InstructionError { index: 0, error: XcmError::Barrier }, // The error that occurred
			};
		}

		*id = properties.message_id.unwrap_or(*id);

		let mut vm = Self::new(origin, *id);
		vm.message_weight = xcm_weight;

		while !message.0.is_empty() {
			let result = vm.process(message);
			tracing::trace!(target: "xcm::execute", ?result, "Message executed");
			message = match result {
				Err(error) => {
					vm.total_surplus.saturating_accrue(error.weight);
					vm.error = Some((error.index, error.xcm_error));
					vm.take_error_handler().or_else(|| vm.take_appendix())
				},
				Ok(()) => {
					vm.drop_error_handler();
					vm.take_appendix()
				},
			}
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L1512-1543)
```rust
			SetErrorHandler(mut handler) => {
				let handler_weight = Config::Weigher::weight(&mut handler, Weight::MAX)
					.map_err(|error| {
						tracing::debug!(
							target: "xcm::executor::SetErrorHandler",
							?error,
							?handler,
							"Failed to calculate weight"
						);
						XcmError::WeightNotComputable
					})?;
				self.total_surplus.saturating_accrue(self.error_handler_weight);
				self.error_handler = handler;
				self.error_handler_weight = handler_weight;
				Ok(())
			},
			SetAppendix(mut appendix) => {
				let appendix_weight = Config::Weigher::weight(&mut appendix, Weight::MAX)
					.map_err(|error| {
						tracing::debug!(
							target: "xcm::executor::SetErrorHandler",
							?error,
							?appendix,
							"Failed to calculate weight"
						);
						XcmError::WeightNotComputable
					})?;
				self.total_surplus.saturating_accrue(self.appendix_weight);
				self.appendix = appendix;
				self.appendix_weight = appendix_weight;
				Ok(())
			},
```

**File:** polkadot/xcm/xcm-builder/src/tests/barriers.rs (L1190-1217)
```rust
#[test]
fn deny_recursively_then_try_works() {
	type Barrier = DenyThenTry<DenyRecursively<DenyReserveTransferToRelayChain>, AllowAll>;
	let xcm = Xcm::<Instruction<()>>(vec![DepositReserveAsset {
		assets: Wild(All),
		dest: Location::parent(),
		xcm: vec![].into(),
	}]);
	let origin = Here.into_location();
	let max_weight = Weight::from_parts(10, 10);
	let mut properties = props(Weight::zero());

	// Should deny the original XCM
	let result =
		Barrier::should_execute(&origin, xcm.clone().inner_mut(), max_weight, &mut properties);
	assert!(result.is_err());

	// Should deny with `SetAppendix`
	let mut message = Xcm::<Instruction<()>>(vec![SetAppendix(xcm.clone())]);
	let result =
		Barrier::should_execute(&origin, message.clone().inner_mut(), max_weight, &mut properties);
	assert!(result.is_err());

	// Should allow with `SetAppendix` for the original `DenyThenTry`
	type OriginalBarrier = DenyThenTry<DenyReserveTransferToRelayChain, AllowAll>;
	let result =
		OriginalBarrier::should_execute(&origin, message.inner_mut(), max_weight, &mut properties);
	assert!(result.is_ok());
```

**File:** cumulus/parachains/runtimes/testing/yet-another-parachain/src/xcm_config.rs (L116-132)
```rust
pub type Barrier = TrailingSetTopicAsId<
	DenyThenTry<
		DenyReserveTransferToRelayChain,
		(
			TakeWeightCredit,
			WithComputedOrigin<
				(
					AllowTopLevelPaidExecutionFrom<Everything>,
					AllowExplicitUnpaidExecutionFrom<ParentOrParentsExecutivePlurality>,
					// ^^^ Parent and its exec plurality get free execution
				),
				UniversalLocation,
				ConstU32<8>,
			>,
		),
	>,
>;
```

**File:** cumulus/parachains/runtimes/testing/yet-another-parachain/src/xcm_config.rs (L186-188)
```rust
	type XcmExecuteFilter = Nothing;
	// ^ Disable dispatchable execute on the XCM pallet.
	// Needs to be `Everything` for local testing.
```
