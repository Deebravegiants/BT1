## Analysis

The CVE describes a **use-after-free**: an object is freed, and a stale reference to it is later dereferenced, corrupting state. The closest reachable analog in this codebase is in `EvmHost.sol`'s incoming-message dispatch functions, which have **no reentrancy protection** and read a storage mapping *after* an untrusted external call that can, via a legitimate reentrant path through `HandlerV2`, delete that same mapping entry first.### Title
Reentrant timeout drains the request-fee record read by `dispatchIncoming(GetResponse)`, causing loss of the relayer's fee reward - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatchIncoming(GetResponse)` calls the untrusted destination module (`onGetResponse`) *before* reading `_requestCommitments[commitment].fee` to pay the relayer. Because `EvmHost`/`HandlerV2` have no reentrancy guard, and `dispatchTimeOut` is only gated by `restrict(_hostParams.handler)` (i.e. callable by any transaction that routes through `HandlerV2`, including one triggered mid-callback), a malicious destination module can reenter through `HandlerV2.handleGetRequestTimeouts` and delete `_requestCommitments[commitment]` before the outer function reads it. This is a direct analog of the CVE's "use after free" pattern: an object (`_requestCommitments[commitment]`) is freed by a nested/reentrant call, and the outer frame subsequently dereferences the now-stale/zeroed storage slot.

