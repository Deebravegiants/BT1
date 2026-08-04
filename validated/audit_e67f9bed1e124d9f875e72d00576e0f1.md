### Title
Overweight messages that structurally exceed the XCM recursion depth limit can never be resolved by `execute_overweight` (`Error::TemporarilyUnprocessable` forever) - ([File: substrate/frame/message-queue/src/lib.rs])

### Summary
An XCM message whose nested-instruction depth exceeds `xcm_executor::RECURSION_LIMIT` (10) can be enqueued, weighed successfully during `prepare()`, and marked `Overweight` purely due to insufficient budget - but when later replayed via `MessageQueue::execute_overweight`, `XcmExecutor::execute()` will deterministically hit `XcmError::ExceedsStackLimit` regardless of the `weight_limit` supplied, so `do_execute_overweight_inner` always returns `Error::TemporarilyUnprocessable`, and the message can never transition to `Processed`. This matches the documented, non-mocked behavior shown by `polkadot/xcm/xcm-builder/src/process_xcm_message.rs:118-121` and `polkadot/xcm/xcm-executor/src/lib.rs:855-877`.

### Finding Description
`MessageExecutionStatus::StackLimitReached` and `Unprocessable{permanent:false}` are both mapped in `do_execute_overweight_inner` (`substrate/frame/message-queue/src/lib.rs:1112-1115`) to `Err(Error::TemporarilyUnprocessable)`, never to `AlreadyProcessed` or a permanent error. `XcmExecutor::process()` (`polkadot/xcm/xcm-executor/src/lib.rs:855-877`) enforces a fixed nesting-depth counter (`RECURSION_LIMIT = 10`), which is reset via `recursion_count::using_once` on every fresh top-level call, whether that call originates from normal block servicing (`service_page_item`) or from the `execute_overweight` extrinsic. This means the recursion check is a deterministic function of the message payload's nesting structure alone - independent of `weight_limit`, of the calling context, or of how many times it is retried. If an attacker crafts a message with nesting depth > 10 (e.g. `SetAppendix`/`Transact` chains, matching the pattern verified by `transact_recursion_limit_works` in `polkadot/xcm/xcm-executor/integration-tests/src/lib.rs:73-167`) it will always produce `XcmError::ExceedsStackLimit` → `ProcessMessageError::StackLimitReached` → `MessageExecutionStatus::StackLimitReached`. Separately, the weigher used during `prepare()` enforces a *total instruction count* limit (`instructions_left`, config `M`), which is a different mechanism from the nesting-depth counter; a message can pass weighing (and thus be classified `Overweight` for budget reasons) while still structurally exceeding the nesting-depth limit at actual execution time. Combined, this can produce exactly the scenario in the question: `OverweightEnqueued` → every subsequent `execute_overweight` call → `Err(Error::TemporarilyUnprocessable)`, forever, because the outcome never depends on the supplied weight.

