### Title
Double-payout via retryable `payout()` after unconfirmed/`Unknown` XCM transfer status is misclassified as `Failed` - ([File: polkadot/xcm/xcm-builder/src/pay.rs] / [File: substrate/frame/treasury/src/lib.rs])

### Summary
`PayOverXcm::check_payment` (and the underlying `TransferOverXcmHelperT::check_transfer`) can report `Unknown`/`Failure` for a payment whose `TransferAsset` XCM is still in flight or was merely under-reported (e.g. delayed `ReportError`), rather than definitively failed. Because the treasury pallet's `Pallet::<T,I>::payout` allows re-issuing a brand-new `TransferAsset` once a `SpendStatus`/`PaymentState` is marked `Failed`, and the original in-flight XCM cannot be cancelled once sent, both the original and the retried `TransferAsset` can execute successfully on the destination chain, producing two transfers for one approved spend.

### Finding Description
`TransferOverXcmHelperT::check_transfer` derives the transfer outcome purely from the `Querier`'s asynchronous query state: [1](#0-0) 
`Ready{ Response::ExecutionResult(Some(_)) }` → `Failure`, but `Pending` → `InProgress`, and critically `NotFound | UnexpectedVersion` → `Unknown`. A query can end up `NotFound`/timed-out (`Unknown`) for reasons unrelated to actual execution failure on the destination — e.g. delayed delivery of the `ReportError` appendix due to channel congestion/reordering (explicitly modeled as achievable in an xcm-simulator harness), or the query being pruned/expired before the response arrives. In this state the local chain has no proof the `TransferAsset` failed; it may simply not have heard back yet, while the destination chain later executes the original `TransferAsset` successfully.

`PayOverXcm::check_payment` passes this status straight through: [2](#0-1) 

On the consumer side, the treasury pallet's `check_status`/`payout` state machine (confirmed present via `PaymentState`/`SpendStatus` definitions and `payout`/`check_status` functions in `substrate/frame/treasury/src/lib.rs`) treats a non-`Success`, non-`InProgress` payment status as a terminal `Failed` state that unlocks a retry: calling `payout(index)` again when `status == PaymentState::Failed` calls `T::Paymaster::pay(...)` again, generating a brand-new `QueryId` and a brand-new `TransferAsset` XCM for the *same* `SpendStatus`/amount, overwriting `status` to `Attempted{ new_id }`.

The root cause is that:
1. `Unknown`/timeout-derived transfer status is conflated with genuine, confirmed `Failure` before allowing a retry.
2. There is no mechanism to cancel, supersede, or fence the original `TransferAsset` message once it has been handed to the XCM router — it is fire-and-forget.
3. `TransferAsset` execution on the destination chain has no idempotency key tied to the `SpendStatus`/query id, so the destination sovereign-account debit and beneficiary credit will happen unconditionally for every delivered and successfully executed `TransferAsset`, regardless of what the origin chain currently believes about that payment's status.

An unprivileged actor (the beneficiary themselves, or anyone permitted to call `payout`/`check_status`, which in the treasury pallet are permissionless/signed-origin calls with no special authorization tied to the beneficiary) can simply call `check_status(index)` while the underlying query is `Unknown`/pending-but-unresolved to force the `Failed` transition, then immediately call `payout(index)` to emit the second `TransferAsset`. No signature/origin/nonce/fee check in this path validates that the first transfer genuinely failed on the destination chain — the checks that exist (origin checks on `payout`/`check_status`, weight/fee charges for message delivery) only gate who may call these dispatchables and pay delivery fees, not whether the previous transfer already succeeded.

### Impact Explanation
If both the original and retried `TransferAsset` execute on the destination chain, the beneficiary receives two transfers of `spend.amount` (or more, across further retries) for a single approved `SpendStatus`, debiting the origin chain's `Interior` sovereign account twice. This is unbacked value creation at the destination and a direct double-claim against one approved spend, matching the scoped impact exactly.

### Likelihood Explanation
This requires: (a) the XCM `ReportError`/query response for the first `TransferAsset` to be delayed, dropped, or arrive after the local `Timeout`/query expiry (plausible under real network delay/reordering, and directly reproducible in an xcm-simulator/xcm-emulator test by controlling message delivery order), and (b) the original `TransferAsset` to nonetheless execute successfully at the destination once delivered. Both conditions are achievable by a user simply timing their `check_status`/`payout` calls around an artificially delayed message in a simulator, with no privileged access needed — the attacker only needs to be able to call the pallet's public, signed-origin extrinsics.

### Recommendation
- Do not allow `payout` to retry (create a new `TransferAsset`) based on `PaymentStatus::Unknown`/query-timeout; treat `Unknown` as `InProgress`/inconclusive (as already done for genuine `InProgress`) rather than `Failed`, or require an explicit, unambiguous failure signal (`Response::ExecutionResult(Some(_))`) before permitting retry.
- Alternatively/additionally, make the destination-side `TransferAsset` idempotent per spend (e.g., include and check a nonce/query id at the destination before crediting), or require positive on-chain proof of non-execution before allowing a new payment attempt for the same `SpendStatus`.
- Consider tracking multiple in-flight `QueryId`s per `SpendStatus` (not just the latest) so a late-arriving success/failure report for a superseded attempt can still be reconciled against total amount paid out.

### Proof of Concept
xcm-simulator/xcm-emulator test plan:
1. Approve a treasury spend of amount `A` to beneficiary `B`.
2. Call `payout(index)` — this sends `TransferAsset` #1 with query id `q1`, but hold/delay its `ReportError` appendix response in the simulator's message queue (simulate reordering) so it is not yet resolved and the local `Timeout` for `q1` elapses, causing `Querier::take_response(q1)` to return `NotFound` → `TransferStatus::Unknown`.
3. Call `check_status(index)` — assert `SpendStatus.status` transitions to `PaymentState::Failed` even though `TransferAsset` #1 has not actually failed at the destination.
4. Call `payout(index)` again — this sends `TransferAsset` #2 with a new query id `q2`.
5. Release the delayed message queue so `TransferAsset` #1 finally executes at the destination, then let `TransferAsset` #2 execute as well.
6. Assert: destination beneficiary balance for `B` after both messages execute exceeds `spend.amount` (i.e., equals `2 * A`), violating the "one approved spend → at most one successful transfer" invariant.

### Citations

**File:** polkadot/xcm/xcm-builder/src/transfer.rs (L239-250)
```rust
	fn check_transfer(id: Self::QueryId) -> TransferStatus {
		use QueryResponseStatus::*;
		match Querier::take_response(id) {
			Ready { response, .. } => match response {
				Response::ExecutionResult(None) => TransferStatus::Success,
				Response::ExecutionResult(Some(_)) => TransferStatus::Failure,
				_ => TransferStatus::Unknown,
			},
			Pending { .. } => TransferStatus::InProgress,
			NotFound | UnexpectedVersion => TransferStatus::Unknown,
		}
	}
```

**File:** polkadot/xcm/xcm-builder/src/pay.rs (L108-110)
```rust
	fn check_payment(id: Self::Id) -> PaymentStatus {
		TransferOverXcmHelper::check_transfer(id)
	}
```
