Audit Report

## Title
HRMP open-channel deposits can become permanently unreservable if a para offboards at the exact session boundary that processes its confirmed channel request - ([File: polkadot/runtime/parachains/src/hrmp.rs])

## Summary
`Pallet::process_hrmp_open_channel_requests` creates the `HrmpChannels` entry only when `paras::Pallet::<T>::is_valid_para` returns true for both `channel_id.sender` and `channel_id.recipient`, but the fallback branch that fires when either side has become invalid still decrements the open/accepted channel counters and removes the request from `HrmpOpenChannelRequestsList` / `HrmpOpenChannelRequests` without unreserving `request.sender_deposit`. Because this function runs before `clean_hrmp_after_outgoing` for the same set of `outgoing_paras` in the session-change hook, a para that offboards in the same session in which its confirmed HRMP request is processed causes the sender's deposit to be permanently orphaned in the reserved balance with no remaining on-chain reference to unreserve it. [1](#0-0) 

## Finding Description
`HrmpOpenChannelRequest.sender_deposit` is reserved at `hrmp_init_open_channel` time and the request is marked `confirmed` by `hrmp_accept_open_channel`, remaining queued in `HrmpOpenChannelRequestsList` until the next session boundary. At the session boundary, the initializer first finalizes lifecycle transitions via `paras::Pallet::<T>::initializer_on_new_session` (producing the `outgoing_paras` list for that session and updating the lifecycle map so `is_valid_para` reflects the removal), and only afterward invokes `hrmp::Pallet::<T>::initializer_on_new_session`, which runs `process_hrmp_open_channel_requests` before iterating `outgoing_paras` and calling `clean_hrmp_after_outgoing`.

Inside `process_hrmp_open_channel_requests`, each confirmed request is checked with `is_valid_para(sender) && is_valid_para(recipient)`. When this check fails — because one side is offboarding in this very session — the function does not create the `HrmpChannels` entry, but it still executes `decrease_open_channel_request_count` / `decrease_accepted_channel_request_count` and removes the entry from both `HrmpOpenChannelRequestsList` and `HrmpOpenChannelRequests`, with no call to unreserve `sender_deposit` on this branch. When `clean_hrmp_after_outgoing` subsequently executes for that same outgoing para, it scans `HrmpOpenChannelRequestsList` for pending requests involving the para to refund and purge — but the request has already been deleted, so no unreserve occurs there either. The deposit is left reserved on the sender's account with no storage item (`HrmpChannels`, `HrmpOpenChannelRequests`) referencing it and no extrinsic path to release it.

This is a genuine ordering/accounting gap: the existing guard (`is_valid_para` check) correctly prevents channel creation with an invalid para, but the code that handles the "invalid para" branch was written as if the request could simply be dropped, without accounting for the reserved currency backing it.

## Impact Explanation
The affected sender's `sender_deposit` becomes permanently locked in reserved balance with no on-chain path to recovery — this is a silent, deterministic loss of user funds triggered purely by ordinary session-boundary processing of already-legitimate extrinsic calls (`hrmp_init_open_channel`, `hrmp_accept_open_channel`, and a normal para offboarding). It violates the core invariant that every HRMP deposit must back either an active channel or be returned to its owner.

## Likelihood Explanation
The precondition (a confirmed pending HRMP request coinciding with the recipient/sender's offboarding session) is a realistic and controllable timing scenario: an offboarding para operator controls both when they trigger deregistration and when they call `hrmp_accept_open_channel`, making the exploit deterministic and repeatable once the ordering is arranged, even though it also could occur as an unintentional coincidence between two independent chains.

## Recommendation
In the `else` branch of `process_hrmp_open_channel_requests` (where `is_valid_para` fails for either side), unreserve `request.sender_deposit` (and any recipient deposit already reserved via `hrmp_accept_open_channel`) before removing the request from storage, mirroring the unreserve logic in `clean_hrmp_after_outgoing`. Alternatively, reorder the session-change hook so `clean_hrmp_after_outgoing` for `outgoing_paras` runs before `process_hrmp_open_channel_requests`, ensuring stale requests involving offboarding paras are refunded and purged first.

## Proof of Concept
1. Register paras A (sender) and B (recipient); fund both and call `Hrmp::hrmp_init_open_channel(A, B, ...)`, reserving `sender_deposit` from A's account.
2. Call `Hrmp::hrmp_accept_open_channel(B, A)`, marking the request `confirmed = true` and reserving B's deposit.
3. Before the next session change, schedule B (or A) for offboarding via the normal deregistration flow.
4. Record A's `reserved_balance` prior to the session change.
5. Trigger the session change so `Initializer::on_new_session` runs `paras::initializer_on_new_session` (offboarding B) followed by `hrmp::initializer_on_new_session` (processing the confirmed request).
6. Assert `HrmpChannels` has no entry for the channel, `HrmpOpenChannelRequests` has no entry for the channel, and A's `reserved_balance` is unchanged — the deposit is neither applied to a channel nor released.

### Citations

**File:** polkadot/runtime/parachains/src/hrmp.rs (L114-120)
```rust
/// A description of a request to open an HRMP channel.
#[derive(Encode, Decode, TypeInfo)]
pub struct HrmpOpenChannelRequest {
	/// Indicates if this request was confirmed by the recipient.
	pub confirmed: bool,
	/// NOTE: this field is deprecated. Channel open requests became non-expiring and this value
	/// became unused.
```
