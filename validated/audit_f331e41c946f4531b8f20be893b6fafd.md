This confirms the mechanism: `RequestReceipts[commitment]` recorded on the destination chain by `EvmHost.dispatchIncoming` [1](#0-0)  is later used as the on-chain attribution of "who delivered this message," and that address is what gets paid the delivery/relayer reward via `accumulate_fees` and the `OutboundRequestDeliveryClaim` pipeline [2](#0-1) [3](#0-2) . This is the exact reward-attribution primitive that an out-of-gas front-run can hijack, mirroring the Futureswap `instantWithdraw` bug class (reserve state written, real action deferred/failed).

### Title
Gas-griefing front-run of `HyperbridgeLzEndpoint.onAccept` lets an attacker steal the destination delivery-receipt (and its relayer reward) while deferring actual message execution — (File: `sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol`)

### Summary
`EvmHost.dispatchIncoming` writes `_requestReceipts[commitment] = relayer` **before** calling the destination module's `onAccept`, and only rolls that write back if the low-level `.call` to `onAccept` itself reverts [4](#0-3) . `HyperbridgeLzEndpoint.onAccept` wraps its actual payload delivery (`lzReceive`) in a `try/catch` specifically so that a failing/expensive OApp callback does **not** revert `onAccept` [5](#0-4) . Combining these two designs, an attacker can front-run the honest relayer's `handlePostRequests` call with the identical proof/calldata but a gas limit tuned so that `lzReceive` runs out of gas — `onAccept` still returns successfully (the `catch` block executes, storing the payload for later retry), so `EvmHost` permanently records the attacker as the delivering relayer in `RequestReceipts[commitment]`, and the honest relayer's transaction reverts with `DuplicateMessage`.

### Finding Description
1. A relayer calls `HandlerV2.handlePostRequests`, which verifies the MMR/consensus proof and calls `host.dispatchIncoming(request, msg.sender)` [6](#0-5) .
2. `EvmHost.dispatchIncoming` immediately writes the request receipt for `commitment`, then performs a low-level `.call` to `IApp.onAccept` [7](#0-6) . The receipt is deleted only if that call itself reverts (`success == false`) [8](#0-7) .
3. For `HyperbridgeLzEndpoint`, `onAccept` deliberately swallows a failing `lzReceive` inside a `try/catch` so the outer `onAccept` call never reverts, on the theory that a "deterministic revert…does not revert `onAccept`" [5](#0-4) . This reasoning does not distinguish a deterministic application revert from an attacker-induced out-of-gas failure: Solidity's `try/catch` also catches out-of-gas failures inside the callee as long as the caller retains enough gas (the classic 63/64th-gas EIP-150 pattern) to execute the `catch` block.
4. An attacker who observes the honest relayer's `handlePostRequests(proof, request)` transaction in the mempool can resubmit the exact same calldata with a higher gas price but a gas limit precisely calibrated so that `lzReceive`'s execution runs out of gas, while enough gas remains for the `catch` block (writing `_inboundPayloadHashes` and emitting `InboundPayloadStored`) and for `EvmHost.dispatchIncoming`'s post-call bookkeeping (`emit PostRequestHandled`).
5. Because `onAccept` does not revert, `EvmHost` keeps `_requestReceipts[commitment] = attacker` permanently. The honest relayer's original transaction then reverts with `DuplicateMessage` when it re-checks `host.requestReceipts(commitment) != address(0)` [9](#0-8) .
6. `RequestReceipts[commitment]` on the destination chain is exactly the value that the relayer-fee accumulation and outbound-delivery-reward pipelines read to attribute (and pay) the delivery reward to a relayer address [2](#0-1) [10](#0-9) . The attacker is therefore credited as "the relayer that delivered this message" and can later claim the associated fee/reward, while the actual cross-chain payload delivery is deferred and must be completed later by anyone calling `retryPayload` [11](#0-10) .

This is structurally the same bug class as the Futureswap report: the attacker copies a legitimate message/proof visible in the mempool, submits it with a crafted gas limit to force an internal call to fail via out-of-gas while the outer transaction "succeeds," and this reserves/claims state (here, the delivery-receipt/relayer-fee attribution) that should only be granted for a real, complete delivery, while griefing the honest submitter's transaction.

### Impact Explanation
The attacker can systematically steal relayer delivery rewards for `HyperbridgeLzEndpoint` messages without doing any of the real work of delivering the payload, and can repeatedly grief the honest relayer network (front-running every delivery attempt), degrading the reliability of the LayerZero-over-Hyperbridge route and misdirecting fee/reward accounting to an address that did not perform the delivery. Because delivery to the OApp is deferred (via `retryPayload`), this is not permanent freezing of the message itself, but it is unauthorized/forged attribution of "delivery" for reward-accounting purposes and a denial-of-service against the honest relayer's transaction — impacting the correctness of "relayer fee and reward accounting," an explicitly in-scope category.

### Likelihood Explanation
Exploitation requires only mempool visibility of a `handlePostRequests` transaction (a normal, public, permissionless relayer action) and the ability to calibrate a gas limit so that `lzReceive` fails from out-of-gas while `onAccept`'s `catch` block and `EvmHost`'s bookkeeping still complete — a standard, well understood Solidity gas-griefing technique (63/64-gas rule) requiring no special privileges, matching the "unprivileged relayer" reachability required by scope.

### Recommendation
Do not treat an out-of-gas failure inside the `try` block the same as a deterministic application revert. Either:
- Explicitly forward a bounded, sufficient amount of gas to `lzReceive` and require the caller (or `EvmHost`) to supply proof that enough gas was available for the full call (e.g., check `gasleft()` against a known minimum before entering the `try`, reverting `onAccept` entirely if insufficient gas was supplied so the whole delivery attempt — including the receipt write — is rolled back and can be retried by a relayer with adequate gas), or
- Decouple the "receipt/relayer credited" attribution from raw `onAccept` success by having `EvmHost` (or the app) distinguish "delivered and processed" from "delivered but deferred," and only pay/attribute the delivery reward once the deferred payload is actually executed via `retryPayload`.

### Proof of Concept
1. Dispatch a legitimate LayerZero-over-Hyperbridge message so that a `PostRequest` targeting `HyperbridgeLzEndpoint` becomes finalized and provable via BEEFY/MMR proof.
2. Wait for a relayer to broadcast `HandlerV2.handlePostRequests(host, message)` in the mempool.
3. Copy the exact calldata and resubmit as `attackerTx` with a higher gas price and a gas limit `G` chosen such that: `G` is enough for MMR/consensus verification and `EvmHost.dispatchIncoming`'s receipt write plus the `onAccept` nonce-check/advance [12](#0-11) , but insufficient for `lzReceive` to complete its logic on the destination OApp, while still leaving the 1/64th gas stipend for the `catch` block [13](#0-12) .
4. `attackerTx` lands first: `_requestReceipts[commitment]` is permanently set to the attacker's address (`emit PostRequestHandled`), and `_inboundPayloadHashes[...]` stores the pending payload for later retry.
5. The honest relayer's original `handlePostRequests` transaction then reverts with `DuplicateMessage` because `host.requestReceipts(commitment) != address(0)`.
6. The attacker (recorded as the "delivering relayer" in `RequestReceipts[commitment]`) later submits an `accumulate_fees`/`claim_outbound_request_delivery_reward`-style claim using this receipt to collect the delivery reward, despite never having actually executed `lzReceive` on the destination OApp.

### Citations

**File:** evm/src/core/EvmHost.sol (L794-818)
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
    }
```

**File:** modules/pallets/relayer/src/outbound_request.rs (L16-25)
```rust
//! Outbound request delivery rewards.
//!
//! Relayers that deliver a hyperbridge-originated request (host-executive,
//! intents-coprocessor, token-governor, the relayer pallet's own withdrawal
//! path, etc.) to a destination earn the per-`module_id`
//! [`crate::pallet::OutboundRequestDeliveryReward`]. The on-chain attribution
//! lives in the destination's `RequestReceipts[commitment]` slot, written by
//! the destination's ISMP host the first time the request is delivered. This
//! module proves that slot against Hyperbridge's stored state commitment for
//! the destination and transfers the configured reward.
```

**File:** modules/pallets/relayer/src/accumulate.rs (L76-92)
```rust
		let source_keys = Self::source_fee_commitment_keys(
			state_machine,
			&*source_sm,
			&withdrawal_proof.commitments,
		);
		let dest_keys = dest_sm.receipts_state_trie_key(withdrawal_proof.commitments.clone());

		let source_result = Self::verify_withdrawal_proof(
			&*source_sm,
			&withdrawal_proof.source_proof,
			source_keys.clone(),
		)?;
		let dest_result = Self::verify_withdrawal_proof(
			&*dest_sm,
			&withdrawal_proof.dest_proof,
			dest_keys.clone(),
		)?;
```

**File:** modules/pallets/relayer/src/accumulate.rs (L317-336)
```rust
impl<T: Config> Pallet<T> {
	/// Decode a proven `RequestReceipts[commitment]` value into the delivering
	/// relayer's bytes. EVM stores the address RLP encoded, substrate stores the
	/// signer bytes or a signature to recover the signer from. Used by both fee
	/// accumulation and the outbound request delivery claim.
	pub fn decode_receipt_relayer(state_id: StateMachine, raw: &[u8]) -> Result<Vec<u8>, Error<T>> {
		match state_id {
			s if crate::is_pharos(&s) =>
				if raw.len() == 32 {
					Ok(Address::from_slice(&raw[12..]).0.to_vec())
				} else {
					Err(Error::<T>::ProofValidationError)
				},
			s if s.is_evm() => {
				use alloy_rlp::Decodable;
				Ok(Address::decode(&mut &*raw)
					.map_err(|_| Error::<T>::ProofValidationError)?
					.0
					.to_vec())
			},
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L375-382)
```text
        // Validate and advance the nonce. The nonce is committed BEFORE (and independently of)
        // OApp execution: a reverting `lzReceive` must not roll back this write. Otherwise the
        // message would be retried forever at the same nonce and every later nonce would be
        // permanently rejected, bricking the (receiver, srcEid, sender) channel.
        address receiverAddr = address(uint160(uint256(receiver)));
        uint64 expectedNonce = _inboundNonce[receiverAddr][srcEid][sender] + 1;
        if (nonce != expectedNonce) revert InvalidNonce(expectedNonce, nonce);
        _inboundNonce[receiverAddr][srcEid][sender] = nonce;
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L384-396)
```text
        // Deliver to the OApp. Isolate the external call so a deterministic revert (zero
        // recipient, over-cap mint, blocklisted recipient, malformed payload, paused OApp, etc.)
        // does not revert `onAccept`. On failure the payload is retained for later retry/recovery
        // via retryPayload/clear/skip/nilify/burn.
        Origin memory origin = Origin({srcEid: srcEid, sender: sender, nonce: nonce});
        try ILayerZeroReceiver(receiverAddr).lzReceive(origin, guid, message, address(0), "") {
            // delivered successfully
        } catch {
            bytes32 payloadHash = keccak256(abi.encode(guid, message));
            _inboundPayloadHashes[receiverAddr][srcEid][sender][nonce] = payloadHash;
            emit InboundPayloadStored(receiverAddr, srcEid, sender, nonce, payloadHash);
        }
    }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L406-433)
```text
     * @notice Retries an inbound delivery whose OApp `lzReceive` previously reverted in {onAccept}.
     * @dev Mirrors {onAccept}'s direct call to the OApp (the adapter is the caller, so the OApp's
     * `onlyEndpoint` check still passes). Permissionless: anyone may push a stuck payload through
     * once it is executable again. On success the stored payload hash is cleared; if delivery
     * reverts again the whole call reverts and the payload remains recoverable.
     * @param receiver The destination OApp
     * @param origin The (srcEid, sender, nonce) of the stored payload
     * @param guid The original message guid
     * @param message The original message payload (must match the stored hash)
     */
    function retryPayload(
        address receiver,
        Origin calldata origin,
        bytes32 guid,
        bytes calldata message
    ) external payable {
        bytes32 stored = _inboundPayloadHashes[receiver][origin.srcEid][origin.sender][origin.nonce];
        if (stored == bytes32(0) || stored == NIL_PAYLOAD_HASH || stored != keccak256(abi.encode(guid, message))) {
            revert InvalidPayloadHash();
        }

        // Clear first; if the retry reverts, this deletion rolls back with the rest of the tx and
        // the payload remains recoverable.
        delete _inboundPayloadHashes[receiver][origin.srcEid][origin.sender][origin.nonce];

        ILayerZeroReceiver(receiver).lzReceive{value: msg.value}(origin, guid, message, msg.sender, "");
        emit InboundPayloadResolved(receiver, origin.srcEid, origin.sender, origin.nonce);
    }
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L7-13)
```markdown
1. A relayer calls `HandlerV2.handlePostRequests` (or `handleGetResponses`). After proof
   verification the handler calls `host.dispatchIncoming(request, _msgSender())`. `_msgSender()` is
   plain `msg.sender`; the handler has no trusted forwarder.
2. `EvmHost.dispatchIncoming` (restricted to the handler) writes a receipt for the request
   commitment, then low-level calls the module with `IApp.onAccept(IncomingPostRequest(request,
   relayer))`. If that call fails the host deletes the receipt and returns without reverting, so the
   rest of the batch proceeds and the message stays deliverable.
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L295-307)
```text
```solidity lineNumbers=159 title="hyperbridge/evm/src/core/HandlerV2.sol"
for (uint256 i = 0; i < requestsLen; ++i) {
    PostRequestLeaf memory leaf = request.requests[i];
    // check destination
    if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
    // check time-out
    if (timestamp >= leaf.request.timeout()) revert MessageTimedOut(); // [!code hl]
    // duplicate request?
    bytes32 commitment = leaf.request.hash();
    if (host.requestReceipts(commitment) != address(0)) revert DuplicateMessage();

    leaves[i] = MmrLeaf(leaf.kIndex, leaf.index, commitment);
}
```