However, the scoped impact claim - that this "permanently occupies page storage and message_count in `BookStateFor`... unresolvable automatically or manually" - is not fully accurate. `do_reap_page`/`do_reap_page_inner` (`substrate/frame/message-queue/src/lib.rs:1150-1213`) provides a manual, permissionless (`ensure_signed` only) cleanup path via the `cullable()` staleness formula, which allows a stale overweight page to be dropped (and `message_count`/`size` decremented) once `page_index < book_state.begin` and the page falls behind the `MaxStale`-derived watermark - regardless of whether the message inside was ever processed. This path does require `book_state.begin` to have advanced past the stuck page's index, i.e. the same origin must continue to receive and successfully service further pages after the stuck one. If the origin's queue never advances past the stuck page (e.g. it is the origin's last/only page, `begin == page_index`), `reap_page` is blocked by the unconditional check `ensure!(page_index < book_state.begin, Error::<T>::NotReapable)` at `substrate/frame/message-queue/src/lib.rs:1155`, and the page truly remains stuck until the origin sends more traffic.

### Impact Explanation
For the affected origin's queue, one specific message can never reach `Processed` and will keep returning `TemporarilyUnprocessable` on every `execute_overweight` retry, regardless of the caller-supplied `weight_limit`. The `OverweightEnqueued` event/state persists, and the message's contribution to `BookStateFor::size`/`message_count` for that origin is not released until either (a) the origin queue advances enough pages for `reap_page`'s staleness-based culling to apply, or (b) the message payload itself is otherwise removed. This is a "stuck message" issue rather than an unbounded, always-permanent DoS of the whole pallet: it does not lock other origins' queues, does not grow indefinitely by itself, and does have a documented (if origin-traffic-dependent) manual escape hatch (`reap_page`/cullable). It is a genuine functional/availability defect for the specific stuck message on a low-traffic or dormant origin, but not the "no recovery path exists at all" scenario the question strictly claims.

### Likelihood Explanation
Feasibility requires: (1) the attacker can get a message enqueued whose nested-instruction structure exceeds `RECURSION_LIMIT=10` while still weighing successfully under `prepare()`'s separate instruction-count limit, and (2) the message must be classified `Overweight` (not immediately discarded, since a message that already hits `StackLimitReached` at first top-level service is discarded per `process_discards_stack_ov_message`, not queued as overweight). Constructing such a payload (deep `SetAppendix`/`Transact` nesting with light weight per level but insufficient available budget at initial service) is plausible for an XCM message reachable via `pallet_xcm::execute`/`send`, or via routed HRMP/UMP messages carrying attacker-influenced instructions (e.g. custom XCM on reserve transfers). Repeated failure on retry is fully deterministic since the recursion counter depends only on message structure.

### Recommendation
- Treat `StackLimitReached` returned from a manual `execute_overweight` call as a permanent condition (drop/mark permanently unprocessable and emit an event) rather than always mapping it to `TemporarilyUnprocessable`, since `execute_overweight` is by definition a top-level call with the greatest available "logical" recursion budget - there is no plausible future retry that will succeed.
- Alternatively, decouple the weigher's instruction-count limit from the executor's nesting-depth limit so that a message which will structurally exceed `RECURSION_LIMIT` at execution time is rejected/discarded during weighing (classified permanently unprocessable) instead of being allowed into the `Overweight` queue.
- Ensure `reap_page`'s cullability does not strictly require `page_index < book_state.begin`, or provide an explicit permissionless path to purge overweight pages whose message consistently fails with `StackLimitReached`, independent of whether the origin ever sends further traffic.

### Proof of Concept
Rust integration test plan (using `polkadot/xcm/xcm-executor/integration-tests` harness, extending `transact_recursion_limit_works`):
1. Build a message that (a) passes `Config::Weigher::weight()` (finite computed weight, e.g. nested `SetAppendix(Xcm(vec![ClearOrigin]))` chained 11+ levels deep with total instruction count kept below the weigher's `MaxInstructions`), and (b) is submitted through `pallet_xcm`/message-queue with a `ServiceWeight` too small to cover the computed weight on first service, so it is enqueued as `OverweightEnqueued` (assert the event and `assert_pages` show one stale page).
2. Call `MessageQueue::execute_overweight(origin, page_index, index, weight_limit)` with a very large `weight_limit` (e.g. `Weight::MAX`).
3. Assert the call returns `Err(Error::TemporarilyUnprocessable)` and that the `ProcessingFailed`/`ExceedsStackLimit` event is emitted.
4. Repeat step 2 several times with varying `weight_limit` values and assert the result is always `Err(Error::TemporarilyUnprocessable)`, that `BookStateFor` `message_count`/`size` never decrease, and that the page is never removed (`Pages::<T>::get` still returns the page with the message unprocessed).
5. Additionally assert that `reap_page` returns `Err(Error::NotReapable)` as long as `book_state.begin == page_index` (no further pages exist), demonstrating that in this configuration neither `execute_overweight` nor `reap_page` resolves the stuck message - while noting that once `book_state.begin` advances past `page_index` (by servicing additional messages/pages for the same origin), `reap_page`'s `cullable()` path does eventually succeed, bounding rather than eliminating the issue. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** substrate/frame/message-queue/src/lib.rs (L1100-1140)
```rust
		use MessageExecutionStatus::*;
		let mut weight_counter = WeightMeter::with_limit(weight_limit);
		match Self::process_message_payload(
			origin.clone(),
			page_index,
			index,
			payload,
			&mut weight_counter,
			Weight::MAX,
			// ^^^ We never recognise it as permanently overweight, since that would result in an
			// additional overweight event being deposited.
		) {
			Overweight | InsufficientWeight => Err(Error::<T>::InsufficientWeight),
			StackLimitReached | Unprocessable { permanent: false } => {
				Err(Error::<T>::TemporarilyUnprocessable)
			},
			Unprocessable { permanent: true } | Processed => {
				page.note_processed_at_pos(pos);
				book_state.message_count.saturating_dec();
				book_state.size.saturating_reduce(payload_len);
				let page_weight = if page.remaining.is_zero() {
					debug_assert!(
						page.remaining_size.is_zero(),
						"no messages remaining; no space taken; qed"
					);
					Pages::<T>::remove(&origin, page_index);
					debug_assert!(book_state.count >= 1, "page exists, so book must have pages");
					book_state.count.saturating_dec();
					T::WeightInfo::execute_overweight_page_removed()
				// no need to consider .first or ready ring since processing an overweight page
				// would not alter that state.
				} else {
					Pages::<T>::insert(&origin, page_index, page);
					T::WeightInfo::execute_overweight_page_updated()
				};
				BookStateFor::<T>::insert(&origin, &book_state);
				T::QueueChangeHandler::on_queue_changed(origin, book_state.into());
				Ok(weight_counter.consumed().saturating_add(page_weight))
			},
		}
	}
```

**File:** substrate/frame/message-queue/src/lib.rs (L1150-1213)
```rust
	/// Same as `do_reap_page` but must be called while holding the `service_mutex`.
	fn do_reap_page_inner(origin: &MessageOriginOf<T>, page_index: PageIndex) -> DispatchResult {
		let mut book_state = BookStateFor::<T>::get(origin);
		// definitely not reapable if the page's index is no less than the `begin`ning of ready
		// pages.
		ensure!(page_index < book_state.begin, Error::<T>::NotReapable);

		let page = Pages::<T>::get(origin, page_index).ok_or(Error::<T>::NoPage)?;

		// definitely reapable if the page has no messages in it.
		let reapable = page.remaining.is_zero();

		// also reapable if the page index has dropped below our watermark.
		let cullable = || {
			let total_pages = book_state.count;
			let ready_pages = book_state.end.saturating_sub(book_state.begin).min(total_pages);

			// The number of stale pages - i.e. pages which contain unprocessed overweight messages.
			// We would prefer to keep these around but will restrict how far into history they can
			// extend if we notice that there's too many of them.
			//
			// We don't know *where* in history these pages are so we use a dynamic formula which
			// reduces the historical time horizon as the stale pages pile up and increases it as
			// they reduce.
			let stale_pages = total_pages - ready_pages;

			// The maximum number of stale pages (i.e. of overweight messages) allowed before
			// culling can happen at all. Once there are more stale pages than this, then historical
			// pages may be dropped, even if they contain unprocessed overweight messages.
			let max_stale = T::MaxStale::get();

			// The amount beyond the maximum which are being used. If it's not beyond the maximum
			// then we exit now since no culling is needed.
			let overflow = match stale_pages.checked_sub(max_stale + 1) {
				Some(x) => x + 1,
				None => return false,
			};

			// The special formula which tells us how deep into index-history we will pages. As
			// the overflow is greater (and thus the need to drop items from storage is more urgent)
			// this is reduced, allowing a greater range of pages to be culled.
			// With a minimum `overflow` (`1`), this returns `max_stale ** 2`, indicating we only
			// cull beyond that number of indices deep into history.
			// At this overflow increases, our depth reduces down to a limit of `max_stale`. We
			// never want to reduce below this since this will certainly allow enough pages to be
			// culled in order to bring `overflow` back to zero.
			let backlog = (max_stale * max_stale / overflow).max(max_stale);

			let watermark = book_state.begin.saturating_sub(backlog);
			page_index < watermark
		};
		ensure!(reapable || cullable(), Error::<T>::NotReapable);

		Pages::<T>::remove(origin, page_index);
		debug_assert!(book_state.count > 0, "reaping a page implies there are pages");
		book_state.count.saturating_dec();
		book_state.message_count.saturating_reduce(page.remaining.into() as u64);
		book_state.size.saturating_reduce(page.remaining_size.into() as u64);
		BookStateFor::<T>::insert(origin, &book_state);
		T::QueueChangeHandler::on_queue_changed(origin.clone(), book_state.into());
		Self::deposit_event(Event::PageReaped { origin: origin.clone(), index: page_index });

		Ok(())
	}
```

**File:** polkadot/xcm/xcm-builder/src/process_xcm_message.rs (L71-128)
```rust
		let pre = XcmExecutor::prepare(message, Weight::MAX).map_err(|_| {
			tracing::trace!(
				target: LOG_TARGET,
				"Failed to prepare message.",
			);

			ProcessMessageError::Unsupported
		})?;
		// The worst-case weight:
		let required = pre.weight_of();
		if !meter.can_consume(required) {
			tracing::trace!(
				target: LOG_TARGET,
				"Xcm required {required} more than remaining {}",
				meter.remaining(),
			);

			return Err(ProcessMessageError::Overweight(required));
		}

		let (consumed, result) = match XcmExecutor::execute(origin.into(), pre, id, Weight::zero())
		{
			Outcome::Complete { used } => {
				tracing::trace!(
					target: LOG_TARGET,
					"XCM message execution complete, used weight: {used}",
				);
				(used, Ok(true))
			},
			Outcome::Incomplete { used, error: InstructionError { index, error } } => {
				tracing::trace!(
					target: LOG_TARGET,
					?error,
					?index,
					?used,
					"XCM message execution incomplete",
				);
				(used, Ok(false))
			},
			// In the error-case we assume the worst case and consume all possible weight.
			Outcome::Error(InstructionError { error, index }) => {
				tracing::trace!(
					target: LOG_TARGET,
					?error,
					?index,
					"XCM message execution error",
				);
				let error = match error {
					xcm::latest::Error::ExceedsStackLimit => ProcessMessageError::StackLimitReached,
					_ => ProcessMessageError::Unsupported,
				};

				(required, Err(error))
			},
		};
		meter.consume(consumed);
		result
	}
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L66-74)
```rust
/// The maximum recursion depth allowed when executing nested XCM instructions.
///
/// Exceeding this limit results in `XcmError::ExceedsStackLimit` or
/// `ProcessMessageError::StackLimitReached`.
///
/// Also used in the `DenyRecursively` barrier.
pub const RECURSION_LIMIT: u8 = 10;

environmental::environmental!(recursion_count: u8);
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L843-902)
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
					if let Err(error) = inst_res {
						tracing::debug!(
							target: "xcm::process",
							?error, "XCM execution failed at instruction index={i}"
						);
						Config::XcmEventEmitter::emit_process_failure_event(
							self.original_origin.clone(),
							error,
							self.context.topic_or_message_id(),
						);
						*r = Err(ExecutorError {
							index: i as u32,
							xcm_error: error,
							weight: Weight::zero(),
						});
					}
				},
				Err(ref mut error) => {
					if let Ok(x) = Config::Weigher::instr_weight(&mut instr) {
						error.weight.saturating_accrue(x)
					}
				},
			}
		}
		result
