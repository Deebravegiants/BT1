### Title
Sender's HRMP deposit is permanently trapped when a pending, unconfirmed `HrmpOpenChannelRequest` is offboarded together with its initiating para - ([File: polkadot/runtime/parachains/src/hrmp.rs])

### Summary
When a para calls `hrmp_init_open_channel` and is deregistered (via `paras_registrar::Pallet::do_deregister` → `schedule_para_cleanup`) before the recipient confirms the channel, the session-boundary cleanup routine `Hrmp::clean_open_channel_requests` deliberately skips refunding the sender's deposit because the sender is itself in the `outgoing` list. Because a deregistered `ParaId` can never again dispatch as a `Parachain` origin, the reserved deposit on that para's sovereign account becomes permanently unrecoverable without governance intervention.

### Finding Description
`Registrar::deregister` (unprivileged, callable by the para manager/owner) invokes `Pallet::do_deregister`, which calls `polkadot_runtime_parachains::schedule_para_cleanup::<T>(id)` [1](#0-0) . This marks the para for offboarding in the next scheduled session via `paras::Pallet::schedule_para_cleanup` [2](#0-1) .

At the next session boundary, `Hrmp::initializer_on_new_session` runs `perform_outgoing_para_cleanup`, which first calls `clean_open_channel_requests(config, outgoing)` to purge pending/unconfirmed HRMP open requests involving any offboarding para [3](#0-2) . Inside that routine, the sender's deposit is refunded **only if the sender is not in the `outgoing` list**:

```
if !outgoing.contains(&req_id.sender) {
    T::Currency::unreserve(&req_id.sender.into_account_truncating(), req_data.sender_deposit...);
}
``` [4](#0-3) 

If the sender para is the one being deregistered, this branch is skipped, and the `req_data.sender_deposit` reserved earlier in `init_open_channel` on `origin.into_account_truncating()` [5](#0-4)  is never unreserved. The `HrmpOpenChannelRequests`/`HrmpOpenChannelRequestsList` entries are still correctly removed, so storage stays internally consistent (no dangling entries, `assert_storage_consistency_exhaustive` would pass), but the reserved balance on the derived sovereign account is orphaned: a deregistered `ParaId` can never dispatch a `Parachain` origin again (`ensure_parachain` requires an active/registered para to route the XCM), so no signed call path exists to invoke `hrmp_cancel_open_request` or otherwise trigger `T::Currency::unreserve` on that account.

By contrast, once a channel is fully *established* (`HrmpChannels` entry exists), the analogous cleanup path `clean_hrmp_after_outgoing` → `close_hrmp_channel` unconditionally refunds both `sender_deposit` and `recipient_deposit` regardless of offboarding status [6](#0-5) , confirmed by the existing test `refund_deposit_on_offboarding` where the offboarding sender's balance is fully restored to 100 [7](#0-6) . The asymmetry only affects the *pending/unconfirmed* request path.

The existing test `no_dangling_open_requests`, which covers exactly the init-then-deregister-same-session scenario, only asserts the recipient's balance is refunded and the storage consistency check passes — it never asserts the sender (`para_a`) balance is restored [8](#0-7) , consistent with the sender's deposit being silently lost.

### Impact Explanation
The para's `hrmp_sender_deposit` (a real reserved balance amount, configured via `configuration::ActiveConfig`) becomes permanently stuck on the deterministic sovereign account derived from the deregistered `ParaId`. Since the account cannot originate a `Parachain` XCM origin anymore, and normal `Balances`/`unreserve` cannot be called by a signed account on funds it does not directly control via extrinsic (unreserve is an internal `Currency` trait call, not a dispatchable), recovering the funds requires a governance/root-level `force_unreserve` or similar privileged intervention. This is a genuine, self-contained fund-loss/accounting bug reachable purely through normal unprivileged extrinsics.

### Likelihood Explanation
Fully reachable by any unprivileged para manager: call `hrmp_init_open_channel(A, B, ...)` from para A's origin, then call `Registrar::deregister(A)` before the recipient B calls `hrmp_accept_open_channel`, and let the scheduled session elapse. No special privileges, race conditions with validators, or governance actions are required — this is deterministic and repeatable every time an unconfirmed request exists at the moment a para self-deregisters.

### Recommendation
In `Hrmp::clean_open_channel_requests`, always unreserve the sender's deposit when purging a pending open request, regardless of whether the sender itself is in the `outgoing` list (the recipient-side check should remain conditioned on the recipient's offboarding status, since it is refunding on behalf of a different account). I.e., change:
```
if !outgoing.contains(&req_id.sender) {
    T::Currency::unreserve(...);
}
```
to unconditionally unreserve the sender's own deposit, matching the behavior of `close_hrmp_channel`, which always refunds both parties irrespective of offboarding.

### Proof of Concept
Add to `polkadot/runtime/parachains/src/hrmp/tests.rs`, extending `no_dangling_open_requests`/`refund_deposit_on_offboarding`:
```rust
#[test]
fn sender_deposit_trapped_on_pending_request_offboarding() {
    let para_a = 2032.into();
    let para_b = 2064.into();
    let mut genesis = GenesisConfigBuilder::default();
    genesis.hrmp_sender_deposit = 20;
    genesis.hrmp_recipient_deposit = 15;
    new_test_ext(genesis.build()).execute_with(|| {
        register_parachain_with_balance(para_a, 100);
        register_parachain_with_balance(para_b, 110);
        run_to_block(5, Some(vec![4, 5]));

        Hrmp::init_open_channel(para_a, para_b, 2, 8).unwrap();
        assert_eq!(<Test as Config>::Currency::free_balance(&para_a.into_account_truncating()), 80);

        deregister_parachain(para_a); // schedule_para_cleanup
        run_to_block(9, Some(vec![9])); // offboarding enacted, request purged

        Hrmp::assert_storage_consistency_exhaustive(); // passes, no dangling entries

        // BUG: sender deposit never returned
        assert_ne!(
            <Test as Config>::Currency::free_balance(&para_a.into_account_truncating()),
            100
        );
        assert_eq!(
            <Test as Config>::Currency::reserved_balance(&para_a.into_account_truncating()),
            20 // permanently stuck
        );
    });
}
```
Expected result: the test demonstrates that `free_balance` for `para_a` stays at 80 (not restored to 100) and `reserved_balance` remains 20 indefinitely, confirming the trapped deposit, while `assert_storage_consistency_exhaustive` passes — showing storage consistency alone is insufficient to catch this accounting defect.

### Citations

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L660-667)
```rust
	fn do_deregister(id: ParaId) -> DispatchResult {
		match paras::Pallet::<T>::lifecycle(id) {
			// Para must be a parathread (on-demand parachain), or not exist at all.
			Some(ParaLifecycle::Parathread) | None => {},
			_ => return Err(Error::<T>::NotParathread.into()),
		}
		polkadot_runtime_parachains::schedule_para_cleanup::<T>(id)
			.map_err(|_| Error::<T>::CannotDeregister)?;
```

**File:** polkadot/runtime/parachains/src/paras/mod.rs (L2133-2151)
```rust
		let lifecycle = ParaLifecycles::<T>::get(&id);
		match lifecycle {
			// If para is not registered, nothing to do!
			None => return Ok(()),
			Some(ParaLifecycle::Parathread) => {
				ParaLifecycles::<T>::insert(&id, ParaLifecycle::OffboardingParathread);
			},
			Some(ParaLifecycle::Parachain) => {
				ParaLifecycles::<T>::insert(&id, ParaLifecycle::OffboardingParachain);
			},
			_ => return Err(Error::<T>::CannotOffboard.into()),
		}

		let scheduled_session = Self::scheduled_session();
		ActionsQueue::<T>::mutate(scheduled_session, |v| {
			if let Err(i) = v.binary_search(&id) {
				v.insert(i, id);
			}
		});
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L955-975)
```rust
	fn perform_outgoing_para_cleanup(
		config: &HostConfiguration<BlockNumberFor<T>>,
		outgoing: &[ParaId],
	) -> Weight {
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
	}
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1006-1012)
```rust
			// Return the deposit of the sender, but only if it is not the para being offboarded.
			if !outgoing.contains(&req_id.sender) {
				T::Currency::unreserve(
					&req_id.sender.into_account_truncating(),
					req_data.sender_deposit.unique_saturated_into(),
				);
			}
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1132-1150)
```rust
	/// Close and remove the designated HRMP channel.
	///
	/// This includes returning the deposits.
	///
	/// This function is idempotent, meaning that after the first application it should have no
	/// effect (i.e. it won't return the deposits twice).
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
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1485-1493)
```rust
		// Do not require deposits for channels with or amongst the system.
		let is_system = origin.is_system() || recipient.is_system();
		let deposit = if is_system { 0 } else { config.hrmp_sender_deposit };
		if !deposit.is_zero() {
			T::Currency::reserve(
				&origin.into_account_truncating(),
				deposit.unique_saturated_into(),
			)?;
		}
```

**File:** polkadot/runtime/parachains/src/hrmp/tests.rs (L785-822)
```rust
#[test]
fn refund_deposit_on_offboarding() {
	let para_a = 2032.into();
	let para_b = 2064.into();

	let mut genesis = GenesisConfigBuilder::default();
	genesis.hrmp_sender_deposit = 20;
	genesis.hrmp_recipient_deposit = 15;
	new_test_ext(genesis.build()).execute_with(|| {
		// Register two parachains and open a channel between them.
		register_parachain_with_balance(para_a, 100);
		register_parachain_with_balance(para_b, 110);
		run_to_block(5, Some(vec![4, 5]));
		Hrmp::init_open_channel(para_a, para_b, 2, 8).unwrap();
		Hrmp::accept_open_channel(para_b, para_a).unwrap();
		assert_eq!(<Test as Config>::Currency::free_balance(&para_a.into_account_truncating()), 80);
		assert_eq!(<Test as Config>::Currency::free_balance(&para_b.into_account_truncating()), 95);
		run_to_block(8, Some(vec![8]));
		assert!(channel_exists(para_a, para_b));

		// Then deregister one parachain.
		deregister_parachain(para_a);
		run_to_block(10, Some(vec![9, 10]));

		// The channel should be removed.
		assert!(!Paras::is_valid_para(para_a));
		assert!(!channel_exists(para_a, para_b));
		Hrmp::assert_storage_consistency_exhaustive();

		assert_eq!(
			<Test as Config>::Currency::free_balance(&para_a.into_account_truncating()),
			100
		);
		assert_eq!(
			<Test as Config>::Currency::free_balance(&para_b.into_account_truncating()),
			110
		);
	});
```

**File:** polkadot/runtime/parachains/src/hrmp/tests.rs (L825-861)
```rust
#[test]
fn no_dangling_open_requests() {
	let para_a = 2032.into();
	let para_b = 2064.into();

	let mut genesis = GenesisConfigBuilder::default();
	genesis.hrmp_sender_deposit = 20;
	genesis.hrmp_recipient_deposit = 15;
	new_test_ext(genesis.build()).execute_with(|| {
		// Register two parachains and open a channel between them.
		register_parachain_with_balance(para_a, 100);
		register_parachain_with_balance(para_b, 110);
		run_to_block(5, Some(vec![4, 5]));

		// Start opening a channel a->b
		Hrmp::init_open_channel(para_a, para_b, 2, 8).unwrap();
		assert_eq!(<Test as Config>::Currency::free_balance(&para_a.into_account_truncating()), 80);

		// Then deregister one parachain, but don't wait two sessions until it takes effect.
		// Instead, `para_b` will confirm the request, which will take place the same time
		// the offboarding should happen.
		deregister_parachain(para_a);
		run_to_block(9, Some(vec![9]));
		Hrmp::accept_open_channel(para_b, para_a).unwrap();
		assert_eq!(<Test as Config>::Currency::free_balance(&para_b.into_account_truncating()), 95);
		assert!(!channel_exists(para_a, para_b));
		run_to_block(10, Some(vec![10]));

		// The outcome we expect is `para_b` should receive the refund.
		assert_eq!(
			<Test as Config>::Currency::free_balance(&para_b.into_account_truncating()),
			110
		);
		assert!(!channel_exists(para_a, para_b));
		Hrmp::assert_storage_consistency_exhaustive();
	});
}
```
