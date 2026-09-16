### Title
Post-interaction fee-metadata read in `dispatchIncoming(GetResponse)` allows a stale/reentrant `_requestCommitments` state to double-pay or forge relayer fee rewards - (File: evm/src/core/EvmHost.sol)

### Summary
The CVE-2022-3886 bug class is a use-after-free: an object is freed/mutated by one code path while a stale reference to it is still used by another in-flight path, corrupting state. The closest reachable analog in this codebase is `EvmHost.dispatchIncoming(GetResponse, address relayer)`, which reads `_requestCommitments[commitment].fee` **after** making an untrusted external call to the destination module, rather than snapshotting the fee metadata before the call (the checks-effects-interactions ordering used everywhere else in this file).

### Finding Description
In `evm/src/core/EvmHost.sol`:

```
function dispatchIncoming(GetResponse memory response, address relayer) external restrict(_hostParams.handler) {
    bytes32 commitment = response.request.hash();
    _responseReceipts[commitment] = ResponseReceipt({relayer: relayer, responseCommitment: response.hash()});

    (bool success,) = _bytesToAddress(response.request.from)
        .call(abi.encodeWithSelector(IApp.onGetResponse.selector, IncomingGetResponse(response, relayer)));
    ...
    // reward the relayer fee
    uint256 fee = _requestCommitments[commitment].fee;   // <-- read AFTER the external call
    if (fee != 0) {
        IERC20(feeToken()).safeTransfer(relayer, fee);
    }
``` [1](#0-0) 

`response.request.from` is an address chosen entirely by whoever originally dispatched the GET request — any attacker-deployed `IApp` contract. `dispatchIncoming` is only `restrict(_hostParams.handler)`-gated (callable by `HandlerV2`), and `HandlerV2.batchCall` explicitly exists to let a relayer chain multiple handler entry points — `handleGetResponses`, `handlePostRequestTimeouts`, `handleGetRequestTimeouts` — inside one atomic transaction via `delegatecall`:

```
function batchCall(bytes[] memory calls) external {
    for (uint256 i = 0; i < len; ++i) {
        (bool success, bytes memory returnData) = address(this).delegatecall(calls[i]);
        ...
``` [2](#0-1) 

No `nonReentrant`/`ReentrancyGuard` modifier exists anywhere on `EvmHost` [3](#0-2) , so the attacker-controlled `onGetResponse` callback can call back into `HandlerV2` (e.g. `handleGetRequestTimeouts`) for the very same GET request commitment while `dispatchIncoming(GetResponse,...)` is still mid-execution and has not yet consumed `_requestCommitments[commitment]`. That reentrant path independently reads and then deletes/re-inserts the same `_requestCommitments[commitment]` slot (`dispatchTimeOut`) and pays out `meta.fee` to `meta.sender` directly:

```
function dispatchTimeOut(GetRequestTimeout memory timeout, FeeMetadata memory meta, bytes32 commitment) ... {
    delete _requestCommitments[commitment];
    (bool success,) = _bytesToAddress(timeout.request.from).call(...);
    if (!success) { _requestCommitments[commitment] = meta; return; }
    if (meta.fee != 0) { IERC20(feeToken()).safeTransfer(meta.sender, meta.fee); }
``` [4](#0-3) 

Because the outer `dispatchIncoming(GetResponse)` only re-reads `_requestCommitments[commitment].fee` from storage **after** the reentrant call returns, whichever code path executes last against that shared slot determines what gets paid, and the value can be manipulated in between the read that gated entry into the handler batch and the later fee payout inside `dispatchIncoming`. This is the same class of bug as the Chromium UAF: a shared record is freed/rewritten by a nested call while an outer frame still holds a "live" reference to it and later reads it as if unmodified.

### Impact Explanation
If exploitable end-to-end, this allows an attacker to trigger fee/reward accounting to be paid out incorrectly (either duplicated, zeroed after legitimate use, or redirected) via a single relayed GET response transaction that reenters the handler. That is unbacked/duplicated payout of protocol fee-token funds, which maps to the "theft or permanent freezing of funds" / "relayer fee and reward accounting" impact categories explicitly in scope.

### Likelihood Explanation
Medium. The attacker fully controls the destination module address (`response.request.from`) since GET request dispatch is permissionless, and `HandlerV2.batchCall` provides a straightforward transaction-level composition vector to call `handleGetResponses` and `handleGetRequestTimeouts` for the same commitment in one atomic transaction. However, exploitability depends on precise timing/ordering of the two commitments' timeout windows and non-membership proof availability, which I was not able to fully trace end-to-end within the available context (in particular whether `handleGetRequestTimeouts`'s non-membership proof check can be satisfied for a request that is simultaneously being delivered as a response in the same block). This uncertainty should be resolved by tracing the full state-machine height/proof preconditions before treating this as confirmed-exploitable.

### Recommendation
Snapshot `_requestCommitments[commitment]` (and its `.fee`) into a local variable **before** making the external call in `dispatchIncoming(GetResponse,...)`, matching the checks-effects-interactions pattern already used in `dispatchIncoming(PostRequest,...)` and `dispatchTimeOut`. Additionally, add a reentrancy guard on `EvmHost`'s handler-restricted entry points (`dispatchIncoming`, `dispatchTimeOut`) so that no other handler path can touch the same `commitment`'s storage while a call to an untrusted `IApp` is outstanding.

### Proof of Concept
Conceptual (not verified against live proof-generation constraints):
1. Attacker deploys `MaliciousApp` implementing `IApp.onGetResponse`, and dispatches a GET request from it, so `_requestCommitments[commitment]` is created with a nonzero relayer fee and `from = MaliciousApp`.
2. Relayer (attacker-controlled or unwitting) submits a `HandlerV2.batchCall` containing `handleGetResponses(...)` for this commitment.
3. Inside `EvmHost.dispatchIncoming(GetResponse,...)`, the external call into `MaliciousApp.onGetResponse` reenters `HandlerV2.handleGetRequestTimeouts(...)` for the same commitment (assuming a satisfiable non-membership proof / timeout window overlap), which runs `EvmHost.dispatchTimeOut`, deleting/rewriting `_requestCommitments[commitment]` and paying out `meta.fee`.
4. Execution returns to the outer `dispatchIncoming`, which reads the now-mutated `_requestCommitments[commitment].fee` and pays out again (or a different amount than intended), corrupting relayer fee accounting. [1](#0-0) [4](#0-3) [2](#0-1) [5](#0-4)

### Citations

**File:** evm/src/core/EvmHost.sol (L794-847)
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

**File:** evm/src/core/HandlerV2.sol (L129-135)
```text
    function batchCall(bytes[] memory calls) external {
        uint256 len = calls.length;
        for (uint256 i = 0; i < len; ++i) {
            (bool success, bytes memory returnData) = address(this).delegatecall(calls[i]);
            if (!success) revert BatchCallFailed(i, returnData);
        }
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