```

**File:** polkadot/xcm/xcm-executor/integration-tests/src/lib.rs (L73-167)
```rust
#[test]
fn transact_recursion_limit_works() {
	sp_tracing::try_init_simple();
	let client = TestClientBuilder::new().build();

	let base_xcm = |call: polkadot_test_runtime::RuntimeCall| {
		Xcm(vec![
			WithdrawAsset((Here, 1_000).into()),
			BuyExecution { fees: (Here, 1).into(), weight_limit: Unlimited },
			Transact {
				origin_kind: OriginKind::Native,
				call: call.encode().into(),
				fallback_max_weight: None,
			},
		])
	};
	let mut call: Option<polkadot_test_runtime::RuntimeCall> = None;
	// set up transacts with recursive depth of 11
	for depth in (1..12).rev() {
		let mut msg;
		match depth {
			// this one should fail with `XcmError::ExceedsStackLimit`
			11 => {
				msg = Xcm(vec![ClearOrigin]);
			},
			// this one checks that the inner one (depth 11) fails as expected,
			// itself should not fail => should have outcome == Complete
			10 => {
				let inner_call = call.take().unwrap();
				let expected_transact_status =
					sp_runtime::DispatchError::Module(sp_runtime::ModuleError {
						index: 27,
						error: [28, 0, 40, 0], // ExceedsStackLimit
						message: Some("LocalExecutionIncompleteWithError"),
					})
					.encode()
					.into();
				msg = base_xcm(inner_call);
				msg.inner_mut().push(ExpectTransactStatus(expected_transact_status));
			},
			// these are the outer 9 calls that expect `ExpectTransactStatus(Success)`
			d if d >= 1 && d <= 9 => {
				let inner_call = call.take().unwrap();
				msg = base_xcm(inner_call);
				msg.inner_mut().push(ExpectTransactStatus(MaybeErrorCode::Success));
			},
			_ => unreachable!(),
		}
		let max_weight =
			<XcmConfig as xcm_executor::Config>::Weigher::weight(&mut msg, Weight::MAX).unwrap();
		call = Some(polkadot_test_runtime::RuntimeCall::Xcm(pallet_xcm::Call::execute {
			message: Box::new(VersionedXcm::from(msg.clone())),
			max_weight,
		}));
	}

	let mut block_builder = client.init_polkadot_block_builder();

	let execute = construct_extrinsic(&client, call.unwrap(), sp_keyring::Sr25519Keyring::Alice, 0);

	block_builder.push_polkadot_extrinsic(execute).expect("pushes extrinsic");

	let block = block_builder.build().expect("Finalizes the block").block;
	let block_hash = block.hash();

	futures::executor::block_on(client.import(sp_consensus::BlockOrigin::Own, block))
		.expect("imports the block");

	client.state_at(block_hash).expect("state should exist").inspect_state(|| {
		let events = polkadot_test_runtime::System::events();
		// verify 10 pallet_xcm calls were successful
		assert_eq!(
			polkadot_test_runtime::System::events()
				.iter()
				.filter(|r| matches!(
					r.event,
					polkadot_test_runtime::RuntimeEvent::Xcm(pallet_xcm::Event::Attempted {
						outcome: Outcome::Complete { .. }
					}),
				))
				.count(),
			10
		);
		// verify transaction fees have been paid
		assert!(events.iter().any(|r| matches!(
			&r.event,
			polkadot_test_runtime::RuntimeEvent::TransactionPayment(
				pallet_transaction_payment::Event::TransactionFeePaid {
					who: payer,
					..
				}
			) if *payer == sp_keyring::Sr25519Keyring::Alice.into(),
		)));
	});
}
```

**File:** substrate/frame/message-queue/src/tests.rs (L1899-1991)
```rust
/// A message that reports `StackLimitReached` will not be put into the overweight queue when
/// executed from the top level.
#[test]
fn process_discards_stack_ov_message() {
	use MessageOrigin::*;
	build_and_execute::<Test>(|| {
		MessageQueue::enqueue_message(msg("stacklimitreached"), Here);

		MessageQueue::service_queues(10.into_weight());

		assert_last_event::<Test>(
			Event::ProcessingFailed {
				id: blake2_256(b"stacklimitreached").into(),
				origin: MessageOrigin::Here,
				error: ProcessMessageError::StackLimitReached,
			}
			.into(),
		);

		assert!(MessagesProcessed::take().is_empty());
		// Message is gone and not overweight:
		assert_pages(&[]);
	});
}

