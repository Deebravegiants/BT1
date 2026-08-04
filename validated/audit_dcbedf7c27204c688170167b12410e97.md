### Title
`force_clean_hrmp` weight benchmark ignores actual `HrmpChannelContents` size, undercharging session-change cleanup for full channels - ([File: polkadot/runtime/parachains/src/hrmp.rs])

### Summary
`Pallet::close_hrmp_channel` (invoked from `clean_hrmp_after_outgoing` during `initializer_on_new_session`) unconditionally removes the `HrmpChannelContents` entry for every channel of an offboarding para, but the `force_clean_hrmp` benchmark that produces `WeightInfo::force_clean_hrmp(i, e)` never populates `HrmpChannelContents` with any queued messages when it measures the cost. The resulting weight formula therefore has no per-channel term that scales with the amount of unprocessed message data sitting in a channel, so a para that fills its channels to the configured maximum before offboarding causes `perform_outgoing_para_cleanup` to consume materially more PoV/computation than what was pre-charged.

### Finding Description
`close_hrmp_channel` at [1](#0-0)  takes the `HrmpChannels` entry and then calls `HrmpChannelContents::<T>::remove(channel_id)` unconditionally, regardless of how much data is stored under that key. This is reached from `clean_hrmp_after_outgoing`, which is called once per outgoing para from `perform_outgoing_para_cleanup` at [2](#0-1) , which in turn charges `WeightInfo::force_clean_hrmp(ingress_count, egress_count)` per outgoing para at [3](#0-2) . This whole path runs unconditionally as part of `initializer_on_new_session`, which is a mandatory (non-skippable) hook executed at every session boundary [4](#0-3) .

The `force_clean_hrmp` benchmark that generates this weight only calls `establish_para_connection` for each ingress/egress channel — it never inserts any `InboundHrmpMessage`s into the channel, so `HrmpChannelContents` is empty (0-length `Vec`) for every measured channel [5](#0-4) . The generated weight function therefore has only a fixed per-channel linear term (e.g. `4_222_698` ref-time and `2575` proof-size bytes per channel in the Rococo weights) that reflects removing an *empty* `HrmpChannelContents` entry [6](#0-5) . It contains no term proportional to `hrmp_channel_max_total_size` / `hrmp_channel_max_message_size`, i.e. no accounting for how large the actual stored `Vec<InboundHrmpMessage>` can legitimately grow (bounded per channel by the runtime's `hrmp_channel_max_total_size`/`hrmp_channel_max_capacity` configuration, which an unprivileged para can reach entirely through normal, permitted HRMP usage).

Because `initializer_on_new_session` runs as a mandatory dispatchable/hook, its actual execution is not gated by "does this fit in remaining block weight" the way normal transactions are — it always runs. If actual weight (particularly proof size, since removing a large trie leaf value requires including that value in the state proof) substantially exceeds the pre-computed `force_clean_hrmp` estimate, the block's total recorded weight can end up higher than anticipated by block-authoring/import weight accounting.

### Impact Explanation
An attacker-controlled para can, without any special privilege:
1. Open ingress and egress HRMP channels up to the network's configured `hrmp_max_parachain_inbound_channels` / `hrmp_max_parachain_outbound_channels` limits (paying the required, self-funded deposits).
2. Fill each channel's stored contents up to `hrmp_channel_max_total_size` with unprocessed inbound messages (never consuming its own inbox so the messages remain in `HrmpChannelContents`).
3. Call `deregister` on itself via `paras_registrar`.
4. At the next session boundary, `perform_outgoing_para_cleanup` runs and removes every full `HrmpChannelContents` entry, at a cost not reflected by the `force_clean_hrmp` benchmark, which measured only empty channels.

The scoped impact — stalling session rotation for all paras — is bounded by the actual configured HRMP limits on the live network (channel count caps and `hrmp_channel_max_total_size`), which are governance-set and typically modest. The finding demonstrates a real benchmarking/weight-accounting gap (unaccounted-for cost scaling with channel content size), but whether it is sufficient by itself to exceed the relay chain's block weight/PoV limit and actually stall session rotation depends on those configuration values, which I cannot verify are large enough on any specific deployed network from this code alone.

### Likelihood Explanation
The preconditions (opening max channels, filling them to capacity, deregistering) are all reachable via normal, permissionless extrinsics available to any para manager, and are fully repeatable each time a new para offboards. The severity of the resulting weight underestimation scales directly with the network's configured `hrmp_channel_max_total_size` and channel-count limits, which are runtime-configurable and not controlled by the attacker — this caps how large the discrepancy can practically get on any given chain.

### Recommendation
Update the `force_clean_hrmp` benchmark (and, if necessary, `HrmpChannelContents`'s storage/weight modeling) to populate each benchmarked channel with the maximum permitted number/size of `InboundHrmpMessage`s (per `hrmp_channel_max_total_size`/`hrmp_channel_max_message_size`) before measuring `close_hrmp_channel`'s removal cost, so the generated `WeightInfo::force_clean_hrmp` weight includes a term proportional to worst-case channel content size, not just channel count.

### Proof of Concept
Benchmark/integration test plan:
1. In a test using `pallet_parachains_runtime_parachains::hrmp` mock, establish the maximum configured ingress/egress channels for a para, and fill each channel's `HrmpChannelContents` to `hrmp_channel_max_total_size` via repeated `queue_inbound_hrmp_message`-equivalent calls without processing/watermark advancement.
2. Deregister the para (or mark it in `outgoing_paras`) and invoke `Hrmp::initializer_on_new_session`.
3. Measure actual execution time / proof size recorded for the call versus `<T as Config>::WeightInfo::force_clean_hrmp(ingress_count, egress_count)`.
4. Assert `actual_weight.proof_size() <= benchmarked_weight.proof_size()` and `actual_weight.ref_time() <= benchmarked_weight.ref_time()`; expect this assertion to fail as channel content approaches `hrmp_channel_max_total_size`, demonstrating the benchmark underestimates the real cost.

### Citations

**File:** polkadot/runtime/parachains/src/hrmp.rs (L937-951)
```rust
	/// Called by the initializer to note that a new session has started.
	pub(crate) fn initializer_on_new_session(
		notification: &initializer::SessionChangeNotification<BlockNumberFor<T>>,
		outgoing_paras: &[ParaId],
	) -> Weight {
		let w1 = Self::perform_outgoing_para_cleanup(&notification.prev_config, outgoing_paras);
		Self::process_hrmp_open_channel_requests(&notification.prev_config);
		Self::process_hrmp_close_channel_requests();
		w1.saturating_add(<T as Config>::WeightInfo::force_process_hrmp_open(
			outgoing_paras.len() as u32
		))
		.saturating_add(<T as Config>::WeightInfo::force_process_hrmp_close(
			outgoing_paras.len() as u32,
		))
	}
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L959-974)
```rust
		let mut w = Self::clean_open_channel_requests(config, outgoing);
		for outgoing_para in outgoing {
			Self::clean_hrmp_after_outgoing(outgoing_para);

			// we need a few extra bits of data to weigh this -- all of this is read internally
			// anyways, so no overhead.
			let ingress_count =
				HrmpIngressChannelsIndex::<T>::decode_len(outgoing_para).unwrap_or_default() as u32;
			let egress_count =
				HrmpEgressChannelsIndex::<T>::decode_len(outgoing_para).unwrap_or_default() as u32;
			w = w.saturating_add(<T as Config>::WeightInfo::force_clean_hrmp(
				ingress_count,
				egress_count,
			));
		}
		w
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1033-1051)
```rust
	/// Remove all storage entries associated with the given para.
	fn clean_hrmp_after_outgoing(outgoing_para: &ParaId) {
		HrmpOpenChannelRequestCount::<T>::remove(outgoing_para);
		HrmpAcceptedChannelRequestCount::<T>::remove(outgoing_para);

		let ingress = HrmpIngressChannelsIndex::<T>::take(outgoing_para)
			.into_iter()
			.map(|sender| HrmpChannelId { sender, recipient: *outgoing_para });
		let egress = HrmpEgressChannelsIndex::<T>::take(outgoing_para)
			.into_iter()
			.map(|recipient| HrmpChannelId { sender: *outgoing_para, recipient });
		let mut to_close = ingress.chain(egress).collect::<Vec<_>>();
		to_close.sort();
		to_close.dedup();

		for channel in to_close {
			Self::close_hrmp_channel(&channel);
		}
	}
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1138-1164)
```rust
	fn close_hrmp_channel(channel_id: &HrmpChannelId) {
		if let Some(HrmpChannel { sender_deposit, recipient_deposit, .. }) =
			HrmpChannels::<T>::take(channel_id)
		{
			T::Currency::unreserve(
				&channel_id.sender.into_account_truncating(),
				sender_deposit.unique_saturated_into(),
			);
			T::Currency::unreserve(
				&channel_id.recipient.into_account_truncating(),
				recipient_deposit.unique_saturated_into(),
			);
		}

		HrmpChannelContents::<T>::remove(channel_id);

		HrmpEgressChannelsIndex::<T>::mutate(&channel_id.sender, |v| {
			if let Ok(i) = v.binary_search(&channel_id.recipient) {
				v.remove(i);
			}
		});
		HrmpIngressChannelsIndex::<T>::mutate(&channel_id.recipient, |v| {
			if let Ok(i) = v.binary_search(&channel_id.sender) {
				v.remove(i);
			}
		});
	}
```

**File:** polkadot/runtime/parachains/src/hrmp/benchmarking.rs (L216-283)
```rust
	#[benchmark]
	fn force_clean_hrmp(
		// ingress channels to a single leaving parachain that need to be closed.
		i: Linear<0, { HRMP_MAX_INBOUND_CHANNELS_BOUND - 1 }>,
		// egress channels to a single leaving parachain that need to be closed.
		e: Linear<0, { HRMP_MAX_OUTBOUND_CHANNELS_BOUND - 1 }>,
	) {
		// first, update the configs to support this many open channels...
		assert_ok!(Configuration::<T>::set_hrmp_max_parachain_outbound_channels(
			frame_system::RawOrigin::Root.into(),
			e + 1
		));
		assert_ok!(Configuration::<T>::set_hrmp_max_parachain_inbound_channels(
			frame_system::RawOrigin::Root.into(),
			i + 1
		));
		assert_ok!(Configuration::<T>::set_max_downward_message_size(
			frame_system::RawOrigin::Root.into(),
			1024
		));
		// .. and enact it.
		Configuration::<T>::initializer_on_new_session(&Shared::<T>::scheduled_session());

		let config = configuration::ActiveConfig::<T>::get();
		let deposit: BalanceOf<T> = config.hrmp_sender_deposit.unique_saturated_into();

		let para: ParaId = 1u32.into();
		register_parachain_with_balance::<T>(para, deposit);
		T::Currency::make_free_balance_be(&para.into_account_truncating(), deposit * 256u32.into());

		for ingress_para_id in 0..i {
			// establish ingress channels to `para`.
			let ingress_para_id = ingress_para_id + PREFIX_0;
			let _ = establish_para_connection::<T>(
				ingress_para_id,
				para.into(),
				ParachainSetupStep::Established,
			);
		}

		// nothing should be left unprocessed.
		assert_eq!(HrmpOpenChannelRequestsList::<T>::decode_len().unwrap_or_default(), 0);

		for egress_para_id in 0..e {
			// establish egress channels to `para`.
			let egress_para_id = egress_para_id + PREFIX_1;
			let _ = establish_para_connection::<T>(
				para.into(),
				egress_para_id,
				ParachainSetupStep::Established,
			);
		}

		// nothing should be left unprocessed.
		assert_eq!(HrmpOpenChannelRequestsList::<T>::decode_len().unwrap_or_default(), 0);

		// all in all, we have created this many channels.
		assert_eq!(HrmpChannels::<T>::iter().count() as u32, i + e);

		#[extrinsic_call]
		_(frame_system::Origin::<T>::Root, para, i, e);

		// all in all, all of them must be gone by now.
		assert_eq!(HrmpChannels::<T>::iter().count() as u32, 0);
		// borrow this function from the tests to make sure state is clear, given that we do a lot
		// of out-of-ordinary ops here.
		Hrmp::<T>::assert_storage_consistency_exhaustive();
	}
```

**File:** polkadot/runtime/rococo/src/weights/polkadot_runtime_parachains_hrmp.rs (L132-165)
```rust
	/// Storage: `Hrmp::HrmpIngressChannelsIndex` (r:128 w:128)
	/// Proof: `Hrmp::HrmpIngressChannelsIndex` (`max_values`: None, `max_size`: None, mode: `Measured`)
	/// Storage: `Hrmp::HrmpEgressChannelsIndex` (r:128 w:128)
	/// Proof: `Hrmp::HrmpEgressChannelsIndex` (`max_values`: None, `max_size`: None, mode: `Measured`)
	/// Storage: `Hrmp::HrmpChannels` (r:254 w:254)
	/// Proof: `Hrmp::HrmpChannels` (`max_values`: None, `max_size`: None, mode: `Measured`)
	/// Storage: `Hrmp::HrmpAcceptedChannelRequestCount` (r:0 w:1)
	/// Proof: `Hrmp::HrmpAcceptedChannelRequestCount` (`max_values`: None, `max_size`: None, mode: `Measured`)
	/// Storage: `Hrmp::HrmpChannelContents` (r:0 w:254)
	/// Proof: `Hrmp::HrmpChannelContents` (`max_values`: None, `max_size`: None, mode: `Measured`)
	/// Storage: `Hrmp::HrmpOpenChannelRequestCount` (r:0 w:1)
	/// Proof: `Hrmp::HrmpOpenChannelRequestCount` (`max_values`: None, `max_size`: None, mode: `Measured`)
	/// The range of component `i` is `[0, 127]`.
	/// The range of component `e` is `[0, 127]`.
	fn force_clean_hrmp(i: u32, e: u32, ) -> Weight {
		// Proof Size summary in bytes:
		//  Measured:  `297 + e * (100 ±0) + i * (100 ±0)`
		//  Estimated: `3759 + e * (2575 ±0) + i * (2575 ±0)`
		// Minimum execution time: 1_442_401_000 picoseconds.
		Weight::from_parts(1_459_213_000, 0)
			.saturating_add(Weight::from_parts(0, 3759))
			// Standard Error: 133_411
			.saturating_add(Weight::from_parts(4_222_698, 0).saturating_mul(i.into()))
			// Standard Error: 133_411
			.saturating_add(Weight::from_parts(4_358_958, 0).saturating_mul(e.into()))
			.saturating_add(T::DbWeight::get().reads(2))
			.saturating_add(T::DbWeight::get().reads((2_u64).saturating_mul(i.into())))
			.saturating_add(T::DbWeight::get().reads((2_u64).saturating_mul(e.into())))
			.saturating_add(T::DbWeight::get().writes(4))
			.saturating_add(T::DbWeight::get().writes((3_u64).saturating_mul(i.into())))
			.saturating_add(T::DbWeight::get().writes((3_u64).saturating_mul(e.into())))
			.saturating_add(Weight::from_parts(0, 2575).saturating_mul(e.into()))
			.saturating_add(Weight::from_parts(0, 2575).saturating_mul(i.into()))
	}
```
