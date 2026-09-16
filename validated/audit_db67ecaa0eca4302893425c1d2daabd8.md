## Analog Found

### Title
Genesis/first-time state machine commitments are never stored due to a zero-height sentinel edge case in `HandlerV2.handleConsensus()` - (File: `evm/src/core/HandlerV2.sol`)

### Summary
The external report's bug class is: a fixed "gate" condition uses a field's zero value as a proxy for "not yet populated," but the field can legitimately be (or resolve to, after truncation/default) zero for reasons unrelated to initialization, so the gate silently skips real, valid data. The direct analog in Hyperbridge is the `latestHeight != 0` guard in `HandlerV2.handleConsensus()`, which gates whether a freshly verified `IntermediateState` is ever persisted via `host.storeStateMachineCommitment`.

### Finding Description
In `handleConsensus`, each verified intermediate state is only committed if the counterparty state machine already has a nonzero recorded height: [1](#0-0) 

```solidity
uint256 latestHeight = host.latestStateMachineHeight(intermediate.stateMachineId);
if (latestHeight != 0 && intermediate.height > latestHeight) {
    StateMachineHeight memory stateMachineHeight =
        StateMachineHeight({stateMachineId: intermediate.stateMachineId, height: intermediate.height});
    host.storeStateMachineCommitment(stateMachineHeight, intermediate.commitment);
}
```

`host.latestStateMachineHeight(...)` reads a mapping whose default (unset) value is `0` — this is exactly the same "sentinel collides with a legitimate default" pattern the Twav report describes (`timestamp == 0` used both as "not yet observed" and as a legitimate wrapped value). Here, `latestHeight == 0` is the default state for **every state machine that has never had a commitment stored**, which is precisely the case for the very first proof relayed for a newly-connected/onboarded counterparty chain. Because the guard requires `latestHeight != 0` *before* even comparing heights, the first-ever intermediate state for that state machine ID is unconditionally dropped, regardless of how high `intermediate.height` is. Since `storeStateMachineCommitment` is the only thing that ever advances `latestStateMachineHeight`, this is a chicken-and-egg lock: `latestHeight` can never become non-zero, so every subsequent consensus proof for that state machine hits the same false branch forever.

### Impact Explanation
`HandlerV2.handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, and `handleGetRequestTimeouts` all require a previously stored, non-zero state commitment before they will process any proof: [2](#0-1) 

Because the commitment for a newly onboarded state machine is never written (per the bug above), `host.stateMachineCommitment(...)` stays at its zero default forever, so `root == bytes32(0)` / `state.stateRoot == bytes32(0)` always reverts with `StateCommitmentNotFound`. This permanently freezes the message-delivery route for that counterparty state machine — no post request, get response, or timeout can ever be delivered to or from it — matching the "route unable to deliver messages" impact class called out in the validation criteria.

### Likelihood Explanation
This triggers deterministically, with no adversarial input required, the very first time a relayer submits a valid consensus proof containing an `IntermediateState` for any state machine ID whose `latestStateMachineHeight` is still at its default (i.e., any state machine being connected/onboarded for the first time, or one reset to 0). Any unprivileged relayer calling `handleConsensus` reliably reproduces it.

### Recommendation
Remove the `latestHeight != 0` short-circuit, or replace it with an explicit "has this state machine ever been initialized" check that does not conflate "unset" with "height 0":
```solidity
if (intermediate.height > latestHeight) {
    ...
    host.storeStateMachineCommitment(stateMachineHeight, intermediate.commitment);
}
```
Since `latestHeight` defaults to `0`, a plain `intermediate.height > latestHeight` comparison already correctly allows the very first commitment through for any height `> 0`, and equals the safe fix the Twav report recommended (replace a zero-sentinel edge check with a monotonic comparison that doesn't require a prior non-zero value).

### Proof of Concept
1. Deploy `EvmHost`/`HandlerV2` and connect a brand-new counterparty state machine `X` that has never had a commitment stored (`latestStateMachineHeight(X) == 0` by mapping default).
2. Have the configured consensus client produce a valid proof containing an `IntermediateState` for `X` at height `H > 0` (e.g., `H = 1000`).
3. Call `handleConsensus(host, proof)`. Because `latestHeight (0) != 0` evaluates to `false`, the `if` body never executes, and `host.storeStateMachineCommitment` is never called.
4. `host.stateMachineCommitment(StateMachineHeight({stateMachineId: X, height: H}))` remains the zero-value default.
5. Any subsequent `handlePostRequests`/`handleGetResponses`/timeout call referencing height `H` for `X` reverts with `StateCommitmentNotFound`, and there is no path by which `latestStateMachineHeight(X)` can ever become non-zero, permanently freezing message delivery to/from `X`.

**Note on verification limits:** I was unable to complete confirmation of whether `EvmHost.sol`'s initializer sets a non-default `latestStateMachineHeight` for pre-registered state machines at deployment time (which could narrow this to only "newly onboarded after deployment" state machines rather than all of them); the tool budget was exhausted before I could inspect `EvmHost.sol`'s `initialize`/genesis logic in full. A Devin session with full repository access should check `evm/src/core/EvmHost.sol` around its `latestStateMachineHeight`/`stateMachineCommitment` storage initialization to determine exactly which state machines are affected (all vs. only those added post-deployment).

### Citations

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

**File:** evm/src/core/HandlerV2.sol (L199-202)
```text
        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();
```
