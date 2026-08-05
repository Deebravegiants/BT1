### No Vulnerability found for this question.

**Analysis:** The premise that `check_upward_messages` and `receive_upward_messages` could parse UMP signals differently is incorrect — both functions call the exact same `skip_ump_signals` utility on the exact same message slice: [1](#0-0) [2](#0-1) 

`skip_ump_signals` is a simple `take_while` that stops at the first element structurally equal to `UMP_SEPARATOR` (an empty `Vec<u8>`), regardless of what follows: [3](#0-2) . Because both `check_upward_messages` (the acceptance check) and `receive_upward_messages` (the enqueue path) apply this identical, deterministic filter to the identical `commitments.upward_messages` array from the same candidate, whatever gets excluded from the count in `check_upward_messages` is exactly what gets excluded from enqueuing in `receive_upward_messages` — there is no divergence between the two parses. The `max_upward_message_num_per_candidate` bound checked in `check_upward_messages` is enforced against the same filtered vector that later gets bounded and enqueued via `receive_bounded_upward_messages`/`T::MessageQueue::enqueue_messages` [4](#0-3) .

An attacker cannot "forge" a separator with attacker payload bytes to fool one function but not the other, since `UMP_SEPARATOR` match requires literal byte-equality to an empty vector — not a structural/type match on `UMPSignal`-like content. Any non-empty payload, however "signal-like," is never treated as a separator by either function, and thus is fully counted by both. This behavior is directly exercised by the existing `enqueue_ump_signals` test, which asserts that only the genuine messages preceding the separator are ever queued and processed, matching `expected_messages` exactly, with the trailing `UMP_SEPARATOR`/`UMPSignal` bytes excluded from both the acceptance count and the actual `MessageQueue` enqueue: [5](#0-4) .

Separately, malformed or duplicated `UMPSignal` content after the separator is validated by `CandidateCommitments::ump_signals`/`CommittedCandidateReceiptV2::parse_ump_signals` during backing/validity checks (`DuplicateUMPSignal`, `TooManyUMPSignals`, `UmpSignalDecode` errors) [6](#0-5) , which is a distinct code path from `inclusion::check_upward_messages`/`receive_upward_messages`. A malformed signal tail there causes the candidate to be rejected outright rather than enabling any smuggling of extra enqueued messages.

Since both the counting and enqueuing logic are driven by the same deterministic filter over the same input, there is no way for a candidate to pass `check_upward_messages`'s count/size limits while getting more genuine messages enqueued via `receive_upward_messages` than the filtered count that was checked.

### Citations

**File:** polkadot/runtime/parachains/src/inclusion/mod.rs (L930-932)
```rust
	) -> Result<(), UmpAcceptanceCheckErr> {
		// Filter any pending UMP signals and the separator.
		let upward_messages = skip_ump_signals(upward_messages.iter()).collect::<Vec<_>>();
```

**File:** polkadot/runtime/parachains/src/inclusion/mod.rs (L985-996)
```rust
	pub(crate) fn receive_upward_messages(para: ParaId, upward_messages: &[Vec<u8>]) {
		let bounded = skip_ump_signals(upward_messages.iter())
			.filter_map(|d| {
				BoundedSlice::try_from(&d[..])
					.inspect_err(|_| {
						defensive!("Accepted candidate contains too long msg, len=", d.len());
					})
					.ok()
			})
			.collect();
		Self::receive_bounded_upward_messages(para, bounded)
	}
```

**File:** polkadot/runtime/parachains/src/inclusion/mod.rs (L998-1013)
```rust
	/// Enqueues storage-bounded `upward_messages` from a `para`'s accepted candidate block.
	pub(crate) fn receive_bounded_upward_messages(
		para: ParaId,
		messages: Vec<BoundedSlice<'_, u8, MaxUmpMessageLenOf<T>>>,
	) {
		let count = messages.len() as u32;
		if count == 0 {
			return;
		}

		T::MessageQueue::enqueue_messages(
			messages.into_iter(),
			AggregateMessageOrigin::Ump(UmpQueueId::Para(para)),
		);
		Self::deposit_event(Event::UpwardMessagesReceived { from: para, count });
	}
```

**File:** polkadot/primitives/src/v9/mod.rs (L2785-2793)
```rust
/// Separator between `XCM` and `UMPSignal`.
pub const UMP_SEPARATOR: Vec<u8> = vec![];

/// Utility function for skipping the ump signals.
pub fn skip_ump_signals<'a>(
	upward_messages: impl Iterator<Item = &'a Vec<u8>>,
) -> impl Iterator<Item = &'a Vec<u8>> {
	upward_messages.take_while(|message| *message != &UMP_SEPARATOR)
}
```

**File:** polkadot/primitives/src/v9/mod.rs (L2795-2823)
```rust
impl CandidateCommitments {
	/// Returns the ump signals of this candidate, if any, or an error if they violate the expected
	/// format.
	pub fn ump_signals(&self) -> Result<CandidateUMPSignals, CommittedCandidateReceiptError> {
		let mut res = CandidateUMPSignals::default();

		let mut signals_iter =
			self.upward_messages.iter().skip_while(|message| *message != &UMP_SEPARATOR);

		if signals_iter.next().is_none() {
			// No UMP separator
			return Ok(res);
		}

		// Process first signal
		let Some(first_signal) = signals_iter.next() else { return Ok(res) };
		res.try_decode_signal(&mut first_signal.as_slice())?;

		// Process second signal
		let Some(second_signal) = signals_iter.next() else { return Ok(res) };
		res.try_decode_signal(&mut second_signal.as_slice())?;

		// At most two signals are allowed
		if signals_iter.next().is_some() {
			return Err(CommittedCandidateReceiptError::TooManyUMPSignals);
		}

		Ok(res)
	}
```

**File:** polkadot/runtime/parachains/src/ump_tests.rs (L649-682)
```rust
#[test]
fn enqueue_ump_signals() {
	let para = 100.into();

	new_test_ext(GenesisConfigBuilder::default().build()).execute_with(|| {
		register_parachain(para);
		run_to_block(5, vec![4, 5]);

		let config = configuration::ActiveConfig::<Test>::get();
		let mut messages = (0..config.max_upward_message_num_per_candidate)
			.into_iter()
			.map(|_| "msg".encode())
			.collect::<Vec<_>>();
		let expected_messages = messages.iter().cloned().map(|msg| (para, msg)).collect::<Vec<_>>();

		// `UMPSignals` and separator do not count as XCM messages. The below check must pass.
		messages.append(&mut vec![
			UMP_SEPARATOR,
			UMPSignal::SelectCore(CoreSelector(0), ClaimQueueOffset(0)).encode(),
		]);

		ParaInclusion::check_upward_messages(
			&configuration::ActiveConfig::<Test>::get(),
			para,
			&messages,
		)
		.unwrap();

		// We expect that all messages except UMP signal and separator are processed
		ParaInclusion::receive_upward_messages(para, &messages);
		MessageQueue::service_queues(Weight::max_value());
		assert_eq!(Processed::take(), expected_messages);
	});
}
```
