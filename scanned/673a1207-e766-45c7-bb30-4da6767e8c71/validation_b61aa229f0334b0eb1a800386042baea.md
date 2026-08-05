### Title
Confirmed HRMP channel deposits can be permanently trapped if sender/recipient para becomes invalid before `process_hrmp_open_channel_requests` runs - (File: `polkadot/runtime/parachains/src/hrmp.rs`)

### Summary
`hrmp_init_open_channel`/`hrmp_accept_open_channel` reserve `sender_deposit`/`recipient_deposit` via `ReservableCurrency::reserve`, and those deposits are only ever released by `close_hrmp_channel`'s `unreserve`, which runs only for channels that actually made it into `HrmpChannels`. In `Pallet::process_hrmp_open_channel_requests`, when either side of a pending request fails `paras::Pallet::<T>::is_valid_para` (e.g. because the para offboarded mid-window), the code removes the `HrmpOpenChannelRequests` entry and adjusts `HrmpOpenChannelRequestCount`/`HrmpAcceptedChannelRequestCount` via `decrease_open_channel_request_count`/`decrease_accepted_channel_request_count`, but there is no corresponding `unreserve` call in that branch.

### Finding Description
The deposit lifecycle for HRMP channels is:
- `init_open_channel` reserves `config.hrmp_sender_deposit` from the sender's deposit account.
- `accept_open_channel` reserves `config.hrmp_recipient_deposit` from the recipient's deposit account.
- `close_hrmp_channel`/`clean_hrmp_after_outgoing` is the only code path that calls `T::Currency::unreserve` for these deposits, and it operates on entries present in `HrmpChannels`/`HrmpIngressChannelsIndex`/`HrmpEgressChannelsIndex` — i.e. channels that were actually created.

`process_hrmp_open_channel_requests` is the session-boundary routine that turns a confirmed `HrmpOpenChannelRequest` into a `HrmpChannels` entry, guarded by `paras::Pallet::<T>::is_valid_para` checks for both `channel_id.sender` and `channel_id.recipient` [1](#0-0) . When one side is no longer a valid para (offboarded between request creation/acceptance and the next session change), the function does not create the `HrmpChannels` entry — instead it decrements the request/accept counters and removes the `HrmpOpenChannelRequests` entry, without ever touching the previously reserved deposits [2](#0-1) . Because the channel was never created, `close_hrmp_channel` (the only unreserve path) can never be invoked for it, and the deposits taken during `init_open_channel`/`accept_open_channel` remain reserved indefinitely with no remaining code path that references them.

This is a known asymmetry in the deposit-accounting design: the invalidation/skip branch is a purely defensive check against a para disappearing mid-cycle, but it was not paired with a refund of the deposits that were reserved on the assumption the channel would be created.

### Impact Explanation
Both `sender_deposit` and `recipient_deposit` (parachain deposit accounts, not end users) become permanently reserved balance with no `HrmpChannels` entry and no code path left that can call `unreserve` for that specific request. This matches the scoped impact: reserved balance is trapped, backing nothing, with no recovery mechanism available to the affected para through any existing unprivileged extrinsic (`hrmp_cancel_open_request` only operates on requests still present in `HrmpOpenChannelRequests`, which have already been removed by this point).

### Likelihood Explanation
The trigger requires: (1) a sender para calls `hrmp_init_open_channel`, (2) the recipient para calls `hrmp_accept_open_channel` to confirm it, and (3) before the next session boundary, one of the two paras becomes invalid (offboarded/deregistered) via the normal para lifecycle. Para offboarding is not attacker-forced in the sense of bypassing checks — it follows the standard lease-expiry/governance-driven lifecycle — but once initiated, the timing window (any point before the next session change) is wide and not adversarially hardenable by the counterparty; a sender/recipient para operator who is aware of an impending offboarding of its channel partner (or its own) can reliably reproduce this every time by opening/accepting a channel shortly before the offboarding session change.

### Recommendation
In the invalid-para branch of `process_hrmp_open_channel_requests`, call `T::Currency::unreserve` for the sender's `sender_deposit` (always) and for the recipient's `recipient_deposit` (only if `request.confirmed` is true, matching when it was actually reserved), mirroring the accounting done in `close_hrmp_channel`, before removing the `HrmpOpenChannelRequests` entry.

### Proof of Concept
Add an integration test to `polkadot/runtime/parachains/src/hrmp/tests.rs`:
1. Register two paras A (sender) and B (recipient) as valid.
2. Call `Hrmp::init_open_channel(A, B, ...)` and `Hrmp::accept_open_channel(B, A)`, and assert `Balances::reserved_balance(A_deposit_account) == sender_deposit` and `Balances::reserved_balance(B_deposit_account) == recipient_deposit`.
3. Before the next session change, deregister/offboard para B (simulate via test helper that flips `paras::Pallet::<Test>::is_valid_para(B)` to false, e.g. by running the standard para lifecycle transition to `Parathread`/`Onboarding`/removed state used elsewhere in the test suite).
4. Run the session-change hook that calls `process_hrmp_open_channel_requests`.
5. Assert `HrmpChannels::<Test>::get(&HrmpChannelId{sender: A, recipient: B})` is `None` (channel not created) and assert `Balances::reserved_balance(A_deposit_account)` and `Balances::reserved_balance(B_deposit_account)` are still equal to the original deposits (non-zero), proving the funds remain trapped instead of returning to zero.

### Citations

**File:** polkadot/runtime/parachains/src/hrmp.rs (L390-402)
```rust
	/// This mapping tracks how many open channel requests are initiated by a given sender para.
	/// Invariant: `HrmpOpenChannelRequests` should contain the same number of items that has
	/// `(X, _)` as the number of `HrmpOpenChannelRequestCount` for `X`.
	#[pallet::storage]
	pub type HrmpOpenChannelRequestCount<T: Config> =
		StorageMap<_, Twox64Concat, ParaId, u32, ValueQuery>;

	/// This mapping tracks how many open channel requests were accepted by a given recipient para.
	/// Invariant: `HrmpOpenChannelRequests` should contain the same number of items `(_, X)` with
	/// `confirmed` set to true, as the number of `HrmpAcceptedChannelRequestCount` for `X`.
	#[pallet::storage]
	pub type HrmpAcceptedChannelRequestCount<T: Config> =
		StorageMap<_, Twox64Concat, ParaId, u32, ValueQuery>;
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L425-429)
```rust
	/// HRMP channel data associated with each para.
	/// Invariant:
	/// - each participant in the channel should satisfy `Paras::is_valid_para(P)` within a session.
	#[pallet::storage]
	pub type HrmpChannels<T: Config> = StorageMap<_, Twox64Concat, HrmpChannelId, HrmpChannel>;
```
