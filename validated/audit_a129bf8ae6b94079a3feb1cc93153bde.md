This confirms the analog. `HandlerV2.batchCall` at [1](#0-0)  is explicitly documented and implemented as atomic — a single failed delegatecall reverts the whole batch. The relayer infra in `tesseract/messaging/evm/src/tx.rs` confirms this is the standard submission path for ≥2 messages, batching multiple `PostRequest`/`GetResponse`/`Consensus` handler calls into one `batchCall` transaction for gas savings, explicitly documented as "Atomic: if any inner call reverts, the whole transaction reverts."

### Title
Atomic `HandlerV2.batchCall` reverts entire relayer message batch when a single message becomes stale, delaying delivery of all other valid messages - (File: evm/src/core/HandlerV2.sol)

### Summary
Relayers batch multiple ISMP messages (`handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, `handleGetRequestTimeouts`, `handleConsensus`) into a single `HandlerV2.batchCall(bytes[])` transaction to save gas, as implemented by the relayer's `submit_batch_messages` in `tesseract/messaging/evm/src/tx.rs`. `batchCall` executes each encoded call via `delegatecall` and reverts the entire transaction if any single inner call fails, exactly mirroring the Notional `_rebalanceCurrency` bug class where a stale precondition check causes an entire otherwise-valid operation to revert.

### Finding Description
`HandlerV2.batchCall` iterates over an array of encoded calls and self-delegatecalls each one; if any single delegatecall fails, the whole function reverts via `BatchCallFailed`: [2](#0-1) 

The relayer explicitly relies on this atomic behavior to batch many independent, unrelated `PostRequest`/`GetResponse` deliveries plus consensus updates into a single transaction whenever it has ≥2 messages to submit, as documented in `submit_batch_messages`: [3](#0-2) 
and in `handle_message_submission`, which routes any batch of size ≥2 through this atomic path with no fallback: [4](#0-3) 

Individual handler functions each contain "up-front" checks over per-message state that can change between when a relayer queries/builds the batch and when the transaction actually lands on-chain — for example `handlePostRequests` reverts the entire call with `DuplicateMessage()` if even one leaf in the batch was already delivered by a competing relayer, and `MessageTimedOut()` if even one leaf's timeout elapsed while the transaction sat in the mempool: [5](#0-4) [6](#0-5) 

Because `batchCall` is atomic, a single stale/duplicate/timed-out message anywhere in the batch — which is entirely plausible in a competitive, permissionless relaying environment where multiple relayers race to deliver the same requests, or where mempool delay causes one message (out of potentially up to 100, per `chunk_size`) to cross its `timeout_timestamp` — causes the revert of *every other message* in that batch, even though those other messages were perfectly valid and deliverable at execution time. This is functionally identical to the Notional `_rebalanceCurrency` finding: a stale precondition check on one item (there, "is currency still unhealthy"; here, "is this message still un-delivered/not-timed-out") aborts a larger batched operation that also covers unrelated, still-valid items.

### Impact Explanation
When a batch reverts, delivery of every message it carried is delayed until a relayer rebuilds and resubmits a batch. In a live, permissionless network with multiple competing relayers (a normal, expected operating condition, not an adversarial one), this failure mode recurs continuously: the larger a batch is (up to 100 EVM messages per `chunk_size`, `tesseract/messaging/messaging/src/events.rs:424-429`), the higher the chance at least one message it contains is raced by another relayer or crosses its timeout mid-flight, causing the whole batch — including consensus updates riding along with it — to fail. Repeated reverts delay delivery of legitimate `PostRequest`/`GetResponse` messages across the bridge, which can cascade into cross-chain messages permanently timing out (since delivery is delayed towards their `timeout_timestamp`), token bridge transfers stalling, and intent/order fills being delayed, i.e. a route becoming intermittently unable to deliver messages promptly, which matches the "route unable to deliver messages" acceptance criterion.

### Likelihood Explanation
This is not a rare edge case: it is a structural consequence of favoring gas-efficient atomic batching in a permissionless, multi-relayer environment. Competing relayers racing the same `PostRequest`/`GetResponse` deliveries (economically incentivized, since relayers earn fees per delivered message) is the expected steady state, and the relayer's own retry logic (`tesseract/messaging/messaging/src/retries.rs`) already assumes and handles "already delivered by someone else" as a routine occurrence, confirming this race condition is common in practice, not hypothetical. Larger batches — the very case `batchCall` is optimized for — multiply the probability that at least one contained message becomes stale before inclusion.

### Recommendation
Do not let a single already-delivered/timed-out message abort delivery of the remaining valid messages in the same batch. Options:
- In `batchCall`, catch per-inner-call failures for known "already superseded" error selectors (`DuplicateMessage`, `MessageTimedOut`, `MessageNotTimedOut`, `UnknownMessage`) and skip/continue rather than reverting the whole batch, similar to `utility.forceBatch` semantics already used elsewhere in this codebase for phantom bids (`sdk/packages/sdk/src/chains/intentsCoprocessor.ts:961-964`, chosen specifically because `batch` "stops at the first failing call ... silently drop[ping] every bid after it").
- Alternatively, change `handlePostRequests`/`handleGetResponses`/`handlePostRequestTimeouts`/`handleGetRequestTimeouts` to skip (rather than revert on) individual leaves whose precondition no longer holds (duplicate/timed-out), continuing to process the rest of the batch, then emit a per-leaf result so relayers can prune only the stale entries on retry instead of resubmitting the entire batch.

### Proof of Concept
1. Relayer A and Relayer B both observe the same set of N pending `PostRequest`s destined for chain X and independently build batches containing overlapping messages `[m1 ... mN]`.
2. Relayer A's `submit_batch_messages` builds `batchCall([handlePostRequests(batch)])` (or a larger mixed batch including consensus + other requests) and submits it.
3. Relayer B's transaction for `m1` alone (or as part of a different batch) lands first, setting `host.requestReceipts(m1.hash())`.
4. Relayer A's transaction executes: `handlePostRequests` loops over all leaves in the batch; when it reaches `m1`, `host.requestReceipts(leaf.request.hash()) != address(0)` is true, so it reverts with `DuplicateMessage()` (`evm/src/core/HandlerV2.sol:207`).
5. Because this call happened via `delegatecall` inside `HandlerV2.batchCall`, the whole batch transaction reverts with `BatchCallFailed(index, reason)` (`evm/src/core/HandlerV2.sol:133`), so `m2 ... mN` — all still valid, undelivered, non-timed-out requests — fail to be delivered in this attempt and must wait for a subsequent resubmission cycle, delaying their delivery.

### Citations

**File:** evm/src/core/HandlerV2.sol (L123-135)
```text
    /**
     * @dev Process a batch of encoded handler calls in a single transaction.
     * Uses delegatecall to self so msg.sender is preserved and storage writes
     * happen in this contract's context. Atomic, any failure reverts the entire batch.
     * @param calls - array of ABI-encoded handler function calls
     */
    function batchCall(bytes[] memory calls) external {
        uint256 len = calls.length;
        for (uint256 i = 0; i < len; ++i) {
            (bool success, bytes memory returnData) = address(this).delegatecall(calls[i]);
            if (!success) revert BatchCallFailed(i, returnData);
        }
    }
```

**File:** evm/src/core/HandlerV2.sol (L190-196)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
```

**File:** evm/src/core/HandlerV2.sol (L204-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```

**File:** tesseract/messaging/evm/src/tx.rs (L441-446)
```rust
/// Submit a full batch of ISMP messages as a single `IHandlerV2.batchCall` transaction.
///
/// One tx replaces what would otherwise be N separate txs (one per message),
/// cutting gas overhead and nonce management complexity. Atomic: if any
/// inner call reverts, the whole transaction reverts.
pub async fn submit_batch_messages(
```

**File:** tesseract/messaging/evm/src/tx.rs (L718-728)
```rust
/// Top-level submission entry.
///
/// - **Batch of 1** (e.g. the mandatory-consensus-only chunks from the outbound rotation catch-up)
///   routes through the legacy per-message [`submit_messages`] path. Wrapping a single call in
///   `IHandlerV2.batchCall` adds a self-delegatecall frame with no upside, costs extra gas, and
///   makes the receipt harder to interpret downstream.
/// - **Batch of ≥2** dispatches through [`submit_batch_messages`], the atomic
///   `IHandlerV2.batchCall` path. Chains whose handler doesn't implement `IHandlerV2` will revert
///   at the handler address — the legacy serial-submit fallback is no longer supported for real
///   batches.
pub async fn handle_message_submission(
```
