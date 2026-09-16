### Title
Removing a state machine from `HostParams.stateMachines` does not revoke its ability to receive consensus updates or deliver messages — ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.updateHostParamsInternal` treats `params.stateMachines` as an append-only allow-list: it initializes `_latestStateMachineHeight[id] = 1` for any newly listed state machine, but never deletes the entry for a state machine that governance drops from the new list. Because `_latestStateMachineHeight != 0` is the only gate `HandlerV2.handleConsensus` uses to decide whether to keep accepting/storing new state commitments for a state machine, a state machine that governance believes it has "disabled" keeps accepting new consensus-verified state and keeps being usable to deliver messages — mirroring the reported Mattermost bug class where disabling a shared-resource feature flag does not actually revoke access to resources that were already provisioned under it.

### Finding Description
`updateHostParamsInternal` in [1](#0-0)  only *adds* to `_latestStateMachineHeight` for entries present in the new `params.stateMachines` array:

```solidity
for (uint256 i = 0; i < stateMachinesLen; ++i) {
    if (_latestStateMachineHeight[params.stateMachines[i]] == 0) {
        _latestStateMachineHeight[params.stateMachines[i]] = 1;
    }
}
```

There is no corresponding removal step for state machine ids that were in the *old* `_hostParams.stateMachines` but are omitted from the *new* one. `_hostParams.stateMachines` itself is simply overwritten [2](#0-1) , but that field is documentation/config only — no dispatch or delivery path checks membership in `_hostParams.stateMachines` before acting.

The actual gate used at runtime is `_latestStateMachineHeight[id] != 0`, checked only inside `handleConsensus` to decide whether to persist a newly verified intermediate state:

```solidity
uint256 latestHeight = host.latestStateMachineHeight(intermediate.stateMachineId);
if (latestHeight != 0 && intermediate.height > latestHeight) {
    host.storeStateMachineCommitment(stateMachineHeight, intermediate.commitment);
}
``` [3](#0-2) 

Since `_latestStateMachineHeight[id]` is never cleared when a state machine is removed from `params.stateMachines`, `handleConsensus` — a fully permissionless function callable by anyone [4](#0-3)  — keeps accepting and storing new state commitments for the "removed" chain forever.

Worse, the message-delivery paths (`handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, `handleGetRequestTimeouts`) never consult `_hostParams.stateMachines` or `_latestStateMachineHeight` for source-authorization at all; they only check that a `stateMachineCommitment` exists at the referenced height [5](#0-4) . Because `handleConsensus` keeps producing new commitments for the "removed" state machine, relayers can keep delivering post requests/responses sourced from it indefinitely, exactly as if it were never removed — the on-chain effect of a governance "disable" action is silently no-op.

### Impact Explanation
This breaks the security guarantee that cross-chain governance (via `HostManager.onAccept` → `SetHostParam` → `updateHostParams`) can shut off a compromised, faulty, or otherwise untrusted counterparty state machine. If governance intends to cut off a state machine (e.g., because its consensus client was compromised, its chain forked maliciously, or as an emergency circuit-breaker), the removal has no actual effect: an unprivileged relayer can continue to submit consensus proofs for that state machine via `handleConsensus`, and continue delivering (forging trust in) post requests/responses/timeouts sourced from it via `handlePostRequests`/`handleGetResponses`/timeout handlers. This is a forged/unauthorized-message-delivery class issue — the removal is a security control that a relayer can silently bypass, potentially enabling continued minting, unauthorized app actions, or state manipulation from a state machine governance explicitly intended to disconnect.

### Likelihood Explanation
High reachability: any relayer can call `handleConsensus`/`handlePostRequests`/etc. permissionlessly with a single transaction, no special privileges required. The only precondition is that governance previously whitelisted the state machine and later attempted to remove it via a normal `updateHostParams` call — a realistic and expected governance operation (e.g. decommissioning a chain or responding to an incident).

### Recommendation
When a state machine present in the old `_hostParams.stateMachines` is absent from the new `params.stateMachines`, explicitly `delete _latestStateMachineHeight[id]` (and ideally purge/mark associated `_stateCommitments`/`_stateCommitmentsUpdateTime` as revoked) during `updateHostParamsInternal`, and add an explicit whitelist check in `handlePostRequests`/`handleGetResponses`/timeout handlers so delivery of messages sourced from a removed state machine is rejected even if stale commitments remain.

### Proof of Concept
1. Governance calls `updateHostParams` with `stateMachines = [A, B]`; `_latestStateMachineHeight[A] = 1`, `_latestStateMachineHeight[B] = 1`.
2. Later, governance (believing it disconnects `B`, e.g. due to a security incident) calls `updateHostParams` with `stateMachines = [A]` only.
3. `_hostParams.stateMachines` now shows `[A]`, but `_latestStateMachineHeight[B]` remains `1` (never cleared).
4. Any relayer calls `HandlerV2.handleConsensus(host, proof)` with a valid consensus proof containing an intermediate state for `B` at a height greater than the stored one — `handleConsensus` happily calls `host.storeStateMachineCommitment` for `B` because `latestHeight != 0`.
5. The relayer then calls `handlePostRequests`/`handleGetResponses` with a valid MMR proof against the freshly stored `B` commitment — the request/response is dispatched to the destination app, exactly as if `B` were still whitelisted, defeating the governance disable action.

### Citations

**File:** evm/src/core/EvmHost.sol (L635-636)
```text
        _hostParams.stateMachines = params.stateMachines;
        _hostParams.hyperbridge = params.hyperbridge;
```

**File:** evm/src/core/EvmHost.sol (L638-644)
```text
        // add whitelisted state machines
        for (uint256 i = 0; i < stateMachinesLen; ++i) {
            // create if it doesn't already exist
            if (_latestStateMachineHeight[params.stateMachines[i]] == 0) {
                _latestStateMachineHeight[params.stateMachines[i]] = 1;
            }
        }
```

**File:** evm/src/core/HandlerV2.sol (L144-150)
```text
    function handleConsensus(IHost host, bytes calldata proof) external notFrozen(host) {
        uint256 delay = block.timestamp - host.consensusUpdateTime();
        if (delay >= host.unStakingPeriod()) revert ConsensusClientExpired();

        bytes memory previousState = host.consensusState();
        (bytes memory verifiedState, IntermediateState[] memory intermediates, uint256 nextAuthoritySetId) =
            IConsensusV2(host.consensusClient()).verify(previousState, proof);
```

**File:** evm/src/core/HandlerV2.sol (L155-164)
```text
        uint256 intermediatesLen = intermediates.length;
        for (uint256 i = 0; i < intermediatesLen; i++) {
            IntermediateState memory intermediate = intermediates[i];
            uint256 latestHeight = host.latestStateMachineHeight(intermediate.stateMachineId);
            if (latestHeight != 0 && intermediate.height > latestHeight) {
                StateMachineHeight memory stateMachineHeight =
                    StateMachineHeight({stateMachineId: intermediate.stateMachineId, height: intermediate.height});
                host.storeStateMachineCommitment(stateMachineHeight, intermediate.commitment);
            }
        }
```

**File:** evm/src/core/HandlerV2.sol (L199-209)
```text
        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```
