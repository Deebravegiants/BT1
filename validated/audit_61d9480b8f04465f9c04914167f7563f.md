### Title
Frozen consensus client permanently blocks both request delivery and timeout processing, permanently locking escrowed intent funds - (File: `modules/ismp/core/src/handlers.rs`, `evm/src/core/HandlerV2.sol`)

### Summary
Hyperbridge's ISMP core exposes a permissionless `freeze_client` fraud-proof mechanism that, once triggered, makes a consensus client permanently unusable — mirroring the DSS `join.sol` `cage()` pattern from the referenced report, where a legitimate, irreversible admin/protocol action (`live = 0`) causes a downstream `require` to permanently block user withdrawals. In Hyperbridge, `validate_state_machine` gates both incoming message delivery *and* timeout processing behind the same `is_consensus_client_frozen` check, so once a client is frozen there is no path left to either deliver a pending request or time it out and reclaim escrowed funds.

### Finding Description
`validate_state_machine` is the shared preliminary check used before processing any request, response, or timeout tied to a given consensus client: [1](#0-0) 

It unconditionally calls `host.is_consensus_client_frozen(...)`, returning an error for *any* message type if the client has been frozen. Per the protocol documentation, freezing a consensus client is permanent and unrecoverable: [2](#0-1) 

This is corroborated by the test suite, which asserts that once frozen, even ordinary request messages hard-fail with `FrozenConsensusClient`: [3](#0-2) 

On the EVM side, the equivalent host-level freeze (`FrozenStatus.Incoming`/`All`) is enforced identically across *all* handler entrypoints via the shared `notFrozen(host)` modifier — including `handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, and `handleGetRequestTimeouts`: [4](#0-3) 

Because timeout processing is what triggers refunds for unfulfilled cross-chain intents (e.g., `IntentGatewayV2`'s escrow release via `withdraw`/`onGetResponse`), any user whose order was escrowed prior to the freeze has no way to either receive a fill or reclaim their tokens once the associated client/host is frozen — the exact "cage prevents withdrawals" shape from the reference report: a legitimate irreversible state transition (not attacker-controlled) permanently blocks the exit path for already-locked funds. [5](#0-4) 

### Impact Explanation
Any user funds escrowed in `IntentGatewayV2` (or any application relying on ISMP timeouts/responses through the affected consensus client) become permanently unrecoverable once that consensus client is frozen, since:
1. Delivery of the fill/response is blocked (`notFrozen`/`is_consensus_client_frozen`).
2. Timeout-triggered refunds are blocked by the identical check.

There is no admin override or unfreeze path for a frozen consensus client per the documented design, making this a permanent freezing of funds — satisfying the High/Critical bar.

### Likelihood Explanation
`freeze_client` is explicitly permissionless and intended to be triggered by "fishermen" upon detecting genuine consensus faults (double-signing, eclipse attacks), so it is a reachable, expected operational event rather than a hypothetical admin action. Any in-flight orders/requests routed through that consensus client at the time of freezing are affected, which is a realistic, non-adversarial scenario (analogous to Maker admins invoking `cage`).

### Recommendation
Provide an unlock/rescue path for funds already escrowed or committed before a consensus client freeze — e.g., allow timeout processing (and associated refunds) to bypass the frozen-client check once a request's `timeoutTimestamp` has passed, since a timeout does not depend on the validity of the frozen client's future state, only on the fact that the timeout deadline elapsed on the local host. Alternatively, provide a governance-gated emergency escrow-recovery function in `IntentGatewayV2` that does not depend on ISMP message delivery at all.

### Proof of Concept
1. A user calls `IntentGatewayV2.newOrder` (or equivalent), escrowing tokens for a cross-chain intent whose fill/refund path depends on state machine `X` served by consensus client `C`.
2. A fisherman detects a fault in `C` and submits a valid `FraudProofMessage` to `freeze_client`, which succeeds permissionlessly: [2](#0-1) .
3. The order's fill response (`RedeemEscrow`) can no longer be delivered because `validate_state_machine` rejects it via `is_consensus_client_frozen`.
4. Once the order's `timeoutTimestamp` passes, the user (or relayer) submits `handlePostRequestTimeouts`, but this call also routes through `notFrozen`/`validate_state_machine`, so it reverts.
5. The escrowed tokens in `_orders[commitment][token]` remain locked in `IntentGatewayV2` indefinitely, with no code path to release them.

### Citations

**File:** modules/ismp/core/src/handlers.rs (L116-147)
```rust
/// This function does the preliminary checks for a request or response message
/// - It ensures the consensus client is not frozen
/// - Checks for frozen state machine is deprecated and malicious state machine commitment will be
///   deleted instead
/// - Checks that the delay period configured for the state machine has elapsed.
pub fn validate_state_machine<H>(
	host: &H,
	proof_height: StateMachineHeight,
) -> Result<Box<dyn StateMachineClient>, Error>
where
	H: IsmpHost,
{
	// Ensure consensus client is not frozen
	let consensus_client_id = host.consensus_client_id(proof_height.id.consensus_state_id).ok_or(
		Error::ConsensusStateIdNotRecognized {
			consensus_state_id: proof_height.id.consensus_state_id,
		},
	)?;
	let consensus_client = host.consensus_client(consensus_client_id)?;
	// Ensure client is not frozen
	host.is_consensus_client_frozen(proof_height.id.consensus_state_id)?;

	// Ensure delay period has elapsed
	if !verify_delay_passed(host, &proof_height)? {
		return Err(Error::ChallengePeriodNotElapsed {
			state_machine_id: proof_height.id,
			current_time: host.timestamp(),
			update_time: host.state_machine_update_time(proof_height)?,
		});
	}

	consensus_client.state_machine(proof_height.id.state_id)
```

**File:** docs/content/protocol/ismp/consensus.mdx (L191-200)
```text
/// Freeze a consensus client by providing a valid consensus fault proof.
pub fn freeze_client<H>(host: &H, msg: FraudProofMessage) -> Result<(), Error>
where
    H: IsmpHost,
{
  // .. implementation details
}
```

The `freeze_client` method is used to prove the existence of a consensus fault to an onchain consensus client. This message will be sent by offchain parties, colloquially known as _fishermen_ when they detect the existence of two conflicting views of the network backed by consensus proofs. This may arise from double signing or eclipse attacks. The consensus client after successfully verifying the validity of the conflicting views of the network will go into a frozen state. In this state it can no longer process new consensus messages as well as new requests & responses. Frozen consensus clients cannot be unfrozen and a new consensus client must be initialized through the `create_client` method instead.
```

**File:** modules/ismp/testsuite/src/lib.rs (L176-208)
```rust
pub fn frozen_consensus_client_check<H: IsmpHost>(host: &H) -> Result<(), &'static str> {
	let intermediate_state = setup_mock_client(host);
	// Set the previous update time
	let challenge_period = host.challenge_period(intermediate_state.height.id).unwrap();
	let previous_update_time = host.timestamp() - (challenge_period * 2);
	host.store_consensus_update_time(mock_consensus_state_id(), previous_update_time)
		.unwrap();
	host.store_state_machine_update_time(intermediate_state.height, previous_update_time)
		.unwrap();
	host.freeze_consensus_client(mock_consensus_state_id()).unwrap();

	let post = PostRequest {
		source: intermediate_state.height.id.state_id,
		dest: host.host_state_machine(),
		nonce: 0,
		from: vec![0u8; 32],
		to: vec![0u8; 32],
		timeout_timestamp: 0,
		body: vec![0u8; 64],
	};
	let (signature, ..) = create_relayer_signer(vec![post.clone()].encode(), &[1u8; 32]);

	// Request message handling check
	let request_message = Message::Request(RequestMessage {
		requests: vec![post.clone()],
		proof: Proof { height: intermediate_state.height, proof: vec![] },
		signer: signature,
	});

	let res = handle_incoming_message(host, request_message).map_err(|e| e.downcast().unwrap());
	dbg!(&res);
	assert!(matches!(res, Err(ismp::error::Error::FrozenConsensusClient { .. })));
	Ok(())
```

**File:** evm/src/core/HandlerV2.sol (L181-322)
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

    /**
     * @dev check response proofs, message delay and timeouts, then dispatch get responses to modules
     * @param host - Ismp host
     * @param message - batch get responses
     */
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

    /**
     * @dev Checks the provided timed-out requests and their proofs, before dispatching them to their relevant destination modules
     * @param host - IsmpHost
     * @param message - batch post request timeouts
     */
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

    /**
     * @dev Check the provided Get request timeouts, then dispatch to modules
     * @param host - Ismp host
     * @param message - batch get request timeouts
     */
    function handleGetRequestTimeouts(IHost host, GetTimeoutMessage calldata message) external notFrozen(host) {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
        uint256 timeoutsLength = message.timeouts.length;

        for (uint256 i = 0; i < timeoutsLength; ++i) {
            GetRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();

            bytes32 commitment = request.hash();
            FeeMetadata memory meta = host.requestCommitments(commitment);
            if (meta.sender == address(0)) revert UnknownMessage();

            bytes[] memory keys = new bytes[](1);
            keys[0] = bytes.concat(RESPONSE_RECEIPTS_STORAGE_PREFIX, commitment);

            // verify state trie non-membership proofs
            PolkadotTrie.StorageValue memory entry = PolkadotTrie.VerifyProof(state.stateRoot, message.proof, keys)[0];
            if (entry.value.length != 0) revert InvalidProof();

            host.dispatchTimeOut(GetRequestTimeout(request, _msgSender()), meta, commitment);
        }
    }
}
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
        }
    }
```
