### Title
Unbounded execute() loop via self-re-arming SetErrorHandler/Trap allows a single XCM message to consume disproportionate weight/CPU vs. its `prepare()`-computed weight - (File: polkadot/xcm/xcm-executor/src/lib.rs)

### Summary
The `RECURSION_LIMIT` guard in `xcm_executor::XcmExecutor::process` only bounds instruction-nesting depth *within a single call* to `process()`, because the recursion counter is reinitialized via `recursion_count::using_once(&mut 1, ...)` on every invocation. The outer `while !message.0.is_empty()` loop in `execute()`, which repeatedly swaps in the taken `error_handler`/`appendix` after an error, is not bounded by this counter or by any other iteration limit, so a message whose error handler re-arms itself (`SetErrorHandler` inside the handler pointing at an equivalent handler, followed by `Trap`) can cause the loop to run indefinitely within one `execute()` call.

### Finding Description
`XcmExecutor::execute` drives message processing as: [1](#0-0) 
Each iteration calls `vm.process(message)`, and on error takes `vm.take_error_handler().or_else(|| vm.take_appendix())` as the next `message` to process, looping until an empty program results.

`process()` enforces `RECURSION_LIMIT` via an `environmental` counter, but that counter is (re-)initialized fresh at the top of every `process()` call via `recursion_count::using_once(&mut 1, ...)`: [2](#0-1) 
This means `RECURSION_LIMIT` only guards against deep *static* nesting of `SetErrorHandler`/`SetAppendix`/`ExecuteWithOrigin` inside one program tree passed into a single `process()` call — it does not count how many times the outer `while` loop in `execute()` re-invokes `process()` with a freshly-taken error handler or appendix.

The `SetErrorHandler`/`SetAppendix` instruction handlers simply overwrite `self.error_handler`/`self.appendix` whenever they execute successfully: [3](#0-2) 
So if the error handler itself contains `SetErrorHandler(<same-or-equivalent-handler>)` followed by `Trap`, then: the top message errors (e.g., via `Trap`) → `take_error_handler()` returns the crafted handler → `process()` executes `SetErrorHandler(...)` (re-arming `self.error_handler`) then `Trap` (causing another error) → outer loop calls `take_error_handler()` again, which now returns the just re-armed handler → repeat indefinitely. `RECURSION_LIMIT` never fires here because each `process()` call only sees a 2-instruction flat program (`SetErrorHandler`, `Trap`), so the recursion counter never exceeds 2.

Separately, `FixedWeightBounds::weight_with_limit` (used by `prepare()`) computes the weight of nested `SetErrorHandler`/`SetAppendix` bodies exactly once, statically, based on the program's syntactic structure: [4](#0-3) 
It has no way to account for a handler that dynamically re-arms itself at runtime and is therefore executed an unbounded number of times — the static analysis and the dynamic execution diverge.

Weight bookkeeping during execution (`total_surplus`, `error.weight` accrual in `process`) only records how much *estimated* weight is consumed/refunded; it is not used as a hard budget that aborts the loop in `execute()`. There is no weight-based or iteration-based circuit breaker inside the `while` loop of `execute()` itself.

### Impact Explanation
Any unprivileged account able to submit an XCM for local execution (e.g., via `pallet_xcm::execute`, or a message delivered through XCMP/UMP/DMP queues that reaches `XcmExecutor::execute`) can craft a small, low-declared-weight message (`SetErrorHandler`/`Trap` ping-pong) whose actual execution never terminates or runs for far longer than its `prepare()`-computed weight implies. Since `execute()` performs the entire loop synchronously within one call, this ties up the calling context (e.g., `on_initialize`/`service_queues` weight budget, or the `pallet_xcm::execute` extrinsic's actual execution time) disproportionately to what was charged, and can starve/exhaust the per-block weight or wall-clock time shared by other queued messages or the block itself.

### Likelihood Explanation
The construct is a straightforward composition of standard, non-privileged XCM instructions (`SetErrorHandler`, `SetAppendix`, `Trap`, `ClearError`) that any XCM-issuing entity can build. The only barrier examined, `DenyRecursively`, checks *static* nesting depth and instruction identity, not dynamic re-arming behavior at runtime, so it does not stop this pattern. `RECURSION_LIMIT` (=10) is ineffective against this specific pattern because the counter resets per top-level `process()` call. Reachability depends on whatever `Barrier`/origin filters are configured for a given runtime's `XcmExecutor::Config` allowing local execution of `SetErrorHandler`/`Trap` from an unprivileged origin (e.g., via `pallet_xcm::execute` with `AllowUnpaidExecutionFrom`/`AllowExplicitUnpaidExecutionFrom` style configs), which is common for locally-originated “self execute” XCM paths.

### Recommendation
Add an explicit bound on the number of error-handler/appendix re-executions per `execute()` call (e.g., a fixed maximum iteration count for the outer `while` loop in `execute()`, independent of/complementary to `RECURSION_LIMIT`), and/or prevent an error handler/appendix from re-arming itself to a non-trivial program after being taken (e.g., clear-and-lock semantics so a handler cannot reinstall an equivalent handler that keeps firing). Alternatively, track cumulative "handler firings" weight against the message's declared `prepare()` weight and abort with `XcmError::WeightLimitReached`/`ExceedsStackLimit` once exceeded, rather than only recording it as `total_surplus`/error weight after the fact.

### Proof of Concept
Rust unit test in `polkadot/xcm/xcm-executor/src/tests` (or `polkadot/xcm/xcm-builder/src/tests/basic.rs`, following the pattern of `code_registers_should_work`):
1. Construct `let handler = Xcm(vec![SetErrorHandler(handler.clone()), Trap(1)])` (self-referential via a fixed small handler body reused) and set it as `SetErrorHandler(handler)` on a top-level message whose body is `Trap(1)`, with `SetAppendix` left empty/benign.
2. Compute `let limit = Weigher::weight(&mut message, Weight::MAX)` — record this as the "declared" weight (expected to be small, e.g., proportional to ~2-4 instructions).
3. Call `XcmExecutor::<TestConfig>::prepare_and_execute(origin, message, &mut hash, limit_or_generous_bound, Weight::zero())` with a watchdog (e.g., wrap in `std::thread` with timeout, or instrument `process()`/`process_instruction` call counts via a test hook) to assert that the number of `process()` invocations or elapsed instructions vastly exceeds what `limit`/`RECURSION_LIMIT` would suggest, and that the call either does not terminate within a reasonable bound or the `Outcome::used` weight is many multiples of the declared `limit`.
4. Assertion: either the test times out (proving unbounded looping) or `Outcome::used` weight vastly exceeds `limit` (proving weight-accounting mismatch), both of which violate the invariant that "execution must terminate deterministically" and that "used weight reflects declared prepared weight."

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

**File:** polkadot/xcm/xcm-builder/src/weight.rs (L75-123)
```rust
impl<T: Get<Weight>, C: Decode + GetDispatchInfo, M> FixedWeightBounds<T, C, M> {
	fn weight_with_limit(
		message: &mut Xcm<C>,
		instructions_left: &mut u32,
		weight_limit: Weight,
	) -> Result<Weight, InstructionError> {
		let mut total_weight: Weight = Weight::zero();
		for (index, instruction) in message.0.iter_mut().enumerate() {
			let index = index.try_into().unwrap_or(InstructionIndex::MAX);
			*instructions_left = instructions_left
				.checked_sub(1)
				.ok_or_else(|| InstructionError { index, error: XcmError::ExceedsStackLimit })?;
			let instruction_weight =
				&Self::instr_weight_with_limit(instruction, instructions_left, weight_limit)
					.map_err(|error| InstructionError { index, error })?;
			total_weight = total_weight
				.checked_add(instruction_weight)
				.ok_or(InstructionError { index, error: XcmError::Overflow })?;
			if total_weight.any_gt(weight_limit) {
				return Err(InstructionError {
					index,
					error: XcmError::WeightLimitReached(total_weight),
				});
			}
		}
		Ok(total_weight)
	}

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
```
