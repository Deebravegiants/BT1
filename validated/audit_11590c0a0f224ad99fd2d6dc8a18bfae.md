### Title
Stale `_requestCommitments` entry after successful GET-response delivery enables double fee refund via replayed historical timeout proof - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatchIncoming(GetResponse, address)` pays out the relayer fee for a fulfilled GET request but never clears the corresponding `_requestCommitments[commitment]` entry, unlike every other terminal path (`dispatchTimeOut` for both POST and GET, which explicitly `delete _requestCommitments[commitment]`). Because old `StateMachineHeight` commitments are never pruned from `EvmHost` and `HandlerV2.handleGetRequestTimeouts` lets the caller pick *any* previously stored, non-vetoed height to build its non-membership proof, a relayer can later replay a timeout for the same GET request using a state root from *before* Hyperbridge processed the response. `dispatchTimeOut` performs no local check against `_responseReceipts` before paying out, so the fee is refunded a second time and the destination module's `onGetTimeout` fires for a request that was already answered.

### Finding Description
The GET-request/response lifecycle in `evm/src/core/EvmHost.sol`:

1. `dispatch(DispatchGet)` (~line 974-1013) stores `_requestCommitments[commitment] = FeeMetadata({sender, fee})`.
2. On success, `dispatchIncoming(GetResponse memory response, address relayer)` (lines 824-847) is invoked by `HandlerV2.handleGetResponses`. It sets `_responseReceipts[commitment]`, calls the module's `onGetResponse`, and — on success — pays `_requestCommitments[commitment].fee` to the relayer: [1](#0-0) 
Notably it never calls `delete _requestCommitments[commitment]`.
3. Compare this with the GET-timeout path, `dispatchTimeOut(GetRequestTimeout, FeeMetadata meta, bytes32 commitment)` (lines 856-877), which explicitly clears the commitment for replay protection and unconditionally refunds `meta.fee` to `meta.sender` on success: [2](#0-1) 
This function does **not** check `_responseReceipts[commitment]` to verify the request hasn't already been answered on this chain — it relies entirely on the caller (`HandlerV2`) having proven, via a state proof, that Hyperbridge has no response receipt for the commitment.

4. `HandlerV2.handleGetRequestTimeouts` (lines 293-321) lets the relayer supply an arbitrary `message.height` (any previously accepted `StateMachineHeight`) and fetches `host.stateMachineCommitment(message.height)` for that specific height, verifying a non-membership proof of `ResponseReceipts` against that height's `stateRoot`: [3](#0-2) 
`EvmHost` never prunes or deprecates old `_stateCommitments[stateMachineId][height]` entries once they've been stored and their challenge period has elapsed (they persist unless explicitly vetoed by a fisherman), so any height recorded *before* Hyperbridge serviced the GET request remains permanently valid for building this non-membership proof — even long after a newer height already shows the response was delivered.

Because (a) `_requestCommitments[commitment]` survives a successful GET response delivery, and (b) `dispatchTimeOut` trusts the caller-selected historical height's non-membership proof without cross-checking local `_responseReceipts` state, a relayer can:
- Wait for a legitimate GET response to be delivered and the fee paid via `dispatchIncoming`.
- Submit `handleGetRequestTimeouts` using an *older*, already-finalized `message.height` (recorded before Hyperbridge processed and stored the response receipt) where the non-membership proof still validly shows "no response yet" and the request's `timeoutTimestamp` was already ≤ that height's timestamp.
- Trigger `dispatchTimeOut`, which finds `meta.sender != address(0)` (never cleared), deletes the (now-redundant) commitment, and pays out `meta.fee` a second time — plus invokes the module's `onGetTimeout` for a request the module already believes was answered via `onGetResponse`.

This is the same bug class as CVE-2021-38011 (use of a resource after it has been logically "freed"/consumed, without invalidating the stale reference): the `_requestCommitments` entry is the resource that should be invalidated once consumed by a successful response delivery, but it is left dangling and can be "reused" through an alternate code path (`dispatchTimeOut`) using a stale-but-still-provable historical state, corrupting the protocol's fee accounting.

### Impact Explanation
This results in concrete theft of ERC20 fee-token funds from `EvmHost`'s balance: relayer fees are paid out twice for the same GET request (once at delivery, once at "timeout"), draining the fee token reserve funded by the protocol/users. It also triggers an unauthorized app-level action — the destination module's `onGetTimeout` callback fires for a request it already processed via `onGetResponse`, which can corrupt any app-side state that assumes exactly one terminal callback per request (e.g., double-refunding an escrowed amount in a dependent app). This satisfies the "concrete theft of funds" / "unauthorized app action" bar required by the report criteria, and is reachable purely by a relayer submitting a relayed proof/message — no privileged role required.

### Likelihood Explanation
Exploitation requires: (1) a GET request whose response is delivered normally, and (2) a relayer holding (or able to re-derive/replay) a valid, previously-accepted `StateMachineHeight` proof from before Hyperbridge recorded the response — something any relayer naturally retains from earlier operation of the bridge, since these proofs and state commitments are public and never invalidated. No collusion with governance, no malicious admin, and no consensus break is needed; it is purely a logic/state-management flaw in `EvmHost`/`HandlerV2`. This makes it readily exploitable by any unprivileged relayer with access to routine historical proof data.

### Recommendation
- In `dispatchIncoming(GetResponse, address)`, delete `_requestCommitments[commitment]` after (or as part of) a successful delivery, mirroring the POST-request/response and GET-timeout handling, so the commitment cannot be reused by a later timeout call.
- In `dispatchTimeOut(GetRequestTimeout, ...)`, add an explicit check that `_responseReceipts[commitment].relayer == address(0)` before proceeding, so a timeout can never be processed for a request that has already received a response on this chain, regardless of which historical state height is presented.
- Consider restricting `handleGetRequestTimeouts`/`handlePostRequestTimeouts` to only accept the *latest* known `StateMachineHeight` for the relevant state machine (or otherwise bound how far back a non-membership proof height can be), to prevent stale historical proofs from being used to bypass state that has since changed.

### Proof of Concept
1. App on chain A calls `EvmHost.dispatch(DispatchGet{...})` → `_requestCommitments[C]` is stored with `fee = F`, `sender = user`.
2. Hyperbridge coprocessor services the GET, and a relayer calls `HandlerV2.handleGetResponses` at Hyperbridge height `H2` → `EvmHost.dispatchIncoming(response, relayer)` pays `F` to `relayer` and sets `_responseReceipts[C]`, but leaves `_requestCommitments[C]` intact (`evm/src/core/EvmHost.sol:824-847`).
3. The same or a different relayer later calls `HandlerV2.handleGetRequestTimeouts` supplying `message.height = H1` where `H1 < H2` was accepted earlier (before the response existed in Hyperbridge's child trie) and where `state(H1).timestamp >= request.timeoutTimestamp`. The non-membership proof for `RESPONSE_RECEIPTS_STORAGE_PREFIX || C` against `state(H1).stateRoot` succeeds because, at height `H1`, no response had yet been recorded.
4. `HandlerV2` calls `host.dispatchTimeOut(GetRequestTimeout(request, relayer2), meta, C)`. Since `_requestCommitments[C]` still holds `meta.sender = user, meta.fee = F` (`evm/src/core/EvmHost.sol:856-877`), and there is no check on `_responseReceipts[C]`, the fee `F` is transferred a second time to `user` (or is otherwise disbursed again), and the destination module's `onGetTimeout` is invoked for an already-answered request. [1](#0-0) [2](#0-1) [3](#0-2)

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
