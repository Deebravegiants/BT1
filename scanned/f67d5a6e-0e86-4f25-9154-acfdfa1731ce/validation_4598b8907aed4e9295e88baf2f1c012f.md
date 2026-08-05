Based on my research, I found a structurally analogous pattern in the HRMP (Horizontal Relay-routed Message Passing) pallet, though with an important caveat about likelihood that I'll detail below.

### Title
Unbounded `HrmpOpenChannelRequestsList`/`HrmpCloseChannelRequestsList` fully iterated during session-change processing - (File: `polkadot/runtime/parachains/src/hrmp.rs`)

### Summary
The HRMP pallet maintains two `Vec`-backed storages, `HrmpOpenChannelRequestsList` and `HrmpCloseChannelRequestsList`, that grow every time any onboarded parachain calls `hrmp_init_open_channel` or `hrmp_close_channel`. These lists are fully iterated, unconditionally and without weight-limit early-exit, in `process_hrmp_open_channel_requests` and `clean_open_channel_requests` during session-change processing — mirroring the reported pattern of an admin-appended array being fully iterated by core logic (`GLPbackingNeeded`) until it exceeds available gas/weight.

### Finding Description
`HrmpOpenChannelRequestsList` and `HrmpCloseChannelRequestsList` are declared as plain, unbounded `Vec<HrmpChannelId>` in storage, with an explicit maintainer comment acknowledging the risk: [1](#0-0) 

Entries are appended via the `hrmp_init_open_channel` and `hrmp_close_channel` extrinsics, callable by any onboarded parachain's sovereign origin (`ensure_parachain`): [2](#0-1) [3](#0-2) 

At every session change, `process_hrmp_open_channel_requests` reads the entire list and iterates it fully with no weight-checkpointing or early exit: [4](#0-3) 

Similarly, `clean_open_channel_requests` partitions and iterates the entire list when paras offboard: [5](#0-4) 

This is structurally the same root cause as the reported `addPool`/`poolInfo` issue: an array that grows via a "privileged-ish" but not fully trusted actor, later fully traversed by core logic without a hard cap, risking exceeding the available execution budget (weight/gas) for that block/session-change.

### Impact Explanation
If either list grows large enough, `process_hrmp_open_channel_requests` or `clean_open_channel_requests` could consume excessive weight during the mandatory session-change transition (part of block execution, not a regular weight-metered extrinsic), potentially causing the block to exceed its weight budget. Since HRMP channel setup/teardown and para offboarding are relay-chain-critical operations, this could degrade or brick cross-chain messaging setup for the affected session — a high-impact scenario, analogous to "bricking core protocol functionality."

### Likelihood Explanation
Likelihood is low-to-very-low, for reasons distinct even from the original report's premise:
- Unlike `addPool` (called by a single admin key), `hrmp_init_open_channel`/`hrmp_close_channel` require the caller to be an already-onboarded parachain (`ensure_parachain` origin) — this is not an arbitrary unprivileged EOA; it requires winning/holding a parachain slot or coretime, a significant economic and governance barrier.
- Each sender is also capped by `HrmpOpenChannelRequestCount`/per-config limits (`OpenHrmpChannelLimitExceeded`), so a single para cannot unilaterally spam the list; an attack would require coordinating many distinct onboarded parachains.
- I was unable to fully verify (tool access ended) what the current relay-chain configuration's practical maximum number of onboarded paras is, or whether `process_hrmp_open_channel_requests`/`clean_open_channel_requests` weight is pre-charged as part of a bounded mandatory-class weight elsewhere in the initializer pipeline that would reject the block before this becomes exploitable. This should be verified in the initializer's `on_new_session` weight accounting before treating this as more than a low-severity, low-likelihood design note (which the maintainers already flagged in-code).

### Recommendation
- Convert `HrmpOpenChannelRequestsList` and `HrmpCloseChannelRequestsList` to `BoundedVec` with a global maximum size derived from the maximum number of paras times per-para channel limits (as the existing code comment already suggests is the fix: "could become bounded").
- Alternatively, process these lists in weight-metered batches across multiple blocks/sessions (similar to the `refund` pattern used in `polkadot/runtime/common/src/crowdloan/mod.rs`, which processes `RemoveKeysLimit` entries per call) rather than unconditionally draining the full list in one pass.

### Proof of Concept
A full runtime-level PoC would require: (1) onboarding a large number of parachains (bounded by relay-chain coretime/slot capacity), (2) having each open the maximum allowed number of HRMP channels via `hrmp_init_open_channel`, and (3) triggering a session change to force `process_hrmp_open_channel_requests` to iterate the full accumulated list, measuring whether weight consumption approaches or exceeds the mandatory-class weight budget. I could not execute or benchmark this within the current investigation; a background engineering session with access to the runtime-benchmarking tooling (`substrate/frame/benchmarking`) and the parachains-runtime test harness would be needed to produce concrete weight numbers and confirm exploitability at realistic para counts.

### Citations

**File:** polkadot/runtime/parachains/src/hrmp.rs (L383-388)
```rust
	// NOTE: could become bounded, but we don't have a global maximum for this.
	// `HRMP_MAX_INBOUND_CHANNELS_BOUND` are per parachain, while this storage tracks the
	// global state.
	#[pallet::storage]
	pub type HrmpOpenChannelRequestsList<T: Config> =
		StorageValue<_, Vec<HrmpChannelId>, ValueQuery>;
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L515-537)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(<T as Config>::WeightInfo::hrmp_init_open_channel())]
		pub fn hrmp_init_open_channel(
			origin: OriginFor<T>,
			recipient: ParaId,
			proposed_max_capacity: u32,
			proposed_max_message_size: u32,
		) -> DispatchResult {
			let origin = ensure_parachain(<T as Config>::RuntimeOrigin::from(origin))?;
			Self::init_open_channel(
				origin,
				recipient,
				proposed_max_capacity,
				proposed_max_message_size,
			)?;
			Self::deposit_event(Event::OpenChannelRequested {
				sender: origin,
				recipient,
				proposed_max_capacity,
				proposed_max_message_size,
			});
			Ok(())
		}
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L551-565)
```rust
		/// Initiate unilateral closing of a channel. The origin must be either the sender or the
		/// recipient in the channel being closed.
		///
		/// The closure can only happen on a session change.
		#[pallet::call_index(2)]
		#[pallet::weight(<T as Config>::WeightInfo::hrmp_close_channel())]
		pub fn hrmp_close_channel(
			origin: OriginFor<T>,
			channel_id: HrmpChannelId,
		) -> DispatchResult {
			let origin = ensure_parachain(<T as Config>::RuntimeOrigin::from(origin))?;
			Self::close_channel(origin, channel_id.clone())?;
			Self::deposit_event(Event::ChannelClosed { by_parachain: origin, channel_id });
			Ok(())
		}
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L977-1031)
```rust
	// Go over the HRMP open channel requests and remove all in which offboarding paras participate.
	//
	// This will also perform the refunds for the counterparty if it doesn't offboard.
	pub(crate) fn clean_open_channel_requests(
		config: &HostConfiguration<BlockNumberFor<T>>,
		outgoing: &[ParaId],
	) -> Weight {
		// First collect all the channel ids of the open requests in which there is at least one
		// party presents in the outgoing list.
		//
		// Both the open channel request list and outgoing list are expected to be small enough.
		// In the most common case there will be only single outgoing para.
		let open_channel_reqs = HrmpOpenChannelRequestsList::<T>::get();
		let (go, stay): (Vec<HrmpChannelId>, Vec<HrmpChannelId>) = open_channel_reqs
			.into_iter()
			.partition(|req_id| outgoing.iter().any(|id| req_id.is_participant(*id)));
		HrmpOpenChannelRequestsList::<T>::put(stay);

		// Then iterate over all open requests to be removed, pull them out of the set and perform
		// the refunds if applicable.
		for req_id in go {
			let req_data = match HrmpOpenChannelRequests::<T>::take(&req_id) {
				Some(req_data) => req_data,
				None => {
					// Can't normally happen but no need to panic.
					continue;
				},
			};

			// Return the deposit of the sender, but only if it is not the para being offboarded.
			if !outgoing.contains(&req_id.sender) {
				T::Currency::unreserve(
					&req_id.sender.into_account_truncating(),
					req_data.sender_deposit.unique_saturated_into(),
				);
			}

			// If the request was confirmed, then it means it was confirmed in the finished session.
			// Therefore, the config's hrmp_recipient_deposit represents the actual value of the
			// deposit.
			//
			// We still want to refund the deposit only if the para is not being offboarded.
			if req_data.confirmed {
				if !outgoing.contains(&req_id.recipient) {
					T::Currency::unreserve(
						&req_id.recipient.into_account_truncating(),
						config.hrmp_recipient_deposit.unique_saturated_into(),
					);
				}
				Self::decrease_accepted_channel_request_count(req_id.recipient);
			}
		}

		<T as Config>::WeightInfo::clean_open_channel_requests(outgoing.len() as u32)
	}
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1057-1121)
```rust
	fn process_hrmp_open_channel_requests(config: &HostConfiguration<BlockNumberFor<T>>) {
		let mut open_req_channels = HrmpOpenChannelRequestsList::<T>::get();
		if open_req_channels.is_empty() {
			return;
		}

		// iterate the vector starting from the end making our way to the beginning. This way we
		// can leverage `swap_remove` to efficiently remove an item during iteration.
		let mut idx = open_req_channels.len();
		loop {
			// bail if we've iterated over all items.
			if idx == 0 {
				break;
			}

			idx -= 1;
			let channel_id = open_req_channels[idx].clone();
			let request = HrmpOpenChannelRequests::<T>::get(&channel_id).expect(
				"can't be `None` due to the invariant that the list contains the same items as the set; qed",
			);

			let system_channel = channel_id.sender.is_system() || channel_id.recipient.is_system();
			let sender_deposit = request.sender_deposit;
			let recipient_deposit = if system_channel { 0 } else { config.hrmp_recipient_deposit };

			if request.confirmed {
				if paras::Pallet::<T>::is_valid_para(channel_id.sender) &&
					paras::Pallet::<T>::is_valid_para(channel_id.recipient)
				{
					HrmpChannels::<T>::insert(
						&channel_id,
						HrmpChannel {
							sender_deposit,
							recipient_deposit,
							max_capacity: request.max_capacity,
							max_total_size: request.max_total_size,
							max_message_size: request.max_message_size,
							msg_count: 0,
							total_size: 0,
							mqc_head: None,
						},
					);

					HrmpIngressChannelsIndex::<T>::mutate(&channel_id.recipient, |v| {
						if let Err(i) = v.binary_search(&channel_id.sender) {
							v.insert(i, channel_id.sender);
						}
					});
					HrmpEgressChannelsIndex::<T>::mutate(&channel_id.sender, |v| {
						if let Err(i) = v.binary_search(&channel_id.recipient) {
							v.insert(i, channel_id.recipient);
						}
					});
				}

				Self::decrease_open_channel_request_count(channel_id.sender);
				Self::decrease_accepted_channel_request_count(channel_id.recipient);

				let _ = open_req_channels.swap_remove(idx);
				HrmpOpenChannelRequests::<T>::remove(&channel_id);
			}
		}

		HrmpOpenChannelRequestsList::<T>::put(open_req_channels);
	}
```
