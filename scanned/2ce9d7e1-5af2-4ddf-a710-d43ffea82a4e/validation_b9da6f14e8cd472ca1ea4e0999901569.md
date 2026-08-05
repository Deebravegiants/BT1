### Title
DMP messages enqueued to an on-demand para during its (unprivileged) offboarding grace window are silently destroyed by `clean_dmp_after_outgoing` with no refund or error - ([File: polkadot/runtime/parachains/src/dmp.rs])

### Summary
`can_queue_downward_message`/`queue_downward_message` only validate message size, queue capacity, and that `paras::Heads` still contains an entry for the destination para; they never check whether the para has already been scheduled for offboarding via `paras_registrar::deregister`. Because `paras::Heads` remains populated until the very session boundary where `clean_dmp_after_outgoing` unconditionally deletes `InboundDownwardQueue`/`DownwardMessageQueueHeads`, any message accepted into the DMP queue during that window is guaranteed to be wiped with no processing and no signal to the sender.

### Finding Description
`Pallet::deregister` in `polkadot/runtime/common/src/paras_registrar/mod.rs` is reachable by a signed on-demand parachain owner and requires no privileged origin: `ensure_root_para_or_owner` accepts the manager account. [1](#0-0) 
`do_deregister` only calls `schedule_para_cleanup`, which schedules removal for a future session — it does not touch `paras::Heads` immediately. [2](#0-1) 

During the interval between the `deregister` extrinsic and the next session change, `paras::Heads::<T>::contains_key(para)` is still `true`, so `can_queue_downward_message` returns `Ok(())` and `queue_downward_message` happily appends the message and updates the MQC head: [3](#0-2) 
The check makes no reference to the para's scheduled lifecycle transition/offboarding status — the only gate is presence of a `Heads` entry. [4](#0-3) 

At the session boundary, `initializer_on_new_session` invokes `perform_outgoing_para_cleanup`, which calls `clean_dmp_after_outgoing` for every para in the `outgoing_paras` list (which includes `id` after `schedule_para_cleanup`). This unconditionally deletes the entire `InboundDownwardQueue` and resets `DownwardMessageQueueHeads`, with no check for whether any messages are still unprocessed and no notification/refund path: [5](#0-4) 

Since a deregistering on-demand parachain typically does not have a scheduled/guaranteed block production slot during this grace window (deregistration explicitly requires the para to already be a `Parathread`, i.e. only produces blocks when assigned via on-demand scheduling), there is no reliable mechanism for the para to drain its DMQ before the wipe. The sender of the message received `Ok(())` from `queue_downward_message` at send time — there is no later failure event, no bounce, and no asset-trap style recovery, because the message (and any XCM `Transact`/asset instructions it encodes) is deleted from storage, not executed.

### Impact Explanation
Any DMP message (including XCM `Transact` calls or messages accompanying asset transfers/teleports whose value accounting on the sending side has already been finalized) sent to a para between its (fully unprivileged, owner-triggered) `deregister` call and the next session boundary is permanently and silently destroyed. If the payload represented value already burned/withdrawn on the sending chain in anticipation of the destination processing it, that value is unrecoverably lost, with the sender having no indication the message will never be executed.

### Likelihood Explanation
The precondition — an on-demand parachain owner calling `deregister` (fully unprivileged, no governance needed) — is a normal, expected action. The window between `deregister` and the next session change is a fixed, non-zero interval (at least one full session) during which `paras::Heads` remains populated, so `can_queue_downward_message`/`queue_downward_message` will accept new DMP messages exactly as documented. Any third party (not just the para owner) can trigger `queue_downward_message` toward that para id via the normal XCM/DMP send path in that window, since there is no coordination requirement between the deregistering owner and message senders. This is fully reproducible and repeatable.

### Recommendation
Track offboarding-scheduled paras (e.g. check the paras `ActionsQueue`/an equivalent "is being offboarded" predicate) inside `can_queue_downward_message` and reject new downward messages with `QueueDownwardMessageError::Unroutable` once a para has been scheduled for cleanup, so senders receive a `SendError` rather than silent acceptance. Additionally/alternatively, require `clean_dmp_after_outgoing` to only run once `dmq_length(para) == 0`, or bounce/refund in-flight messages, before removing the queue.

### Proof of Concept
Integration test in `polkadot/runtime/parachains/src/dmp/tests.rs` style, combined with `paras_registrar`:
1. Register and onboard on-demand para `P` (through the normal register/onboard flow) so `paras::Heads::<Test>::contains_key(P)` is true.
2. As `P`'s owner (signed origin), call `Registrar::deregister(P)` — assert it succeeds (`Ok`) with unprivileged origin.
3. Before running to the next session, call `Dmp::queue_downward_message(&config, P, msg)` and assert it returns `Ok(())`, and that `Dmp::dmq_contents_do_not_call_in_consensus(P)` contains `msg`.
4. Advance the chain to the session where `initializer_on_new_session` fires `perform_outgoing_para_cleanup` for `P`.
5. Assert `Dmp::dmq_contents_do_not_call_in_consensus(P)` is empty and `DownwardMessageQueueHeads::<Test>::get(P) == Hash::default()`, proving the message was deleted rather than delivered, refunded, or bounced — with the original `queue_downward_message` call having reported `Ok(())` and no compensating event ever emitted.

### Citations

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L301-310)
```rust
		/// Deregister a Para Id, freeing all data and returning any deposit.
		///
		/// The caller must be Root, the `para` owner, or the `para` itself. The para must be an
		/// on-demand parachain.
		#[pallet::call_index(2)]
		#[pallet::weight(<T as Config>::WeightInfo::deregister())]
		pub fn deregister(origin: OriginFor<T>, id: ParaId) -> DispatchResult {
			Self::ensure_root_para_or_owner(origin, id)?;
			Self::do_deregister(id)
		}
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L659-676)
```rust
	/// Deregister a Para Id, freeing all data returning any deposit.
	fn do_deregister(id: ParaId) -> DispatchResult {
		match paras::Pallet::<T>::lifecycle(id) {
			// Para must be a parathread (on-demand parachain), or not exist at all.
			Some(ParaLifecycle::Parathread) | None => {},
			_ => return Err(Error::<T>::NotParathread.into()),
		}
		polkadot_runtime_parachains::schedule_para_cleanup::<T>(id)
			.map_err(|_| Error::<T>::CannotDeregister)?;

		if let Some(info) = Paras::<T>::take(&id) {
			<T as Config>::Currency::unreserve(&info.manager, info.deposit);
		}

		PendingSwap::<T>::remove(id);
		Self::deposit_event(Event::<T>::Deregistered { para_id: id });
		Ok(())
	}
```

**File:** polkadot/runtime/parachains/src/dmp.rs (L244-264)
```rust
	/// Called by the initializer to note that a new session has started.
	pub(crate) fn initializer_on_new_session(
		_notification: &initializer::SessionChangeNotification<BlockNumberFor<T>>,
		outgoing_paras: &[ParaId],
	) {
		Self::perform_outgoing_para_cleanup(outgoing_paras);
	}

	/// Iterate over all paras that were noted for offboarding and remove all the data
	/// associated with them.
	fn perform_outgoing_para_cleanup(outgoing: &[ParaId]) {
		for outgoing_para in outgoing {
			Self::clean_dmp_after_outgoing(outgoing_para);
		}
	}

	/// Remove all relevant storage items for an outgoing parachain.
	fn clean_dmp_after_outgoing(outgoing_para: &ParaId) {
		InboundDownwardQueue::<T>::delete_all(*outgoing_para);
		DownwardMessageQueueHeads::<T>::remove(outgoing_para);
	}
```

**File:** polkadot/runtime/parachains/src/dmp.rs (L269-326)
```rust
	pub fn can_queue_downward_message(
		config: &HostConfiguration<BlockNumberFor<T>>,
		para: &ParaId,
		msg: &DownwardMessage,
	) -> Result<(), QueueDownwardMessageError> {
		let serialized_len = msg.len() as u32;
		if serialized_len > config.max_downward_message_size {
			return Err(QueueDownwardMessageError::ExceedsMaxMessageSize);
		}

		// Hard limit on Queue size
		if Self::dmq_length(*para) > Self::dmq_max_length(config.max_downward_message_size) {
			return Err(QueueDownwardMessageError::ExceedsMaxMessageSize);
		}

		// If the head exists, we assume the parachain is legit and exists.
		if !paras::Heads::<T>::contains_key(para) {
			return Err(QueueDownwardMessageError::Unroutable);
		}

		Ok(())
	}

	/// Enqueue a downward message to a specific recipient para.
	///
	/// When encoded, the message should not exceed the `config.max_downward_message_size`.
	/// Otherwise, the message won't be sent and `Err` will be returned.
	///
	/// It is possible to send a downward message to a non-existent para. That, however, would lead
	/// to a dangling storage. If the caller cannot statically prove that the recipient exists
	/// then the caller should perform a runtime check.
	pub fn queue_downward_message(
		config: &HostConfiguration<BlockNumberFor<T>>,
		para: ParaId,
		msg: DownwardMessage,
	) -> Result<(), QueueDownwardMessageError> {
		let serialized_len = msg.len();
		Self::can_queue_downward_message(config, &para, &msg)?;

		let inbound = InboundDownwardQueue::<T>::push_back(para, msg)
			.map_err(|_| QueueDownwardMessageError::ExceedsMaxQueueSize)?;
		let q_len = InboundDownwardQueue::<T>::len(para).unwrap_or(0);

		// obtain the new link in the MQC and update the head.
		DownwardMessageQueueHeads::<T>::mutate(para, |head| {
			let new_head =
				BlakeTwo256::hash_of(&(*head, inbound.sent_at, T::Hashing::hash_of(&inbound.msg)));
			*head = new_head;
		});

		let threshold =
			Self::dmq_max_length(config.max_downward_message_size).saturating_div(THRESHOLD_FACTOR);
		if q_len > threshold as u64 {
			Self::increase_fee_factor(para, serialized_len as u128);
		}

		Ok(())
	}
```
