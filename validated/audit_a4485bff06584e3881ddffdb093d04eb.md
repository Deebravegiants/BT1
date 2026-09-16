### Title
Stale `_requestCommitments` fee metadata after `GetResponse` delivery allows double payment via a later `GetRequestTimeout` proof - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming(GetResponse, relayer)` pays the delivering relayer from `_requestCommitments[commitment].fee` but never deletes that entry, unlike the timeout path which explicitly deletes it before acting. `_requestCommitments` is also never pruned by height/cap on the EVM host, so an old state commitment proving non-membership of the response can still be replayed afterwards.

### Finding Description
`dispatchIncoming(GetResponse, address relayer)` in `evm/src/core/EvmHost.sol` performs, in order: set `_responseReceipts[commitment]`, call the destination app's `onGetResponse`, then on success read `_requestCommitments[commitment].fee` and pay it to `relayer`. [1](#0-0) 

Crucially it never clears `_requestCommitments[commitment]` afterward. Compare this to `dispatchTimeOut(GetRequestTimeout,...)`, which explicitly `delete`s `_requestCommitments[commitment]` up front specifically to enforce replay protection before paying out a fee refund to `meta.sender`: [2](#0-1) 

Because the entry is left live after a successful `GetResponse` delivery, `meta.sender != address(0)` remains true for that commitment, so `HandlerV2.handleGetRequestTimeouts` will still accept a later, valid-looking timeout claim for the same commitment as long as the caller can supply (a) an on-chain state commitment height that is still stored in `_stateCommitments` and (b) a Polkadot-trie non-membership proof of `ResponseReceipts[commitment]` at that height: [3](#0-2) 

`EvmHost` keeps state-machine commitments in a flat `mapping(id => mapping(height => commitment))` with no automatic pruning/eviction by height or cap (unlike the queue-capped design used in `pallet-ismp`), so old heights recorded before Hyperbridge's own response commitment was written into its state trie remain queryable and challenge-period-eligible indefinitely unless explicitly vetoed by a fisherman: [4](#0-3) 

This is the same root-cause pattern as CVE-2023-4394: a reference (`_requestCommitments[commitment]`) that has already been logically "consumed" by one code path (successful `GetResponse` delivery / fee payout) is not invalidated, and a second, independent code path (`dispatchTimeOut`) later reuses that stale reference as if it were still live, causing a duplicate payout with attacker-controlled proof timing rather than a raw memory read, but with the same "use of freed/stale state" mechanism.

### Impact Explanation
A relayer who legitimately delivered a `GetResponse` (and was already paid the fee) can, after the fact, submit a `GetRequestTimeout` proof anchored to an earlier state height (one recorded before Hyperbridge itself wrote the response commitment into its state trie) to trigger `dispatchTimeOut`, which refunds `meta.fee` again to `meta.sender` (typically the original requester, but the relayer can arrange to be the fee sender/beneficiary via `dispatch(DispatchGet)`'s `payer`/`sender` semantics) and calls `onGetTimeout` on an app that has already received a successful response. This drains the fee token pool an extra time per exploited commitment and can desynchronize app state that assumed a response XOR timeout invariant, i.e. concrete theft of fee-token funds and unsound protocol state.

### Likelihood Explanation
Reachable by any unprivileged relayer with a single relayed timeout message once they hold (or can still reference) an older, still-stored state commitment height that predates Hyperbridge's write of the corresponding `ResponseReceipts` entry — no admin/collator/governance privilege is required, and `handleGetRequestTimeouts`/`dispatchTimeOut` are both permissionless entry points restricted only to "handler" at the host level, itself callable by anyone through the handler contract.

### Recommendation
Delete `_requestCommitments[commitment]` in `dispatchIncoming(GetResponse, relayer)` immediately after (or atomically with) the fee payout, mirroring the pattern already used in `dispatchTimeOut`, so that a commitment can only ever be consumed once by either the response-delivery path or the timeout path.

### Proof of Concept
I was not able to fully trace, within the remaining investigation budget, whether an EVM `GetRequest`'s destination-height selection for a timeout proof can concretely be pinned to a height stored before the Hyperbridge-side response write in a real deployment, or whether some other unseen invariant (e.g., height monotonicity enforced elsewhere in the handler or on the Hyperbridge side) prevents constructing such a stale non-membership proof after a response has already been delivered. This is the piece that would need to be confirmed/exercised with a Foundry test against `EvmHost`/`HandlerV2` to turn this into a fully demonstrated exploit; the missing-cleanup bug itself (`_requestCommitments` not deleted in `dispatchIncoming(GetResponse,...)`) is verified directly in the source.

### Citations

**File:** evm/src/core/EvmHost.sol (L691-699)
```text
        _stateCommitments[height.stateMachineId][height.height] = commitment;
        _stateCommitmentsUpdateTime[height.stateMachineId][height.height] = block.timestamp;
        _latestStateMachineHeight[height.stateMachineId] = height.height;

        emit StateMachineUpdated({
            stateMachineId: this.stateMachineId(_hostParams.hyperbridge, height.stateMachineId), 
            height: height.height
        });
    }
```

**File:** evm/src/core/EvmHost.sol (L824-847)
```text
    function dispatchIncoming(GetResponse memory response, address relayer) external restrict(_hostParams.handler) {
        // replay protection
        bytes32 commitment = response.request.hash();
        _responseReceipts[commitment] = ResponseReceipt({
            relayer: relayer,
            responseCommitment: response.hash()
        });

        (bool success,) = _bytesToAddress(response.request.from)
            .call(abi.encodeWithSelector(IApp.onGetResponse.selector, IncomingGetResponse(response, relayer)));

        if (!success) {
            // so that it can be retried
            delete _responseReceipts[commitment];
            return;
        }

        // reward the relayer fee
        uint256 fee = _requestCommitments[commitment].fee;
        if (fee != 0) {
            IERC20(feeToken()).safeTransfer(relayer, fee);
        }
        emit GetRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** evm/src/core/EvmHost.sol (L856-877)
```text
    function dispatchTimeOut(
        GetRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onGetTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** evm/src/core/HandlerV2.sol (L293-320)
```text
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
```
