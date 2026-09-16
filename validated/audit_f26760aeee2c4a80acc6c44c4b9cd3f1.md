### Title
Double-spend of escrowed GET request fee via stale `_requestCommitments` entry not cleared after successful response delivery - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming(GetResponse)` pays the escrowed request fee to the delivering relayer but never deletes the corresponding `_requestCommitments[commitment]` entry. `EvmHost.dispatchTimeOut(GetRequestTimeout, ...)` independently reads and pays out the *same* `_requestCommitments[commitment]` entry to the original requester when a non-membership proof is supplied. Because the first code path leaves the fee-escrow record intact ("dangling"), the second path can still successfully "use" it later, paying out the same fee a second time. This mirrors a use-after-free primitive: a resource is consumed/freed on one path but the reference to it is never invalidated, allowing a second, illegitimate consumption of the same resource.

### Finding Description
`EvmHost.dispatch(DispatchGet)` escrows the caller-supplied fee into `_requestCommitments[commitment] = FeeMetadata({sender, fee})`: [1](#0-0) 

When the relayer delivers the corresponding `GetResponse` through `HandlerV2.handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse)`, the fee is paid to the relayer, but the fee-metadata record is never removed: [2](#0-1) 

Separately, `HandlerV2.handleGetRequestTimeouts` allows anyone to submit a non-membership proof, anchored at *any* previously-committed state height, showing that at that historical height Hyperbridge had not yet recorded a response for this request: [3](#0-2) 

It then calls `EvmHost.dispatchTimeOut(GetRequestTimeout, ...)`, which reads `meta.fee` from the *same* `_requestCommitments[commitment]` slot and refunds it to `meta.sender`: [4](#0-3) 

The only guard against a spurious timeout is `if (meta.sender == address(0)) revert UnknownMessage();`, checked in `handleGetRequestTimeouts`. Because `dispatchIncoming(GetResponse)` never clears `_requestCommitments[commitment]`, this check still passes after a legitimate, successful response delivery. As long as an attacker can produce a non-membership proof for a state height whose timestamp is at/after `request.timeout()` but whose response-receipt storage predates the actual (possibly late-arriving) response — which is trivially available whenever a response is delivered even slightly after its nominal timeout, or simply by using any state height captured before Hyperbridge recorded the response — the same escrowed fee can be paid twice: once to the relayer via `dispatchIncoming(GetResponse)`, and again to the original sender via `dispatchTimeOut(GetRequestTimeout)`, draining `feeToken` reserves held by `EvmHost`.

The `dispatchTimeOut(PostRequestTimeout, ...)` path does not have this issue, because it explicitly `delete`s `_requestCommitments[commitment]` for replay protection before the external call: [5](#0-4) 

The `GetResponse` delivery path lacks the analogous cleanup, which is the root cause.

### Impact Explanation
This allows theft of `feeToken` funds held by `EvmHost`: the same escrowed GET-request fee can be released twice through two independently reachable, permissionless handler entry points (`handleGetResponses` and `handleGetRequestTimeouts`), draining protocol fee reserves. This is unprivileged, single-transaction-reachable by any relayer/requester, and results in concrete theft of funds, satisfying the required impact bar.

### Likelihood Explanation
Both `handleGetResponses`/`dispatchIncoming(GetResponse)` and `handleGetRequestTimeouts`/`dispatchTimeOut` are explicitly permissionless entry points intended to be called by any relayer. Producing a non-membership proof for a historical state height that predates when the response commitment was recorded on the remote/Hyperbridge chain is a normal byproduct of asynchronous cross-chain messaging (late responses relative to their own timeout, or simply reusing an earlier already-finalized state commitment), making this reachable without any privileged access or unusual timing assumptions.

### Recommendation
Delete `_requestCommitments[commitment]` inside `dispatchIncoming(GetResponse)` immediately upon successful (or even attempted) fee payout, mirroring the replay-protection pattern already used in `dispatchTimeOut(PostRequestTimeout, ...)` and `dispatchTimeOut(GetRequestTimeout, ...)`, so the fee-escrow slot cannot be "used" a second time by a subsequently submitted timeout proof.

### Proof of Concept
1. Attacker calls `EvmHost.dispatch(DispatchGet)` with `fee = F`, escrowing `F` fee tokens into `_requestCommitments[commitment]`.
2. The GET request times out on-chain-logically (`request.timeout()` elapses) but Hyperbridge still processes and returns a `GetResponse` (e.g., due to relaying/finality delay).
3. A relayer submits this response via `HandlerV2.handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse)`. The callback to `onGetResponse` succeeds, and `fee = F` is paid to the relayer. `_requestCommitments[commitment]` is **not** deleted.
4. Attacker (or colluding relayer) submits `HandlerV2.handleGetRequestTimeouts` with a non-membership proof anchored at an earlier committed `StateMachineHeight` whose `state.timestamp >= request.timeout()` but at which the response-receipt was not yet present in Hyperbridge's child trie.
5. `dispatchTimeOut(GetRequestTimeout, meta, commitment)` executes: `meta.sender != address(0)` passes, the external `onGetTimeout` call to `timeout.request.from` (attacker-controlled) succeeds, and `meta.fee = F` is transferred again to `meta.sender`.
6. Net result: `F` fee tokens paid out twice for a single GET request, draining `EvmHost`'s fee token balance.

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

**File:** evm/src/core/EvmHost.sol (L999-1001)
```text
        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: _msgSender(), fee: get.fee});
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
