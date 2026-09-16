### Title
Missing `_requestCommitments` cleanup on GetResponse delivery enables double payout of the escrowed relayer fee - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatchIncoming(GetResponse, address)` reads the escrowed fee from `_requestCommitments[commitment]` and pays it to the relayer, but — unlike every other consumer of that mapping — never deletes the entry afterward. All three sibling code paths that consume a `_requestCommitments` entry (`dispatchTimeOut(GetRequestTimeout,...)`, `dispatchTimeOut(PostRequestTimeout,...)`) explicitly `delete _requestCommitments[commitment];` under an explicit `// replay protection` comment, but the GetResponse delivery path omits this cleanup.

### Finding Description
`_requestCommitments` stores `FeeMetadata{fee, sender}` for every outgoing request and is meant to be a single-use "session" for the escrowed relayer fee — it should be cleared once the fee has been disbursed, exactly as documented and implemented for both timeout paths: [1](#0-0) 

Both `dispatchTimeOut` overloads explicitly free the slot with a `// replay protection` comment before invoking the module callback: [2](#0-1) [3](#0-2) 

However, `dispatchIncoming(GetResponse memory response, address relayer)` reads and pays out `_requestCommitments[commitment].fee` but never deletes the entry: [4](#0-3) 

The only replay guard added on this path is `_responseReceipts[commitment]`, which only prevents the *same* `GetResponse` message from being redelivered — it does nothing to protect `_requestCommitments`, which remains populated with a non-zero `fee` and non-zero `sender` indefinitely after the response is processed.

`HandlerV2.handleGetRequestTimeouts` gates entry into `dispatchTimeOut(GetRequestTimeout,...)` solely on:
1. `meta.sender != address(0)` read from the stale, un-cleared `_requestCommitments[commitment]`, and
2. a non-membership proof of `ResponseReceipts` against the *coprocessor's* (Hyperbridge) state trie root at `message.height`: [5](#0-4) 

Because condition (1) is checked against the never-deleted local `_requestCommitments` mapping, and condition (2) is a proof against a separate, independently-updated remote trie (`ResponseReceipts` on Hyperbridge, populated by `pallet_ismp`'s `child_trie::ResponseReceipts`), the two checks are not derived from the same causally-linked local state transition that `GetResponse` delivery on this host makes. If a relayer can produce a valid non-membership proof for a height at/around the time the corresponding `GetResponse` was already delivered locally (e.g. by using an older accepted state-machine height still within `challengePeriod`, or any height preceding the point at which Hyperbridge's own `ResponseReceipts` entry for that commitment was committed relative to the response being included in the delivered MMR/overlay batch), `handleGetRequestTimeouts` → `dispatchTimeOut` will succeed for a request whose fee has *already* been paid out via `dispatchIncoming(GetResponse,...)`.

### Impact Explanation
`dispatchTimeOut(GetRequestTimeout,...)` refunds `meta.fee` to `meta.sender` a second time, transferring `feeToken` out of the host that was already fully disbursed to the relayer during response delivery. This is a direct drain of protocol/escrowed funds triggered purely by a relayer submitting two independently-provable proofs for the same request — no privileged role is required. Even ignoring the specific race window, the missing cleanup is a genuine defect: the mapping is documented and implemented everywhere else as single-use ("replay protection"), and its omission here breaks that invariant for the GetResponse path specifically, unlike its Post/Get-timeout siblings.

### Likelihood Explanation
Reachable by any relayer (unprivileged) who can submit a `GetResponseMessage` followed later by a `GetTimeoutMessage` for the same commitment using a state height/proof combination that still satisfies the non-membership check on Hyperbridge's `ResponseReceipts` child trie for that commitment. The `challengePeriod`/height-based checks in `HandlerV2` do not by themselves guarantee that a response's inclusion and its `ResponseReceipts` commitment on the coprocessor are updated atomically with respect to every height a relayer could still supply a proof for.

### Recommendation
Delete `_requestCommitments[commitment]` in `dispatchIncoming(GetResponse memory response, address relayer)` immediately after successfully paying the relayer fee (mirroring the `// replay protection` pattern used in both `dispatchTimeOut` overloads), so the fee-escrow slot cannot be referenced or paid out again via a later timeout dispatch for the same commitment.

### Proof of Concept
1. Dispatch a `GetRequest` via `EvmHost.dispatch(DispatchGet)`, escrowing `fee` in `_requestCommitments[commitment]`.
2. Relayer delivers the `GetResponse` via `HandlerV2.handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse,...)`: `_responseReceipts[commitment]` is set, `fee` is paid to the relayer, but `_requestCommitments[commitment]` is left unchanged (still `{fee, sender}`).
3. The same or a colluding relayer later submits `HandlerV2.handleGetRequestTimeouts` with a `GetTimeoutMessage` referencing a state height/non-membership proof for `ResponseReceipts` that is still valid for that commitment (e.g., a height prior to/around the response's inclusion, still within the accepted `challengePeriod`/height window tracked by the host).
4. `meta.sender != address(0)` check passes (stale entry), non-membership proof passes, `dispatchTimeOut` executes and refunds `meta.fee` to `meta.sender` again — the same fee has now been paid out twice from the host's `feeToken` balance.

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

**File:** evm/src/core/EvmHost.sol (L885-893)
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
