Confirmed: the relayer submits `leaf.response` (a full `GetResponse` struct, including `values`) as part of the calldata in `HandlerV2.handleGetResponses`, and the only check performed is that `leaf.response.hash()` matches a leaf proven in the MMR root (`MerkleMountainRange.VerifyProof`) — there is no check anywhere in `handleGetResponses` (`evm/src/core/HandlerV2.sol:217-247`) that `leaf.response.values.length` equals `leaf.response.request.keys.length`, or that it is non-empty. The `values` array is whatever Hyperbridge's MMR leaf encodes for that response, which for the `_cancelFromSource` GET query (`evm/src/apps/intentsv2/ExtrinsicIntents.sol:257-258`) always requests exactly one key, so an honest response also has exactly one value — but nothing enforces that shape here in the app callback itself.

### Title
Empty/short `values` array in a GET response permanently reverts `onGetResponse` and freezes the cross-chain escrow refund - (File: evm/src/apps/intentsv2/ExtrinsicIntents.sol)

### Summary
`ExtrinsicIntents.onGetResponse` indexes `incoming.response.values[0]` without checking the array is non-empty: [1](#0-0) 
Similarly, `onAccept` indexes `incoming.request.body[0]` without checking `body.length != 0`: [2](#0-1) 
Both mirror the CVE-2018-18873 bug class: a callee reads an offset out of attacker/relayer-influenced data without validating length first, causing an unconditional revert (the Solidity analog of a NULL/out-of-bounds crash) instead of a clean, typed rejection.

### Finding Description
`onGetResponse` is invoked by `EvmHost.dispatchIncoming` after `HandlerV2.handleGetResponses` verifies the GET response's MMR/state-commitment inclusion proof: [3](#0-2) 
That verification only checks `leaf.response.hash()` against the proven leaf hash — it never checks `leaf.response.values.length` against `leaf.response.request.keys.length`, nor that it's non-zero. The `values` array content is whatever the ISMP host that produced the response committed to; it is not re-derived or bounds-checked by `HandlerV2` or `EvmHost` before being handed to the app. If a `values` array of length 0 (or any length that omits index 0) is ever included in a proven response leaf — whether via a malformed/incompatible off-chain responder implementation, a future protocol change to `GetResponse` encoding, or a bug on the counterparty chain's ISMP host — `incoming.response.values[0]` reverts unconditionally inside `onGetResponse`.

Because `EvmHost.dispatchIncoming` treats callback failure as "retry later" (deletes the response receipt so it can be resubmitted) rather than storing a fallback, and because the response's content is fixed once committed by the source ISMP host, a response leaf with the wrong-shaped `values` array can never be delivered successfully — the callback will revert every single time it is retried, since the calldata is immutable once produced.

### Impact Explanation
This is a permanent denial-of-delivery for the specific cross-chain message: the escrow-cancellation GET response can never be processed by `onGetResponse`, so `_withdraw` is never reached and the escrowed input tokens for that order remain frozen in the contract with no other code path to release them (the destination-side fill path is closed once cancellation was already initiated). This matches the "route unable to deliver messages" / permanent freezing-of-funds impact class.

### Likelihood Explanation
Likelihood is **low-to-medium** and depends on an implementation-level mismatch rather than a directly attacker-forgeable value: `HandlerV2`/`EvmHost` do not independently validate `values.length` against the corresponding `keys.length`, so the guarantee that `values` is non-empty rests entirely on every ISMP host implementation across every connected chain always populating exactly one `StorageValue` per requested key. This is currently true for the reference implementations reviewed, but the missing explicit check means a single non-conforming/buggy off-chain host, a future key-batching change, or a version-encoding mismatch is enough to trigger the unconditional revert with no defensive error message, silently freezing user funds rather than failing closed with a clear, recoverable error.

### Recommendation
Add explicit length checks before indexing attacker/host-supplied arrays in both callbacks:
- In `onGetResponse`, require `incoming.response.values.length != 0` (and ideally `== incoming.response.request.keys.length`) before indexing `values[0]`, reverting with a clear typed error (e.g. `InvalidGetResponse()`) rather than an implicit out-of-bounds revert.
- In `onAccept`, require `incoming.request.body.length != 0` before reading `body[0]`, reverting with a typed error (e.g. `EmptyRequestBody()`).

This turns an unrecoverable, permanently-reverting delivery into a clean rejection, consistent with how other proof-parsing paths in this codebase (e.g. `modules/trees/ethereum/src/node_codec.rs`, `modules/consensus/beefy/verifier/src/lib.rs`) were hardened against exactly this class of unchecked-index panic on attacker/relayer-controlled data.

### Proof of Concept
1. A source ISMP host (or a future/alternate implementation of the counterparty chain's response encoder) produces a `GetResponse` whose `values` array has length 0 for a request that queried one key, and commits this response into its MMR/state.
2. A relayer submits this response leaf via `HandlerV2.handleGetResponses`, which verifies only the inclusion proof of `leaf.response.hash()` — passing, since the hash matches the committed (malformed) response — and calls `EvmHost.dispatchIncoming(leaf.response, relayer)`.
3. `EvmHost.dispatchIncoming` calls `IApp(instance).onGetResponse(IncomingGetResponse(response, relayer))`, executing `incoming.response.values[0].value.length` in `ExtrinsicIntents.onGetResponse`, which reverts with an out-of-bounds panic.
4. `dispatchIncoming` catches the failure, deletes the response receipt "so it can be retried" — but because the message bytes are immutable and always regenerate the same empty `values` array, every retry reverts identically, and the escrowed tokens tied to that order's cancellation commitment are never released.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L360-366)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
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
