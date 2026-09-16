## Finding

### Title
Stale `FeeMetadata` reused after GET-response delivery enables double payment of relayer fee via forged historical timeout proof - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming(GetResponse memory response, address relayer)` pays out the relayer fee from `_requestCommitments[commitment]` but never deletes that entry afterward, unlike every other consuming path in the same contract. [1](#0-0)  This leaves a stale, still-"alive" `FeeMetadata` object that can later be consumed a second time by a timeout message for the same commitment.

### Finding Description
`EvmHost` tracks per-request fee escrow in `_requestCommitments[commitment]` (a `FeeMetadata{sender, fee}`), populated at dispatch time. [2](#0-1) 

There are three code paths that consume this record:
- `dispatchIncoming(GetResponse, relayer)` — pays the fee to the relayer on successful delivery, but does **not** delete `_requestCommitments[commitment]` afterward. [1](#0-0) 
- `dispatchTimeOut(GetRequestTimeout, meta, commitment)` — explicitly `delete _requestCommitments[commitment]` **before** the external callback, then refunds `meta.fee` to `meta.sender` on success (checks-effects-interactions pattern). [3](#0-2) 
- `dispatchTimeOut(PostRequestTimeout, meta, commitment)` — same delete-before-call pattern. [4](#0-3) 

`HandlerV2.handleGetRequestTimeouts` guards the timeout path only with: (1) a `request.timeout() > state.timestamp` check against the *timeout message's referenced height* `message.height`, (2) `host.requestCommitments(commitment).sender != address(0)`, and (3) a non-membership proof that `ResponseReceipts[commitment]` is absent from the state trie *at that specific height* `message.height`. [5](#0-4) 

Because `dispatchIncoming(GetResponse,...)` never clears `_requestCommitments[commitment]`, condition (2) remains satisfied indefinitely after a successful response delivery. The only remaining barrier is the non-membership proof in condition (3) — but that proof is checked against an arbitrary, relayer-chosen finalized height `message.height`, not against the *current* state. If a `GetRequestTimeout` proof is anchored to a height *prior* to the block in which the response was actually delivered/recorded on the destination chain (while still satisfying `request.timeout() > state.timestamp` and the challenge-period delay check), the non-membership proof for `ResponseReceipts` at that earlier height verifies successfully even though the response has since been delivered and its relayer already paid. `host.dispatchTimeOut` will then pay `meta.fee` a second time, to `meta.sender`, off the same never-cleared `FeeMetadata`.

This is the same bug *class* as the referenced Chrome UAF (CVE-2022-3071): an object (`FeeMetadata`) that should have been "freed" (cleared) once consumed is instead left alive and reachable, and a subsequent, protocol-permitted interaction (a permissionless timeout submission) reuses that stale object to trigger unintended state mutation — here, a second token transfer.

### Impact Explanation
A successfully-answered `GetRequest`'s escrowed fee can be paid twice: once to the legitimate relayer that delivered the `GetResponse`, and a second time refunded to `meta.sender` via a timeout proof anchored to an earlier finalized height. This drains `feeToken` from `EvmHost` beyond what was actually escrowed for that request — a direct theft/unbacked-payout of protocol funds reachable by any relayer submitting a permissionless message (`handleGetRequestTimeouts` is unauthenticated, matching the "reachable by an unprivileged relayer" scope of this program).

### Likelihood Explanation
Exploitability depends on being able to construct a valid consensus/state proof for a finalized height `message.height` that (a) precedes the block where the response's `ResponseReceipts` entry was written, (b) still satisfies `request.timeout() > state.timestamp` at that height, and (c) has cleared the challenge-period delay. This is plausible because `state.timestamp`/height selection for the timeout proof is entirely the caller's choice among any previously finalized heights still tracked by the host (`_stateCommitments`), and nothing ties the timeout proof's height to "current" state. I was not able to fully verify, within the scope of this review, the exact window of finalized heights retained by the host or the prover tooling's height-selection constraints, so the precise ease of constructing such a proof is uncertain; the missing `delete` itself, however, is a concrete, unconditional root-cause defect confirmed in code.

### Recommendation
In `EvmHost.dispatchIncoming(GetResponse memory response, address relayer)`, delete `_requestCommitments[commitment]` (mirroring the `dispatchTimeOut` pattern, ideally before the external `onGetResponse` call per checks-effects-interactions) once the fee has been read/paid, so that no later timeout path can find a non-zero `meta.sender`/`fee` for an already-delivered response, regardless of which historical height is used for the non-membership proof.

### Proof of Concept
1. Attacker dispatches a `GetRequest` on chain A with `fee = F`; `_requestCommitments[commitment] = {sender: attacker, fee: F}`.
2. Relayer delivers the corresponding `GetResponse` via `HandlerV2.handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse, relayer)`; `F` is paid to `relayer`; `_requestCommitments[commitment]` remains unchanged (bug). [6](#0-5) 
3. Attacker (or colluding relayer) later submits `HandlerV2.handleGetRequestTimeouts` with a `GetTimeoutMessage` proof anchored at a finalized height *earlier* than the block that recorded the `ResponseReceipts` entry for `commitment`, satisfying `request.timeout() > state.timestamp` for that height and the challenge-period delay. [7](#0-6) 
4. The non-membership proof for `ResponseReceipts[commitment]` at that earlier height succeeds (entry did not yet exist then), passing `entry.value.length == 0`.
5. `host.dispatchTimeOut(GetRequestTimeout, meta, commitment)` executes; since `meta.sender`/`meta.fee` were never cleared in step 2, `F` is refunded to `attacker`, resulting in `2F` paid out for a single `F` originally escrowed. [3](#0-2)

### Citations

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

**File:** evm/src/core/EvmHost.sol (L946-948)
```text
        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
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
