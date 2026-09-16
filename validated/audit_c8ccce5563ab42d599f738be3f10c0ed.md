## Analysis Result [1](#0-0) 

### Title
Missing fee-commitment invalidation lets a GetRequest's relayer fee be paid twice (delivery + timeout) - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatchIncoming(GetResponse, address)` pays the relayer fee out of `_requestCommitments[commitment].fee` on successful delivery but never deletes that record, unlike every other consuming path (`dispatchTimeOut`) which explicitly deletes it "for replay protection." This leaves a stale `FeeMetadata` entry that a later, otherwise-legitimate timeout proof can consume again.

### Finding Description
`dispatchIncoming(GetResponse)` reads and pays out the escrowed fee without freeing the record: [2](#0-1) 

Contrast this with both `dispatchTimeOut` overloads, which explicitly `delete _requestCommitments[commitment]` before paying, precisely to prevent the same commitment being consumed twice: [3](#0-2) [4](#0-3) 

`HandlerV2.handleGetRequestTimeouts` gates the timeout path only on (a) `request.timeout() > state.timestamp` and (b) a non-membership proof of a `ResponseReceipts` key **on the destination chain's own trie**: [5](#0-4) 

Because a `GetRequest` answered via `dispatchIncoming(GetResponse)` on the EVM **source** host writes nothing to the destination chain's `ResponseReceipts`, that non-membership proof remains valid indefinitely for a commitment whose response was already delivered on the source. The only guard against reprocessing the same commitment on the source side is `host.requestCommitments(commitment).sender == address(0)` — which stays non-zero forever because `dispatchIncoming(GetResponse)` never clears it. This is the classic "consume without freeing" pattern behind CVE-2023-5472's use-after-free class: a resource is logically finished with (the fee has been paid to the relayer) but the reference to it is never invalidated, so it is reachable and reusable from a second, independently-authorized code path.

### Impact Explanation
A relayer (or anyone paying for a valid timeout proof) can:
1. Deliver a legitimate `GetResponse` through `handleGetResponses`, which pays the escrowed fee to the relayer (`EvmHost.sol:842-845`).
2. Later obtain a non-membership storage proof for the same request from the destination chain (trivially available since that chain never wrote anything about this GET in the first place) and submit it through `handleGetRequestTimeouts`.
3. `dispatchTimeOut(GetRequestTimeout, ...)` re-reads the still-present `FeeMetadata` and refunds the same fee a second time to `meta.sender` (`EvmHost.sol:856-877`).

The result is a double payout of the same escrowed fee out of the host's fee-token balance — a concrete, permanent drain of protocol/user funds reachable from a single relayed proof, matching the "concrete theft" / "unbacked payout" bar in the validation rules.

### Likelihood Explanation
High: both code paths are permissionless (`handleGetResponses` and `handleGetRequestTimeouts` are callable by any relayer with valid proofs), and no additional privilege or race condition is required — the second call simply needs a normal Hyperbridge-issued non-membership proof for a state height after the declared timeout, which is always obtainable once time has passed, independent of whether the response was already delivered.

### Recommendation
In `EvmHost.dispatchIncoming(GetResponse memory response, address relayer)`, delete `_requestCommitments[commitment]` (or otherwise mark the commitment consumed) immediately after fee payout succeeds, mirroring the replay protection already implemented in both `dispatchTimeOut` overloads. Additionally, `handleGetRequestTimeouts` should verify the request has not already been answered on the source host before accepting a timeout proof for it.

### Proof of Concept
1. App on EVM chain A dispatches a `GetRequest` targeting chain B, escrowing `fee` in `_requestCommitments[commitment]`.
2. Relayer R1 delivers a valid `GetResponse` via `HandlerV2.handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse, R1)`; `fee` is transferred to R1; `_requestCommitments[commitment]` is left untouched (`EvmHost.sol:824-847`).
3. After `request.timeout()` has elapsed, relayer R2 (or R1 again) obtains a normal non-membership proof of the `ResponseReceipts` key for `commitment` from chain B's state trie (trivial, since chain B never records anything for this GET).
4. R2 submits this via `HandlerV2.handleGetRequestTimeouts`, which passes all checks (`EvmHost.sol` `requestCommitments(commitment).sender != 0`, non-membership proof valid, `request.timeout() > state.timestamp`) and calls `host.dispatchTimeOut(GetRequestTimeout, meta, commitment)`.
5. `EvmHost.dispatchTimeOut` pays `meta.fee` again — the same fee already paid in step 2 is refunded a second time, draining the host's fee-token reserve.

**Uncertainty note:** I could not fully verify, from the indexed portions of the repository, whether the substrate-side `pallet-ismp` `ResponseReceipts` child-trie entry (`modules/pallets/ismp/src/child_trie.rs`) is ever populated for a raw storage-read `GetRequest` answered by relayer-supplied proofs (as opposed to a module-routed response). If it is populated in some flow I did not locate, the non-membership proof in step 3 would fail and this exact double-payment would not be reachable. Given index size limits, some file contents may not be available; a full Devin session with complete repository access would be needed to conclusively trace all `GetRequest`/`ResponseReceipts` write sites on the substrate side and confirm end-to-end exploitability.

### Citations

**File:** evm/src/core/EvmHost.sol (L820-847)
```text
    /**
     * @dev Dispatch an incoming GET response to source module
     * @param response - get response
     */
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

**File:** evm/src/core/EvmHost.sol (L885-906)
```text
    function dispatchTimeOut(
        PostRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onPostRequestTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit PostRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** evm/src/core/HandlerV2.sol (L293-321)
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
    }
```
