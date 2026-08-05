### Title
Repeated re-weighing of chained `SetAppendix`/`SetErrorHandler` payloads causes quadratic weighing cost not reflected in accounted weight - (File: polkadot/xcm/xcm-executor/src/lib.rs)

### Summary
`XcmExecutor::execute` computes a single upper-bound weight for the whole message once via `Config::Weigher::weight()` in `prepare()`, but each time a `SetAppendix`/`SetErrorHandler` instruction is *executed* it calls `Config::Weigher::weight(&mut appendix/handler, Weight::MAX)` again with a brand-new `instructions_left = M::get()` budget [1](#0-0) . Because the executor's outer `while` loop in `execute()` sequentially processes the taken appendix/error-handler as a new top-level `process()` call, an attacker can chain `SetAppendix` instructions inside each other's appendix so that at every level the executor re-weighs the remaining (still MaxInstructions-bounded) sub-tree, yielding weighing work that grows roughly quadratically with nesting depth while only linear weight is ever debited from the budget.

### Finding Description
`FixedWeightBounds::weight()` initializes a fresh `instructions_left = M::get()` and calls `weight_with_limit` [2](#0-1) . Inside `weight_with_limit`, nested `SetErrorHandler`/`SetAppendix`/`ExecuteWithOrigin` instructions share the *same* `instructions_left` counter as the outer message, so the whole nested tree is bounded once by a single `MaxInstructions` budget at `prepare()` time [3](#0-2) . This matches the test `weight_bounds_should_respect_instructions_limit`, confirming that "hidden" nested instructions are counted against one shared limit [4](#0-3) .

However, at actual execution time, `process_instruction` handles `SetAppendix`/`SetErrorHandler` by calling `Config::Weigher::weight(&mut appendix, Weight::MAX)` again, which resets `instructions_left` to a **fresh** `M::get()` budget independent of what was already spent during `prepare()` [1](#0-0) . This weighing call is a real traversal cost (CPU work), not accounted anywhere in the final `weight_used` figure — it only produces `appendix_weight`/`error_handler_weight`, used for bookkeeping surplus/refund, not for metering the CPU cost of the weighing traversal itself.

`XcmExecutor::execute`'s outer loop is not a single recursive call bounded by `RECURSION_LIMIT`; it iteratively re-invokes `vm.process(message)` on whatever `take_error_handler()`/`take_appendix()` returns [5](#0-4) . Each of these calls is a *fresh* entry into `process()`, which resets the `recursion_count` guard (`using_once`) [6](#0-5) , so `RECURSION_LIMIT` (10) only bounds true Rust call-stack recursion within one `process()` invocation, not the length of an appendix-chain processed by the outer `while` loop.

Exploit construction: an attacker crafts a message such as
```
SetAppendix([ SetAppendix([ SetAppendix([ ... ClearOrigin ]) ]) ])
```
with depth D, where the total instruction count of the whole nested tree is ≤ `MaxInstructions` (so `prepare()`'s single weighing pass succeeds and the Barrier/weight checks pass normally). When executed:
1. The outer message's `SetAppendix` instruction executes → calls `weight()` on the depth-(D-1) sub-tree (O(D) work).
2. That sub-tree becomes the new appendix; the `while` loop in `execute()` processes it as message #2, whose own `SetAppendix` instruction triggers another `weight()` call on the depth-(D-2) sub-tree (O(D-1) work).
3. This repeats down the chain, giving total weighing cost O(D) + O(D-1) + ... + O(1) = O(D²), while the officially debited/accounted weight only reflects each instruction's declared unit cost once (O(D)).

The Barrier (`Config::Barrier::should_execute`) is invoked only once at the very start of `execute()`, not per appendix iteration, so it cannot re-validate or reject the chain as it unwinds. `MaxInstructions`/`FixedWeightBounds` protects against unboundedly large *declared* instruction counts, but not against the *repeated re-weighing* of the same already-counted instructions triggered by chained appendices.

### Impact Explanation
A single crafted XCM (delivered via HRMP/XCMP/DMP into a parachain's `MessageQueue`) can force the `XcmExecutor` to spend real CPU time re-weighing nested appendix/error-handler sub-trees repeatedly, quadratic in nesting depth, while the weight accounted to that message (and thus the amount deducted from `MessageQueue`'s `ServiceWeight`/`WeightMeter` budget during `on_initialize`/`service_queues`) reflects only the linear, once-counted instruction weights. This divergence between accounted weight and actual computational cost could let a single message consume more wall-clock/CPU time than its accounted weight implies, potentially causing block-time overruns or degraded throughput for sibling queues serviced in the same `service_queues_impl` call, since the `WeightMeter` believes it has budget remaining based on the (too-low) accounted weight.

### Likelihood Explanation
The precondition (crafting a message whose nested `SetAppendix` chain fits under `MaxInstructions` counted once, e.g. depth ~`MaxInstructions/2` for typical configs like `MaxInstructions = 100`–`1000` seen across parachain runtimes) is fully reachable by any unprivileged account able to send an HRMP/XCMP/DMP message, subject only to normal Barrier/origin rules (which only gate at the top level, not per-appendix). The magnitude of the quadratic blowup is bounded by `MaxInstructions²`, which for commonly configured values (100–1000) yields a bounded, not catastrophic, extra cost (thousands to a few million weighing operations) — this limits practical severity but the architectural gap (weight metering not accounting for repeated re-weighing work) is real and reproducible deterministically, not probabilistic.

### Recommendation
- Do not re-weigh the appendix/error-handler payload from scratch every time it is set/executed; instead, either (a) weigh the whole message once up-front (already done in `prepare()`) and thread the already-computed nested weights through instruction execution instead of calling `Config::Weigher::weight()` again inside `process_instruction`'s `SetAppendix`/`SetErrorHandler` handling, or (b) cap the total number of `SetAppendix`/`SetErrorHandler` "hops" processed across the entire `execute()` outer loop (in addition to `RECURSION_LIMIT`, which only guards Rust stack recursion within one `process()` call), charging real weight for every re-weighing invocation from a single shared, message-wide instruction/weighing budget.
- Alternatively, account for the CPU cost of the `Weigher::weight()` call itself (proportional to sub-tree size) directly against `weight_used`/the `WeightMeter`, so that this cost is never omitted from `MessageQueue`'s consumption bookkeeping.

### Proof of Concept
Rust integration test plan (in `polkadot/xcm/xcm-executor/src/tests` or an xcm-emulator test):
1. Configure `FixedWeightBounds<UnitWeight, RuntimeCall, MaxInstructions=100>` as `Weigher`.
2. Build a message: `Xcm(vec![SetAppendix(Xcm(vec![SetAppendix(Xcm(vec![... nested to depth ~48 ..., ClearOrigin]))]))])` such that total instruction count ≤ 100 (so `prepare()` succeeds).
3. Call `XcmExecutor::<Config>::prepare_and_execute(origin, message, &mut hash, weight_limit, Weight::zero())` while instrumenting/counting invocations of `Weigher::weight()` (e.g., via a wrapper `Weigher` type that increments an atomic counter each call).
4. Assert: number of `weight()` invocations scales quadratically with nesting depth D (e.g., invocations ≈ D, but total instructions traversed across those invocations ≈ D(D+1)/2), while `Outcome::used` reflects only the linear sum of declared instruction weights.
5. Optionally wrap in an `xcm-emulator`/`xcm-simulator` test sending this message via HRMP into a parachain and measuring wall-clock time of `MessageQueue::service_queues` versus the `weight_used` reported in the `Processed` event, asserting the wall-clock/weighing-operation count diverges from the naive linear expectation by more than a fixed tolerance factor.

### Citations

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L300-314)
```rust
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
		}
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L843-877)
```rust
	fn process(&mut self, xcm: Xcm<Config::RuntimeCall>) -> Result<(), ExecutorError> {
		tracing::trace!(
			target: "xcm::process",
			origin = ?self.origin_ref(),
			total_surplus = ?self.total_surplus,
			total_refunded = ?self.total_refunded,
			error_handler_weight = ?self.error_handler_weight,
		);
		let mut result = Ok(());
		for (i, mut instr) in xcm.0.into_iter().enumerate() {
			match &mut result {
				r @ Ok(()) => {
					// Initialize the recursion count only the first time we hit this code in our
					// potential recursive execution.
					let inst_res = recursion_count::using_once(&mut 1, || {
						recursion_count::with(|count| {
							if *count > RECURSION_LIMIT {
								return None;
							}
							*count = count.saturating_add(1);
							Some(())
						})
						.flatten()
						.ok_or(XcmError::ExceedsStackLimit)?;

						// Ensure that we always decrement the counter whenever we finish processing
						// the instruction.
						defer! {
							recursion_count::with(|count| {
								*count = count.saturating_sub(1);
							});
						}

						self.process_instruction(instr)
					});
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

**File:** polkadot/xcm/xcm-builder/src/weight.rs (L44-58)
```rust
	fn weight(message: &mut Xcm<C>, weight_limit: Weight) -> Result<Weight, InstructionError> {
		tracing::trace!(target: "xcm::weight", ?message, "FixedWeightBounds");
		let mut instructions_left = M::get();
		Self::weight_with_limit(message, &mut instructions_left, weight_limit).inspect_err(
			|&error| {
				tracing::debug!(
					target: "xcm::weight",
					?error,
					?instructions_left,
					message_length = ?message.0.len(),
					"Weight calculation failed for message"
				);
			},
		)
	}
```

**File:** polkadot/xcm/xcm-builder/src/weight.rs (L103-124)
```rust
	fn instr_weight_with_limit(
		instruction: &mut Instruction<C>,
		instructions_left: &mut u32,
		weight_limit: Weight,
	) -> Result<Weight, XcmError> {
		let instruction_weight = match instruction {
			Transact { ref mut call, .. } => {
				call.ensure_decoded()
					.map_err(|_| XcmError::FailedToDecode)?
					.get_dispatch_info()
					.call_weight
			},
			SetErrorHandler(xcm) | SetAppendix(xcm) | ExecuteWithOrigin { xcm, .. } => {
				Self::weight_with_limit(xcm, instructions_left, weight_limit)
					.map_err(|outcome_error| outcome_error.error)?
			},
			_ => Weight::zero(),
		};
		let total_weight = T::get().checked_add(&instruction_weight).ok_or(XcmError::Overflow)?;
		Ok(total_weight)
	}
}
```

**File:** polkadot/xcm/xcm-builder/src/tests/weight.rs (L195-219)
```rust
	let log_capture = capture_test_logs!({
		let mut message =
			Xcm(vec![SetErrorHandler(Xcm(vec![SetErrorHandler(Xcm(vec![SetErrorHandler(
				Xcm(vec![ClearOrigin]),
			)]))]))]);
		// 4 instructions are too many, even when it's just one that's 3 levels deep.
		assert_eq!(
			<TestConfig as Config>::Weigher::weight(&mut message, Weight::MAX),
			Err(InstructionError { index: 0, error: XcmError::ExceedsStackLimit })
		);
	});
	assert!(log_capture.contains(
		"Weight calculation failed for message error=InstructionError { index: 0, error: ExceedsStackLimit } instructions_left=0 message_length=1"
	));

	let log_capture = capture_test_logs!({
		let mut message =
			Xcm(vec![SetErrorHandler(Xcm(vec![SetErrorHandler(Xcm(vec![ClearOrigin]))]))]);
		// 3 instructions are OK.
		assert_eq!(
			<TestConfig as Config>::Weigher::weight(&mut message, Weight::MAX),
			Ok(Weight::from_parts(30, 30))
		);
	});
	assert!(!log_capture.contains("Weight calculation failed for message"));
```
