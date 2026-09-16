## Analysis

CVE-2019-15504 is a double-free bug class: a kernel resource gets released along two different code paths without one path invalidating the other, leading to a use of already-freed state. The analogous pattern in Hyperbridge's `EvmHost` is a fee-escrow that gets released twice: once when a GET response is delivered, and again when a stale/historical timeout proof is submitted for the same request, because the timeout path never checks the destination chain's own local delivery state before paying out.

### Title
Double payout of GET request relayer fee via stale non-membership timeout proof after response delivery - (File: evm/src/core/HandlerV2.sol / evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatchIncoming(GetResponse,...)` pays the escrowed fee out of `_requestCommitments[commitment].fee` when a GET response is delivered, but never deletes `_requestCommitments[commitment]` afterwards. `HandlerV2.handleGetRequestTimeouts` / `EvmHost.dispatchTimeOut(GetRequestTimeout,...)` later refunds the very same `_requestCommitments[commitment].fee` again if it can produce a non-membership proof of the response against *any* historically stored, still-queryable state commitment height — not necessarily the latest one. Because old heights are never purged from `_stateCommitments`, and the non-membership check is only validated against the remote hyperbridge trie (never against the EVM host's own `_responseReceipts`, which already recorded the delivery locally), the same fee can be paid out twice from two independent code paths.

### Finding Description
On response delivery: [1](#0-0) 

Note that `_requestCommitments[commitment]` is read for the fee but is **never deleted** here, unlike the POST path.

On timeout: [2](#0-1) 

`EvmHost.dispatchTimeOut(GetRequestTimeout,...)` (same replay-delete-then-refund pattern) is driven by `HandlerV2.handleGetRequestTimeouts`, which verifies a non-membership proof of the response receipt against `host.stateMachineCommitment(message.height)` for an attacker-chosen `message.height`: [3](#0-2) 

Crucially, this only checks `meta.sender == address(0)` (i.e. whether `_requestCommitments` was already cleared) and a *remote* non-membership proof at an arbitrary historical height — it never checks the *local* `_responseReceipts[commitment]` that `dispatchIncoming(GetResponse,...)` already populated on this same chain. `EvmHost` retains state commitments per-height indefinitely (`_stateCommitments[height.stateMachineId][height.height]`), and `handleGetRequestTimeouts` only requires that the chosen height's own challenge period has elapsed — not that it be the latest height: [4](#0-3) 

Consequently: an attacker dispatches a GET request with a short `timeout` (satisfying `request.timeout() > state.timestamp` becoming false at many historical heights), waits for a relayer to legitimately deliver the response (paying the relayer the fee, but leaving `_requestCommitments` intact), then submits a valid-but-stale non-membership proof from a height that predates the response's inclusion on hyperbridge. `dispatchTimeOut` pays `meta.fee` a second time to `meta.sender` — the original payer, i.e. the attacker themselves — and this requires only that the attacker's own `onGetTimeout` callback (their own module) return success.

### Impact Explanation
This is a fund-drain / theft vulnerability: the `feeToken` balance held by `EvmHost` can be paid out twice for the same GET request — once to the relayer, once back to the payer — with the second payout obtained "for free" via a stale-but-cryptographically-valid proof. Repeated across many requests this drains the host's fee-token reserves, meeting the "concrete theft ... of funds" bar. It is reachable entirely from unprivileged, permissionless entry points (`handleGetResponses` / `handleGetRequestTimeouts` are both explicitly documented as callable by anyone).

### Likelihood Explanation
The attacker fully controls the GET request's `timeout` value and is the natural `payer`/`sender` and destination-module operator for their own request, so no third-party cooperation or race is required beyond waiting for normal relayer delivery, then submitting an old (but genuinely valid) consensus/state-commitment proof that the host still stores. `EvmHost`'s state-commitment history is not automatically purged, unlike `pallet-ismp` on the Substrate side, which uses a bounded eviction queue for this same map (`insert_bounded_state_commitment`) — the EVM path has no equivalent invalidation of stale heights relative to already-settled requests.

### Recommendation
In `dispatchIncoming(GetResponse,...)`, delete `_requestCommitments[commitment]` (or otherwise mark it settled) once the fee has been paid, and have `dispatchTimeOut(GetRequestTimeout,...)`/`handleGetRequestTimeouts` check the chain's own `_responseReceipts[commitment]` (not just a remote non-membership proof) before refunding, rejecting the timeout if a response was already recorded locally. Alternatively, require that timeout proofs be verified only against the *latest* known state commitment height for the destination, not an arbitrary historical one.

### Proof of Concept
1. Attacker deploys a trivial `IApp` module implementing `onGetResponse` and `onGetTimeout` (both simply return success).
2. Attacker calls `EvmHost.dispatch(DispatchGet)` with a short `timeout` (e.g. 60s), paying `fee` in `feeToken`; `_requestCommitments[commitment] = {sender: attacker, fee}` is stored.
3. A relayer delivers the response normally via `HandlerV2.handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse,...)`, paying `fee` to the relayer; `_requestCommitments[commitment]` remains set (not deleted).
4. Attacker (or colluding relayer) submits `HandlerV2.handleGetRequestTimeouts` using a state-machine height `H0` recorded before hyperbridge processed/recorded the response (still stored and challenge-period-elapsed on `EvmHost`), whose `state.timestamp >= request.timeout()`, with a valid non-membership proof of `ResponseReceipts[commitment]` at `H0`.
5. `EvmHost.dispatchTimeOut(GetRequestTimeout,...)` executes: `meta.sender == attacker`, `onGetTimeout` succeeds, and `fee` is transferred to the attacker a second time — total payout for the single request is `2 * fee` instead of `fee`.

### Citations

**File:** evm/src/core/EvmHost.sol (L781-788)
```text

        _consensusState = state;
        _consensusUpdateTimestamp = block.timestamp;

        _stateCommitments[height.stateMachineId][height.height] = commitment;
        _stateCommitmentsUpdateTime[height.stateMachineId][height.height] = block.timestamp;
        _latestStateMachineHeight[height.stateMachineId] = height.height;
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
