### Title
Permanently-overweight XCM messages (e.g. asset `WithdrawAsset`/`DepositAsset`) can be silently reaped by `do_reap_page` before `execute_overweight` is called, discarding the message while the corresponding assets were already debited on the source chain - (File: substrate/frame/message-queue/src/lib.rs)

### Summary
`pallet-message-queue` marks a message that exceeds `ServiceWeight` as "permanently overweight" and advances the page's processing cursor past it so the page can still be considered "done" from the perspective of ordinary queue servicing, while the raw message bytes remain addressable only through the separate manual `execute_overweight` path. Because page cleanup (`ReapPage`/`do_reap_page`) is driven by the page-completion/staleness watermark (`MaxStale`) and not by whether every message it contains has actually been executed, a page holding an un-executed overweight message can be reaped once enough newer pages accumulate in the same queue, permanently destroying the message data (and any `Overweight` index pointing at it).

### Finding Description
The message-queue pallet's documented design (see the module doc, `substrate/frame/message-queue/src/lib.rs`) explicitly separates "message servicing" (bounded by `ServiceWeight`, run in `on_initialize`/`service_queues`) from "overweight execution" (a manual, permissionless call, `Pallet::execute_overweight` / `do_execute_overweight_inner`). When a message cannot be executed within the available weight and is marked permanently overweight, its slot in the page is skipped (the page's read cursor/`remaining` count is advanced as if the message were processed) so that queue servicing can continue past it. The page is only kept alive as long as it is needed to preserve the byte-addressable overweight entry; once the pallet's own bookkeeping considers the page "done" (all entries either processed or skipped-as-overweight) it becomes a candidate for `do_reap_page`, which is gated only by the `MaxStale` watermark of trailing done/stale pages in that queue, not by whether any `Overweight`-indexed message inside it is still unexecuted.

For a cross-chain asset transfer, the XCM containing `WithdrawAsset`/`ReserveAssetDeposited`+`DepositAsset` (or a `Transact` performing the deposit) is delivered via UMP/DMP/HRMP into a specific per-origin queue (keyed by the sending chain/`ParaId`). If that XCM becomes permanently overweight at the destination (e.g., due to weight mis-estimation or a deliberately weight-heavy payload chosen relative to `ServiceWeight`), the destination-side page holding it is eligible for the same treatment as any other completed page. An unprivileged attacker (the intended recipient, or anyone who can route additional traffic into that same queue key, e.g. via repeated `pallet_xcm::send` calls that produce cheap messages routed through the same channel) can push `MaxStale`+N further pages through that queue without ever calling `execute_overweight` on the asset message. Once the watermark is exceeded, `do_reap_page` removes the page (and its data) from storage.

No check in this path re-verifies "is there still an un-executed overweight message referenced by `Overweight` within this page" before allowing reaping; the staleness/­watermark logic only reasons about page completion counters, not about outstanding manual-execution obligations. This is consistent with the pallet's stated goal of bounding storage/PoV growth rather than guaranteeing indefinite retention of unexecuted overweight messages.

### Impact Explanation
If the source chain has already burned/reserved/withdrawn the asset before or as part of sending the XCM (the normal reserve-transfer/teleport protocol), and the destination-side `DepositAsset`/`Transact` is lost because its page was reaped before manual execution, the asset is permanently unbacked on the destination and cannot be minted/credited there, while it no longer exists on the source. This breaks the cross-chain conservation invariant ("assets debited on source must be recoverable or refunded, not silently vanish") and results in an unrecoverable loss of user funds, without any error being surfaced back to the source chain (XCM is fire-and-forget once delivered/enqueued).

### Likelihood Explanation
Exploitability requires: (1) the XCM must actually become *permanently* overweight at the destination - this depends on weight configuration/estimation, which is not fully attacker-controlled but can be influenced by message construction (e.g., a `Transact` with a large declared `require_weight_at_most`); (2) the attacker (or unrelated third parties) must be able to push at least `MaxStale` further pages through the *same* per-origin queue before anyone calls `execute_overweight` - this is plausible since sending cheap repeated XCM through `pallet_xcm::send` from a signed account is a normal, permissionless extrinsic path, and message-queue's `MaxStale`/`ServiceWeight` are runtime-configured constants that a knowledgeable attacker can budget against. This is a race rather than a guaranteed win in every runtime configuration, but it is fully reachable through routine, unprivileged extrinsic/XCM usage and does not require exploiting a missing signature/origin check - it is a logic/lifecycle gap between "manual overweight execution" and "automatic page reaping."

### Recommendation
`do_reap_page` (and the staleness bookkeeping that feeds it) should refuse to reap a page while it still contains any entry referenced by the `Overweight` storage map that has not been executed via `execute_overweight`/`do_execute_overweight_inner`, or alternatively `execute_overweight` should be triggered/forced (or the message re-enqueued/refunded) before such a page can be counted as stale. At minimum, the pallet should expose a way to detect/alert when a permanently-overweight message is about to be reaped so integrators (e.g., XCM asset-transactor logic) can react before funds become unbacked.

### Proof of Concept
xcm-emulator/integration test plan:
1. Configure a destination parachain's `MessageQueue` with small `ServiceWeight` and small `MaxStale`.
2. From the source chain, execute a reserve-transfer/teleport that debits/reserves assets and sends an XCM to the destination containing `WithdrawAsset`+`BuyExecution`+`DepositAsset` (or `Transact`) crafted so it exceeds `ServiceWeight` at the destination (permanently overweight).
3. Assert `Event::OverweightEnqueued` (or equivalent) is emitted at destination and total asset supply constant is now source-decreased/destination-unchanged.
4. Without calling `execute_overweight`, use a signed, unprivileged account to call `pallet_xcm::send` repeatedly (or otherwise enqueue unrelated messages into the same origin's queue) until `MaxStale`+N pages have been serviced/reaped in that queue.
5. Attempt `MessageQueue::execute_overweight(origin, page_index, message_index, weight_limit)` for the original message and assert it now fails with `Error::NoPage`/`Error::NoMessage` (data gone).
6. Assert the destination account's balance was never credited and the source chain's debited amount is unrecoverable — total cross-chain asset supply is permanently reduced, proving the conservation invariant is broken. [1](#0-0)

### Citations

**File:** substrate/frame/message-queue/src/lib.rs (L49-66)
```rust
//! **Message Execution**
//!
//! Executing a message is offloaded to the [`Config::MessageProcessor`] which contains the actual
//! logic of how to handle the message since they are blobs. Storage changes are not rolled back on
//! error.
//!
//! A failed message can be temporarily or permanently overweight. The pallet will perpetually try
//! to execute a temporarily overweight message. A permanently overweight message is skipped and
//! must be executed manually.
//!
//! **Reentrancy**
//!
//! This pallet has two entry points for executing (possibly recursive) logic;
//! [`Pallet::service_queues`] and [`Pallet::execute_overweight`]. Both entry points are guarded by
//! the same mutex to error on reentrancy. The only functions that are explicitly **allowed** to be
//! called by a message processor are: [`Pallet::enqueue_message`] and
//! [`Pallet::enqueue_messages`]. All other functions are forbidden and error with
//! [`Error::RecursiveDisallowed`].
```