/// A message that reports `StackLimitReached` will stay in the overweight queue when it is executed
/// by `execute_overweight`.
#[test]
fn execute_overweight_keeps_stack_ov_message() {
	use MessageOrigin::*;
	build_and_execute::<Test>(|| {
		// We need to create a mocked message that first reports insufficient weight, and then
		// `StackLimitReached`:
		IgnoreStackOvError::set(true);
		MessageQueue::enqueue_message(msg("weight=200 stacklimitreached"), Here);
		MessageQueue::service_queues(0.into_weight());

		assert_last_event::<Test>(
			Event::OverweightEnqueued {
				id: blake2_256(b"weight=200 stacklimitreached"),
				origin: MessageOrigin::Here,
				message_index: 0,
				page_index: 0,
			}
			.into(),
		);
		// Does not count as 'processed':
		assert!(MessagesProcessed::take().is_empty());
		assert_pages(&[0]);

		// Now let it return `StackLimitReached`. Note that this case would normally not happen,
		// since we assume that the top-level execution is the one with the most remaining stack
		// depth.
		IgnoreStackOvError::set(false);
		// Ensure that trying to execute the message does not change any state (besides events).
		System::reset_events();
		let storage_noop = StorageNoopGuard::new();
		assert_eq!(
			<MessageQueue as ServiceQueues>::execute_overweight(3.into_weight(), (Here, 0, 0)),
			Err(ExecuteOverweightError::Other)
		);
		assert_last_event::<Test>(
			Event::ProcessingFailed {
				id: blake2_256(b"weight=200 stacklimitreached").into(),
				origin: MessageOrigin::Here,
				error: ProcessMessageError::StackLimitReached,
			}
			.into(),
		);
		System::reset_events();
		drop(storage_noop);

		// Now let's process it normally:
		IgnoreStackOvError::set(true);
		assert_eq!(
			<MessageQueue as ServiceQueues>::execute_overweight(200.into_weight(), (Here, 0, 0))
				.unwrap(),
			200.into_weight()
		);

		assert_last_event::<Test>(
			Event::Processed {
				id: blake2_256(b"weight=200 stacklimitreached").into(),
				origin: MessageOrigin::Here,
				weight_used: 200.into_weight(),
				success: true,
			}
			.into(),
		);
		assert_pages(&[]);
		System::reset_events();
	});
}
```
