No vulnerability found for this question.

Reasoning: The Code4rena finding describes a cryptographic flaw where a custom secret-sharing/encryption backup scheme (SSS-based) is initialized with trivial threshold=0 parameters, allowing the resulting on-chain ciphertext to be deterministically decrypted without guardian participation. This is fundamentally a crypto-library design flaw in an off-chain/hybrid encryption backup system.

The closest analog in `polkadot-sdk` is `substrate/frame/recovery` (pallet-recovery / the newer friend-groups design), but its recovery mechanism is structurally different — it is a pure on-chain state-machine/authorization gate, not a cryptographic secret-sharing scheme that encrypts a master key. Recovery there works by requiring actual signed extrinsics from friends (`approve_attempt`) to be recorded on-chain before `as_recovered`/`control_inherited_account` access is granted; there is no encrypted secret whose decryption key could be trivially reconstructed from public data.

Critically, the pallet explicitly validates against the exact "weak parameter" pattern described in the report: [1](#0-0) 
which shows `set_friend_groups` rejecting `friends_needed: 0` with `Error::<T>::NoFriendsNeeded`, and [2](#0-1) 
which shows `approve_attempt` requiring a real signed extrinsic per friend, counted via `attempt.approvals`, before a recovery can proceed — there is no deterministic, off-chain-computable bypass analogous to the `threshold = 0` → `Secret(Fr::ZERO)` derivation in the Swafe report.

There is also no automatic/default recovery configuration created at account genesis with weak parameters in this pallet (unlike the Swafe `AccountUpdate` flow that always populates `rec.social` with `threshold = 0` at registration); `create_recovery`/`set_friend_groups` are opt-in, user-initiated, and validated. Since the underlying vulnerable primitive (a custom threshold secret-sharing encryption scheme with a zero-threshold degenerate case) does not exist in this codebase, and the analogous FRAME pallet already enforces non-zero threshold checks with on-chain approval gating rather than cryptographic reconstruction, this vulnerability class does not have a reachable, unprivileged analog in the polkadot-sdk code.

### Citations

**File:** substrate/frame/recovery/src/tests.rs (L146-164)
```rust
/// Setting a friend group with `friends_needed` of zero fails.
#[test]
fn set_friend_groups_zero_friends_needed_fails() {
	new_test_ext().execute_with(|| {
		let fg = FriendGroupOf::<T> {
			friends: friends([BOB, CHARLIE, DAVE]),
			friends_needed: 0,
			inheritor: FERDIE,
			inheritance_delay: 10,
			inheritance_priority: 0,
			cancel_delay: 10,
		};

		assert_noop!(
			Recovery::set_friend_groups(signed(ALICE), vec![fg]),
			Error::<T>::NoFriendsNeeded
		);
	});
}
```

**File:** substrate/frame/recovery/src/lib.rs (L748-788)
```rust
		/// Approve the recovery for a lost account.
		///
		/// Must be called by a friend of the friend group that the recovery attempt belongs to that
		/// did not yet vote. Voting is only allowed until the threshold is reached.
		/// `finish_attempt` should be called after the last friend voted.
		#[pallet::call_index(4)]
		#[pallet::weight(T::WeightInfo::approve_attempt())]
		pub fn approve_attempt(
			origin: OriginFor<T>,
			lost: AccountIdLookupOf<T>,
			friend_group_index: FriendGroupIndex,
		) -> DispatchResult {
			let friend = ensure_signed(origin)?;
			let lost = T::Lookup::lookup(lost)?;
			let now = T::BlockNumberProvider::current_block_number();

			let (mut attempt, ticket, deposit) = Self::attempt_of(&lost, friend_group_index)?;
			let friend_group = Self::friend_group_of(&lost, friend_group_index).defensive()?;

			let friend_index = friend_group
				.friends
				.iter()
				.position(|f| f == &friend)
				.ok_or(Error::<T>::NotFriend)?;

			let friends_voted = attempt.approvals.count_ones();
			ensure!(friends_voted < friend_group.friends_needed, Error::<T>::AlreadyApproved);
			attempt.last_approval_block = now;

			attempt
				.approvals
				.set_if_not_set(friend_index)
				.map_err(|_| Error::<T>::AlreadyVoted)?;

			// NOTE: We do not update the ticket since the attempt has static size.
			Attempt::<T>::insert(&lost, friend_group_index, (&attempt, &ticket, &deposit));

			Self::deposit_event(Event::<T>::AttemptApproved { lost, friend_group_index, friend });

			Ok(())
		}
```
