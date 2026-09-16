### Title
Missing length check on `IncomingGetResponse.response.values` before indexing in `onGetResponse` — ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
`ExtrinsicIntents.onGetResponse` indexes `incoming.response.values[0]` without first checking that the `values` array is non-empty, mirroring the CVE-2024-42276 bug class: a data structure produced conditionally (here, per-key proof values) is consumed by a downstream handler that assumes its existence instead of re-validating it, matching the "map" step's guarantees.

### Finding Description
`_cancelFromSource` in `IntrinsicIntents`/`ExtrinsicIntents` dispatches a `DispatchGet` with exactly one storage key (the `_filled[commitment]` slot on the destination) via `IDispatcher(hostAddr).dispatch(...)`. When the response comes back, `onGetResponse` reads it as:

```solidity
function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
    _checkRelayer(incoming.relayer);
    if (incoming.response.values[0].value.length != 0) revert Filled();

    WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
    _withdraw(body, true, true);
}
``` [1](#0-0) 

`incoming.response.values` is populated on Hyperbridge's `pallet-ismp` response handler from `state_machine.verify_state_proof(host, keys, ...)`, which builds a `BTreeMap<key, Option<value>>` and then `.collect()`s it in map order into a `Vec<StorageValue>` [2](#0-1) . On the EVM `HandlerV2.handleGetResponses` side, the `GetResponseLeaf` (including its `values` array) is supplied entirely by the relayer and only checked for a matching MMR leaf hash and a known/unduplicated request commitment — there is no check that `values.length` matches the number of keys in the original `GetRequest`, nor any lower bound enforced by the handler itself [3](#0-2) . Whether `values` can legitimately be length 0 for a well-formed key set is not verifiable here without access to the exact state-machine key-resolution code paths (e.g. `verify_state_proof` for every supported client) that build the map from the requested keys — the EVM state-machine implementation appears to guarantee one entry per requested contract, but the completeness argument spans multiple consensus/state-machine backends (Pharos, sync-committee, Substrate) not all confirmed to preserve a 1:1 key→value mapping.

The unconditional `values[0]` access is the same class of defect as the kernel bug: a consumer indexes into a collection that was populated conditionally on a specific state (successful proof-driven population, one entry per key) without re-checking that state at the point of use, instead of guarding with `values.length == 0` the way `onGetResponse` for balance queries does elsewhere in the docs example (`if (response.values.length == 0) { ...; return; }`) [4](#0-3) .

### Impact Explanation
If `values` can ever arrive empty or shorter than expected for a delivered `GetResponse` (e.g. a relayer submits a legitimate MMR-proved response where the state-machine's key resolution produced zero entries, or a future/alternate state-machine implementation used with this app has different unwind behavior for missing keys), `onGetResponse` reverts on the out-of-bounds index. Because the host's `dispatchIncoming` treats a reverting `onAccept`/`onGetResponse` call as "undelivered" and leaves the receipt un-set, the response can never be successfully delivered through that same commitment, permanently blocking the source-chain cancellation/refund flow (`_cancelFromSource` → GET request → `onGetResponse` → `_withdraw`) for that order. This is a route-unable-to-deliver-messages / permanent-freezing-of-escrowed-funds condition for the affected order, since the user's escrow can no longer be refunded via this path once the GET response is (or must be) delivered.

### Likelihood Explanation
Reachable from a single relayed GET-response delivery — no privileged role required, matching the message-dispatcher/relayer path in scope. Likelihood depends on whether any supported consensus/state-machine backend can produce a `values` array with fewer entries than the requested `keys` for a validly-proved response (this could not be fully confirmed for every backend in the time available); if so, exploitation requires no attacker action beyond normal delivery of a legitimately-provable response, making it plausible under specific state conditions (e.g., proof of non-existence handled inconsistently by a state-machine backend) rather than trivially always triggerable.

### Recommendation
Add an explicit length check before indexing, mirroring the safe pattern already used elsewhere in the documentation examples:
```solidity
if (incoming.response.values.length == 0) revert Filled(); // or a dedicated error
if (incoming.response.values[0].value.length != 0) revert Filled();
```
More robustly, assert `incoming.response.values.length == incoming.response.request.keys.length` (or `== 1`, since exactly one key is dispatched) at the top of `onGetResponse`, so any response shape divergence from the expected single-key GET request fails safely instead of relying on implicit invariants from the proof-verification pipeline.

### Proof of Concept
Not fully constructible without confirming a concrete state-machine/consensus path that yields `values.length == 0` for a MMR-provable `GetResponse` to a single-key `GetRequest`; this would require crafting or finding a state-machine client (Pharos/sync-committee/Substrate) where `verify_state_proof` drops a requested key from its result map, then relaying that GetResponse through `HandlerV2.handleGetResponses` to `ExtrinsicIntents.onGetResponse`, causing the revert and stranding the escrow refund for the corresponding order commitment.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L360-366)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```

**File:** modules/ismp/core/src/handlers/response.rs (L82-89)
```rust
		.map(|request| {
			let wrapped_req = Request::Get(request.clone());
			let keys = request.keys.clone();
			let values = state_machine
				.verify_state_proof(host, keys, state.state_root, &proof)?
				.into_iter()
				.map(|(key, value)| StorageValue { key, value })
				.collect();
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

**File:** docs/content/developers/evm/messaging/get-requests.mdx (L256-261)
```text
        
        // response.values[0] could be empty if the user has no balance
        if (response.values.length == 0) {
            emit BalanceRetrieved(initiator, token, account, 0);
            return;
        }
```
