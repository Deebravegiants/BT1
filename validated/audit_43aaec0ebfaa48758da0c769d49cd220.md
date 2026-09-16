### Title
Batch handler functions in `HandlerV2` revert entirely when a single leaf becomes stale, delaying delivery of all other valid messages in the batch - (File: `evm/src/core/HandlerV2.sol`)

### Summary
`HandlerV2.handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts` and `handleGetRequestTimeouts` each process a batch of leaves that share a single MMR/state proof. Any relayer can permissionlessly submit these batches, and `IHandlerV2.batchCall` additionally lets a relayer bundle several handler calls (e.g. consensus update + multiple post-request batches) into one atomic transaction. If, between the time a relayer builds the batch/proof and the time the transaction is mined, any single leaf in the batch becomes invalid (already delivered by a competing relayer, timed out, etc.), the `require`/`revert` check for that one leaf reverts the *entire* transaction, causing every other still-valid message in the same batch to fail delivery and be delayed, exactly analogous to the Notional `_rebalanceCurrency` finding where one healthy currency reverted the whole rebalance of several unhealthy ones.

### Finding Description
`handlePostRequests` iterates over `request.requests` twice: first to validate destination/timeout and build MMR leaves, then (after verifying the aggregate merkle proof) to check for duplicates and dispatch: [1](#0-0) 

The duplicate check `if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();` at line 207 reverts the whole call the instant any single leaf in the batch has already been delivered (for example, by a competing relayer, or by the beneficiary self-relaying the same request). Because all leaves in the call share one merkle multiproof verified at lines 199-202, the transaction cannot simply skip the stale leaf — the entire batch aborts, and none of the other, still-pending requests are delivered in that transaction.

The same check-batch/verify-batch/dispatch-batch pattern with an all-or-nothing revert exists in the sibling functions: [2](#0-1) [3](#0-2) 

This is compounded by `batchCall`, which permissionlessly bundles multiple handler invocations (e.g. a consensus update plus one or more `handlePostRequests` calls) into a single atomic transaction via `delegatecall`, explicitly reverting the entire batch if any inner call fails: [4](#0-3) 

The off-chain relayer (`tesseract`) builds exactly this kind of multi-message batch and submits it as one `batchCall` transaction: [5](#0-4) 

Because delivery is permissionless (any relayer, or the request's own beneficiary, may self-relay per the documented self-relay flow), it is a normal, expected occurrence — not an attack precondition — that two parties race to deliver the same request commitment. When the relayer's batch was built with stale state (any of the timeout/duplicate/height conditions changed between proof generation and mining, which is unavoidable given block-production latency and multiple concurrent relayers), the entire multi-message transaction reverts, and the relayer must detect the failure, strip the stale leaf, rebuild the merkle proof and consensus intermediates, and resubmit — delaying delivery of the remaining, still-valid messages by at least one additional block/round-trip.

### Impact Explanation
Under this scenario, message delivery for otherwise healthy, still-pending, possibly time-sensitive requests (which may be close to their `timeoutTimestamp`) is delayed because they are bundled in the same atomic call as a stale leaf. Repeated occurrences under normal multi-relayer conditions can push affected requests past their timeout window entirely, denying them delivery and forcing the timeout/refund path instead of successful execution — a route that becomes unable to deliver messages within its intended window. This matches the accepted impact class of "a route unable to deliver messages."

### Likelihood Explanation
Likelihood is non-trivial and does not require any malicious actor: delivery is permissionless by design (`notFrozen` modifier only, no access control) and self-relay is an explicitly documented use case, so multiple parties racing to deliver the same commitment is expected protocol behavior, not an edge case. Any relayer batching more than one request/leaf (which `tesseract` does by default via `submit_batch_messages`/`batchCall` for batches ≥2) is exposed every time a competing delivery lands first.

### Recommendation
For the batched handler functions, avoid all-or-nothing reversion on a per-leaf basis:
- Perform the duplicate/timeout checks for each leaf before it is added to the merkle-proof leaf set, and instead of reverting the whole call, skip that leaf (excluding it from both the proof verification and the dispatch loop) while continuing to process the rest of the batch.
- Alternatively, expose a per-leaf try/catch style processing (already partially done at the Substrate `handlers::request` layer where failures are collected per-request rather than aborting the whole batch) so a stale leaf only fails its own entry: [6](#0-5) 
- For `IHandlerV2.batchCall`, consider offering a non-atomic variant (or documenting/encouraging relayers to size batches conservatively) so that a single stale inner call does not block delivery of unrelated messages bundled in the same transaction.

### Proof of Concept
1. Relayer A builds a `PostRequestMessage` batch containing leaves for requests `R1`, `R2`, `R3` (all currently un-delivered, non-timed-out) with the corresponding MMR multiproof, and submits it via `handlePostRequests` (optionally wrapped together with a consensus update inside `batchCall`).
2. Before Relayer A's transaction is mined, the beneficiary of `R2` self-relays `R2` directly (a documented, permissionless path), so `host.requestReceipts(hash(R2))` becomes non-zero.
3. Relayer A's transaction is mined: the first loop builds leaves for `R1, R2, R3` and the merkle proof verifies successfully; the second loop hits `R2` and reverts with `DuplicateMessage()` at `HandlerV2.sol:207`, aborting the entire call.
4. `R1` and `R3`, which were still valid and deliverable, are not delivered in this transaction. Relayer A must detect the revert, rebuild a new merkle proof excluding `R2`, and resubmit — delaying `R1` and `R3` by at least one additional round trip, with risk of eventual timeout if this repeats near the requests' `timeoutTimestamp`.

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

**File:** evm/src/core/HandlerV2.sol (L217-247)
```text
    function handleGetResponses(IHost host, GetResponseMessage calldata message) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(message.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 responsesLength = message.responses.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](responsesLength);

        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // don't check for timeouts because it's checked on Hyperbridge

            // known request? also serves as source check
            FeeMetadata memory meta = host.requestCommitments(leaf.response.request.hash());
            if (meta.sender == address(0)) revert UnknownMessage();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.response.hash());
        }

        bytes32 root = host.stateMachineCommitment(message.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, message.proof.multiproof, leaves, message.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // duplicate response?
            if (host.responseReceipts(leaf.response.request.hash()).relayer != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.response, _msgSender());
        }
    }
```

**File:** evm/src/core/HandlerV2.sol (L254-286)
```text
    function handlePostRequestTimeouts(IHost host, PostRequestTimeoutMessage calldata message)
        external
        notFrozen(host)
    {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
        uint256 timeoutsLength = message.timeouts.length;

        for (uint256 i = 0; i < timeoutsLength; ++i) {
            PostRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();

            // known request? also serves as source check
            bytes32 requestCommitment = request.hash();
            FeeMetadata memory meta = host.requestCommitments(requestCommitment);
            if (meta.sender == address(0)) revert UnknownMessage();

            bytes[] memory keys = new bytes[](1);
            keys[0] = bytes.concat(REQUEST_RECEIPTS_STORAGE_PREFIX, requestCommitment);

            // verify state trie non-membership proofs
            PolkadotTrie.StorageValue memory entry = PolkadotTrie.VerifyProof(state.stateRoot, message.proof, keys)[0];
            if (entry.value.length != 0) revert InvalidProof();

            host.dispatchTimeOut(PostRequestTimeout(request, _msgSender()), meta, requestCommitment);
        }
    }
```

**File:** tesseract/messaging/evm/src/tx.rs (L441-462)
```rust
/// Submit a full batch of ISMP messages as a single `IHandlerV2.batchCall` transaction.
///
/// One tx replaces what would otherwise be N separate txs (one per message),
/// cutting gas overhead and nonce management complexity. Atomic: if any
/// inner call reverts, the whole transaction reverts.
pub async fn submit_batch_messages(
	client: &EvmClient,
	messages: Vec<Message>,
) -> anyhow::Result<SubmitOutcome> {
	if messages.is_empty() {
		return Ok((BTreeSet::new(), Vec::new(), Vec::new()));
	}

	let handler_addr = Address::from_slice(&client.handler().await?.0);
	let from = Address::from_slice(&client.address);
	let gas_price = fetch_gas_price(client, false).await?;
	let chain_gas_limit = get_chain_gas_limit(client.state_machine);

	let inner_calls = build_batch_inner_calls(client, &messages).await?;
	let handler_v2 = HandlerV2Instance::new(handler_addr, client.signer.clone());
	let call = handler_v2.batchCall(inner_calls);
	let gas = call.estimate_gas().await.unwrap_or_else(|_| (chain_gas_limit * 8) / 10);
```

**File:** modules/ismp/core/src/handlers/request.rs (L95-133)
```rust
	let mut total_weights = Weight::zero();
	let result = msg
		.requests
		.into_iter()
		.map(|request| {
			let wrapped_req = Request::Post(request.clone());
			let mut lambda = || {
				let cb = router.module_for_id(request.to.clone())?;
				// Re-check the receipt right before dispatch. The up-front pass above
				// runs before any callback executes; a prior request's on_accept in
				// this same batch could have stored a receipt for this request
				// (directly or by re-entering the handler), and we must not invoke
				// on_accept a second time.
				if host.request_receipt(&wrapped_req).is_some() {
					Err(Error::DuplicateRequest { meta: wrapped_req.clone().into() })?
				}
				// Store request receipt to prevent reentrancy attack
				let signer = host.store_request_receipt(&wrapped_req, &msg.signer)?;
				let res = cb.on_accept(request.clone()).map(|weight| {
					total_weights.saturating_accrue(weight);

					let commitment = hash_request::<H>(&wrapped_req);
					Event::PostRequestHandled(RequestResponseHandled {
						commitment,
						relayer: signer,
					})
				});
				// Delete receipt if module callback failed so it can be timed out
				if res.is_err() {
					host.delete_request_receipt(&wrapped_req)?;
				}
				Ok(res)
			};

			let res = lambda().and_then(|res| res);
			res
		})
		.collect::<Vec<_>>();

```
