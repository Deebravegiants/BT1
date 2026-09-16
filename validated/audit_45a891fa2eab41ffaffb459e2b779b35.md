Found a strong analog. `HandlerV2.handlePostRequests` batches multiple independent POST requests into a single MMR-proof-verified call, but the per-item validity checks (`InvalidMessageDestination`, `MessageTimedOut`, `DuplicateMessage`) are *not* isolated per item — any single bad item reverts the whole batch, unlike the per-item dispatch step which is properly isolated via a low-level `.call`.Confirmed root cause. `HandlerV2.handlePostRequests` batches multiple independent `PostRequest`s under one MMR multiproof, and the pre-dispatch validity checks in the loop at [1](#0-0)  and the duplicate-check loop at [2](#0-1)  use plain `revert` statements that are not isolated per item, unlike the module-dispatch step in `EvmHost.dispatchIncoming` which deliberately uses a low-level `.call` with early-return-on-failure specifically "instead of reverting the entire batch" ( [3](#0-2) ). The relayer tooling packs multiple unrelated requests into one such batched call for gas efficiency ( [4](#0-3) , [5](#0-4) ), and `IHandlerV2.batchCall` further wraps this atomically, reverting the whole transaction on any single failure ( [6](#0-5) ).

### Title
Forced All-or-Nothing Reversion of Batched POST Request Deliveries on One Front-Runnable Item - (File: evm/src/core/HandlerV2.sol)

### Summary
`HandlerV2.handlePostRequests` proves and delivers an entire array of unrelated `PostRequest`s under a single MMR multiproof. Unlike the per-item module dispatch, which is deliberately isolated via a low-level `.call` in `EvmHost.dispatchIncoming` so a failing callback does not abort sibling requests, the request-level validity checks (`InvalidMessageDestination`, `MessageTimedOut`, `DuplicateMessage`) inside `handlePostRequests`'s two loops are plain `revert` statements that abort the *entire* call for the whole batch. This mirrors the reported Across bug class: an unprivileged party can force a fallback/failure path for many uninvolved participants because of one bad item that they don't control.

### Finding Description
In `handlePostRequests` [7](#0-6) :
1. The first loop checks `dest` and `timeout()` for every leaf in the batch and reverts the whole call on the first failing entry (`InvalidMessageDestination`, `MessageTimedOut`).
2. After the MMR multiproof is verified against the fixed set of leaves, the second loop checks `host.requestReceipts(leaf.request.hash()) != address(0)` and reverts with `DuplicateMessage` for the whole call if *any single* request in the batch was already delivered.

Because the MMR multiproof is generated for one specific fixed set of leaves (built off-chain by the relayer, e.g. `tesseract/messaging/messaging/src/retries.rs::batch_requests` and `tesseract/messaging/evm/src/tx.rs::build_batch_inner_calls`), the relayer cannot simply drop the "bad" leaf from the calldata and resubmit — doing so would invalidate the multiproof and require regenerating a fresh proof querying only the remaining commitments from Hyperbridge (a separate proof-query round trip), which is exactly the extra "execution overhead" complained about in the reported bug class.

This is compounded by `IHandlerV2.batchCall`, which the relayer's tx builder uses to bundle a `handleConsensus` call together with a `handlePostRequests` call into one atomic transaction (`tesseract/messaging/evm/src/tx.rs::build_batch_inner_calls`, `submit_batch_messages`): "Atomic, any failure reverts the entire batch" [6](#0-5) . A revert anywhere inside `handlePostRequests` therefore also unwinds the just-verified consensus update in the same transaction.

The protocol explicitly acknowledges the danger of exactly this pattern in `EvmHost.dispatchIncoming`, where a comment states the design intentionally avoids reverting a whole batch: "instead of reverting the entire batch, early return here" [8](#0-7) . That mitigation was applied only to the per-request module callback step, not to the pre-dispatch destination/timeout/duplicate checks that run earlier in the very same function.

### Impact Explanation
Any unprivileged actor watching the mempool (or simply racing) can front-run a batched `handlePostRequests`/`batchCall` transaction by delivering just one of its constituent commitments individually (a cheap, single-request `handlePostRequests` call, itself permissionless per the docs at `docs/content/developers/evm/api/ihandler.mdx`). When the victim's larger batch then lands, the `DuplicateMessage` check reverts the *entire* transaction, so every other legitimate, otherwise-valid, and possibly time-sensitive request bundled alongside it fails to be delivered in that attempt. This:
- Wastes the relayer's gas on the reverted transaction.
- Delays delivery of otherwise valid, non-conflicting requests — some of which may be close to their `timeout()` and could time out as a direct result of the forced delay, converting into "a route unable to deliver messages" for those unrelated requests.
- Can be leveraged as a repeatable, low-cost griefing tool by a malicious actor (no privilege required) against a chosen relayer's batches, since re-querying and rebuilding the multiproof after every griefed attempt is required, giving the attacker a persistent economic edge (attacker pays for one cheap single-item call; victim repeatedly pays for gas-heavy batch verification that reverts).

### Likelihood Explanation
Requires only a public mempool observation and enough gas to front-run a single-request delivery — no special privileges, keys, or governance access are needed. Batching (`batchCall`, multi-request `handlePostRequests`) is the standard relayer code path used for gas efficiency (`tesseract/messaging/evm/src/tx.rs`, `tesseract/messaging/messaging/src/retries.rs`), so batches of many pending requests bound for the same destination height are common in production, making the attack broadly applicable rather than a rare edge case.

### Recommendation
Isolate the duplicate/timeout/destination checks per-item the same way the module dispatch step already is: instead of `revert DuplicateMessage()` (and the destination/timeout checks) aborting the whole call, `continue`/skip that leaf (while still including it in the MMR leaf array for proof verification) and proceed to dispatch the remaining, valid requests. Alternatively, allow the relayer to submit a `try/catch`-style low-level self-call per request analogous to `EvmHost.dispatchIncoming`'s early return, so one already-delivered or timed-out request cannot block delivery of the rest of the batch. If keeping the `batchCall` atomic-revert semantics, document/support a fallback so callers can decode `BatchCallFailed(index, reason)` and automatically retry only the surviving requests without needing a full new proof query.

### Proof of Concept
1. Relayer A builds a `PostRequestMessage` batching commitments `[C1, C2, C3]` with one MMR multiproof (as done by `batch_requests` in `tesseract/messaging/messaging/src/retries.rs`) and submits it via `handler.handlePostRequests(host, msg)` or bundled inside `handler.batchCall([...])`.
2. Attacker observes A's pending transaction in the mempool, extracts `C2`'s `PostRequestLeaf`, and submits a minimal single-item `handlePostRequests` call delivering only `C2`, paying minimal gas, with higher priority fee so it lands first.
3. `host.requestReceipts(hash(C2))` is now non-zero.
4. A's original transaction executes: the first loop passes (destination/timeout fine), the multiproof verifies, but the second loop's `if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();` fires on `C2`, reverting the whole transaction — `C1` and `C3`, which were legitimate and undelivered, are not dispatched in this attempt, per [2](#0-1) .
5. Relayer A must re-query a fresh MMR proof excluding `C2` and resubmit, incurring extra round trips and gas, while `C1`/`C3` risk timing out if their `timeout()` is close.

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

**File:** evm/src/core/HandlerV2.sol (L181-210)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 requestsLen = request.requests.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](requestsLen);

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
        }

        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
    }
```

**File:** evm/src/core/EvmHost.sol (L794-817)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
```

**File:** tesseract/messaging/messaging/src/retries.rs (L317-340)
```rust
async fn batch_requests(
	ctx: &RetryContext,
	profitable: &[(PostRequest, Query)],
	height: StateMachineHeight,
) -> Result<Vec<Message>, anyhow::Error> {
	let dest_state_machine = ctx.dest.state_machine_id().state_id;
	let mut messages = vec![];

	for chunk in profitable.chunks(chunk_size(dest_state_machine)) {
		let (requests, queries): (Vec<_>, Vec<_>) = chunk.iter().cloned().unzip();
		let proof = ctx
			.hyperbridge
			.query_requests_proof(height.height, queries, dest_state_machine)
			.await?;

		messages.push(Message::Request(RequestMessage {
			requests,
			proof: Proof { height, proof },
			signer: ctx.dest.address(),
		}));
	}

	Ok(messages)
}
```

**File:** tesseract/messaging/evm/src/tx.rs (L298-315)
```rust
			Message::Request(msg) => {
				let (mmr_proof, leaf_indices) = decode_mmr_proof(&msg.proof.proof)?;
				let mut leaves: Vec<PostRequestLeaf> = msg
					.requests
					.iter()
					.zip(&leaf_indices)
					.map(|(post, &leaf_index)| PostRequestLeaf {
						request: post.clone().into(),
						index: AlloyU256::from(leaf_index),
					})
					.collect();
				leaves.sort_by_key(|l| l.index);
				let proof = build_solidity_proof(&mmr_proof, &msg.proof.height)?;
				let call = contract
					.handlePostRequests(ismp_host, PostRequestMessage { proof, requests: leaves });
				let gas = call.estimate_gas().await.unwrap_or_else(|_| chain_gas_limit / 4);
				(call.calldata().clone(), gas_with_buffer(gas))
			},
```