### Finding Description
- `EvmHost.dispatchIncoming(GetResponse, relayer)` [1](#0-0)  writes the response receipt, makes a low-level `call` to the destination module's `onGetResponse` (fully attacker-controlled code when the module is the original requester contract), and only *after* that external call returns does it read `_requestCommitments[commitment].fee` to pay the relayer:
```
uint256 fee = _requestCommitments[commitment].fee;
if (fee != 0) { IERC20(feeToken()).safeTransfer(relayer, fee); }
```
- `EvmHost.dispatchTimeOut(GetRequestTimeout, ...)` [2](#0-1)  unconditionally `delete`s `_requestCommitments[commitment]` *before* invoking the module's `onGetTimeout` callback and refunding `meta.fee` to `meta.sender`.
- Both `dispatchIncoming` and `dispatchTimeOut` are restricted only to `_hostParams.handler` — i.e. any call that originates from `HandlerV2` satisfies the restriction, including one that HandlerV2 itself triggers as a nested call while `EvmHost` is mid-execution of a different top-level call. Neither `EvmHost.sol` nor `HandlerV2.sol` contain any `nonReentrant`/reentrancy-guard mechanism (confirmed by search — no matches for `nonReentrant`, `ReentrancyGuard`, or `reentran` in `evm/src/core/*.sol`).
- `HandlerV2.handleGetRequestTimeouts` [3](#0-2)  accepts **any previously stored state commitment height** as proof of timeout, requiring only `request.timeout() > state.timestamp` for that height and a non-membership proof of the response receipt *at that specific historical height*. It does not require the height to be the latest known height, nor does it re-validate against a fresher state that might already contain the response. Because state commitments for old heights are retained indefinitely (`_stateCommitments` is never pruned except via fisherman veto), an attacker can supply a proof anchored to an older height whose timestamp already exceeds the GET request's `timeoutTimestamp` but which predates the height at which the response was actually recorded/delivered.

Attack flow:
1. Attacker deploys a malicious `IApp` module and dispatches a `GetRequest` via `EvmHost.dispatch(DispatchGet)`, paying a relayer fee `F`. `_requestCommitments[commitment] = FeeMetadata({sender: attacker, fee: F})` [4](#0-3) .
2. A relayer delivers the legitimate `GetResponse` via `HandlerV2.handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse, relayer)` [5](#0-4) .
3. Inside the low-level call to attacker's `onGetResponse`, the attacker's module reenters via `HandlerV2.handleGetRequestTimeouts`, supplying a valid non-membership proof anchored to an *older* stored height whose `state.timestamp` already exceeds `request.timeout()`. This passes all checks (`meta.sender != 0`, valid non-membership proof) and calls `host.dispatchTimeOut(GetRequestTimeout(...), meta, commitment)`.
4. `dispatchTimeOut` deletes `_requestCommitments[commitment]`, calls the attacker's `onGetTimeout` (which the attacker makes succeed), and refunds fee `F` to `meta.sender` (the attacker) via `safeTransfer`.
5. Control returns to the outer `dispatchIncoming(GetResponse)` call, which now reads `_requestCommitments[commitment].fee` — but the entry was just deleted, so `fee == 0`. The relayer who legitimately delivered the response receives **nothing**.

Net effect: the attacker collects the fee twice in intent (once as an illegitimate "timeout" refund to themselves, while the response was in fact delivered) and the relayer who did the real work of delivering the response is paid zero, because the outer function dereferences a request-commitment record that was freed by a reentrant call it did not anticipate.

### Impact Explanation
This is a fee/reward-accounting bypass reachable via a single relayed GET-response delivery combined with an attacker-controlled destination module — squarely within the audited "relayer fee and reward accounting" and "token bridge mint/burn"-adjacent scope (fee token transfers via `IERC20.safeTransfer`). It results in permanent loss of the relayer's expected fee (the funds are drained to the attacker instead), which is a concrete theft/fund-diversion outcome, not merely a griefing/DoS issue.

### Likelihood Explanation
Exploitability requires: (a) the attacker be the `GetRequest` sender/destination module (fully attacker-controlled, always possible since `dispatch(DispatchGet)` is open to anyone), (b) an already-finalized older state-commitment height whose timestamp exceeds the request's configured timeout while a non-membership proof for that height is obtainable (plausible whenever request timeouts are set shorter than the challenge/finality delay, which is a realistic configuration), and (c) no reentrancy guard exists to prevent the nested call — confirmed by direct code search. No governance, admin, or privileged role is required; only a standard relayer submitting a legitimate response transaction is needed to trigger the callback into the attacker's contract.

### Recommendation
- Add a reentrancy guard (e.g. OpenZeppelin `ReentrancyGuard`) around `EvmHost.dispatchIncoming` and `dispatchTimeOut`, or otherwise prevent `HandlerV2` from being re-entered while a prior dispatch is executing.
- In `dispatchIncoming(GetResponse)`, cache `_requestCommitments[commitment]` (or its `fee`) **before** making the external call to the destination module, so the fee to be paid is fixed at the start of the function rather than read after arbitrary reentrant state mutation.
- In `HandlerV2.handleGetRequestTimeouts` (and the POST analog), require that the state height used for the non-membership proof be the *latest* known height for that state machine (or otherwise bind the timeout check to a height that cannot predate a later height at which the response was actually recorded), to prevent "time-travel" timeout proofs against stale but still-valid historical state commitments.

### Proof of Concept
Conceptual PoC (Foundry-style), given the analyzed call graph:
1. Deploy `MaliciousApp` implementing `IApp`:
   - `onAccept`/`dispatch`: unused.
   - Have `MaliciousApp` call `host.dispatch(DispatchGet({... timeout: shortTimeout, payer: address(MaliciousApp), fee: F ...}))`.
2. Relayer submits the response via `HandlerV2.handleGetResponses`, targeting `MaliciousApp` as `response.request.from`.
3. `MaliciousApp.onGetResponse` callback reenters `HandlerV2.handleGetRequestTimeouts`, passing a `GetTimeoutMessage` whose `message.height` refers to an already-finalized, still-stored state height with `state.timestamp > shortTimeout`, together with a valid Merkle/Patricia non-membership proof of the response receipt at that height (obtainable because Hyperbridge recorded the response at a *later* height than the one supplied).
4. Assert: `host.requestCommitments(commitment).fee == 0` after `dispatchIncoming` returns, and that `feeToken.balanceOf(MaliciousApp)` increased by `F`, while `feeToken.balanceOf(relayer)` did not increase by the expected `F`.

Note: This PoC could not be executed against a live/compiled contract in this analysis (read-only code review); the trace above follows directly from the cited function bodies and the confirmed absence of any reentrancy guard in `evm/src/core/EvmHost.sol` / `evm/src/core/HandlerV2.sol`.

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

**File:** evm/src/core/EvmHost.sol (L999-1002)
```text
        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: _msgSender(), fee: get.fee});
        emit GetRequestEvent({
```

**File:** evm/src/core/HandlerV2.sol (L217-247)
```text
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
