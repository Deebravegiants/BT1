### Title
`deleteStateMachineCommitmentInternal` resets `_latestStateMachineHeight` to a hardcoded value of `1` on veto, an invalid assumption that height `1` is always a valid/initialized commitment - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.deleteStateMachineCommitmentInternal` (invoked from `deleteStateMachineCommitment`, callable only by the handler when a fisherman vetoes a state commitment) resets `_latestStateMachineHeight[stateMachineId]` to the literal constant `1` whenever the vetoed height equals the currently tracked latest height. This mirrors the root cause of the reported `getMaxSecondsAgo()` bug: falling back to a fixed index/height that is assumed to always hold valid, initialized data, without verifying that a commitment actually exists there.

### Finding Description
In `EvmHost.sol`: [1](#0-0) 

```solidity
function deleteStateMachineCommitmentInternal(StateMachineHeight memory height, address fisherman) internal {
    StateCommitment memory stateCommitment = _stateCommitments[height.stateMachineId][height.height];
    delete _stateCommitments[height.stateMachineId][height.height];
    delete _stateCommitmentsUpdateTime[height.stateMachineId][height.height];
    // technically any state commitment can be vetoed, safety check that it's the latest before resetting it.
    if (_latestStateMachineHeight[height.stateMachineId] == height.height) {
        _latestStateMachineHeight[height.stateMachineId] = 1;
    }
    ...
}
```

When the vetoed height happens to be the currently recorded latest height, the code blindly sets `_latestStateMachineHeight[stateMachineId] = 1` instead of rolling back to the actual previous valid height (or `0`/unset). This is exactly the same bug class as the reported issue: instead of checking whether a commitment genuinely exists at the fallback slot (here, height `1`), the code assumes it is always populated/valid.

This assumption breaks in the ordinary lifecycle of a state machine:
- If height `1` was never submitted (e.g., the state machine's genesis commitment starts at a height > 1, or height `1`'s commitment was itself vetoed/expired earlier), `_stateCommitments[stateMachineId][1]` is empty/zero. `latestStateMachineHeight()` (a public getter used by `IIsmpHost`, dispatchers, and downstream consumers such as `latestStateMachineHeight()` calls, `checkClientMembership` flows, and off-chain relayers/indexers) will now report `1` as the "latest" height even though no valid commitment for height `1` exists.
- Any subsequent read (`stateMachineCommitment(height)` with `height.height == 1`) will return a zeroed `StateCommitment` (empty state root / zero overlay root), because `deleteStateMachineCommitmentInternal`'s deletion of the actual commitment (from a *different*, larger height) does not create a valid commitment at height `1`.
- Relayers and message-dispatch flows querying `latestStateMachineHeight` to decide which height to use for proof submission (state membership/non-membership checks in `EvmHost`/`HandlerV2` request delivery) could be pointed at a height with no verified commitment, causing either denial-of-service on delivery (proofs against height `1` will fail verification because the commitment is empty/zero) or, in a worst case where a different unrelated commitment happens to be stored at height `1` from a stale prior submission, acceptance of proofs verified against a stale/incorrect state root — enabling forged message delivery for that particular height.

The stated invariant "technically any state commitment can be vetoed, safety check that it's the latest before resetting it" only checks whether the vetoed height *matches* the tracked latest height; it never checks whether height `1` itself holds a real, non-empty commitment before treating it as the new "latest."

### Impact Explanation
This is a High-severity issue in the message-dispatch/state-verification path:
- `_latestStateMachineHeight` is the primary on-chain reference other contracts and relayers use to determine what height's commitment is safe to prove against (via `latestStateMachineHeight()` in `IIsmpHost`). Pointing it at an uninitialized/zeroed commitment can cause routes to be unable to deliver messages (all proofs against the reported "latest" height fail because no valid commitment exists there), which is a concrete denial-of-service for message delivery on that state machine.
- If a state machine's commitment at height `1` was previously set (even if since superseded and pruned via other paths) but does not match the semantically expected "current" state, resolvers/relayers could unknowingly accept/produce proofs referencing an incorrect height, undermining the integrity of state membership checks used across `EvmHost`/`HandlerV2` request/response delivery.

### Likelihood Explanation
This path is reachable purely through the normal fisherman-veto flow: `deleteStateMachineCommitment` is called by the configured handler whenever a fisherman successfully challenges/vetoes a state commitment (a standard, expected part of Hyperbridge's operational flow, not a privileged/malicious-admin scenario). The triggering condition — vetoing the state machine's currently-tracked latest commitment while no valid commitment exists at height `1` — is very plausible in production: most state machines' first tracked height is not literally `1` (it is whatever height was first submitted via `storeStateMachineCommitment`/`setConsensusState`), so the fallback to `1` will very often reference an empty slot.

### Recommendation
Do not hardcode the fallback to `1`. Either:
- Maintain an explicit "previous height" pointer per state machine that is updated on every `storeStateMachineCommitment` call, and roll back to that value (or to `0`/an explicit "unset" sentinel) on veto of the latest height, or
- After vetoing, scan/require that the fallback height actually has `stateCommitment.timestamp != 0` (or equivalent non-empty marker) before treating it as valid, and otherwise set `_latestStateMachineHeight` to `0` to signal "no known latest height" so that downstream consumers can react accordingly rather than silently querying a fabricated height.

### Proof of Concept
1. State machine `X` begins operation; its first commitment is stored at height `100` via `storeStateMachineCommitment`, setting `_latestStateMachineHeight[X] = 100`. No commitment for height `1` was ever stored (`_stateCommitments[X][1]` is the zero-initialized default `StateCommitment`).
2. A fisherman successfully vetoes height `100`'s commitment; the handler calls `deleteStateMachineCommitment({stateMachineId: X, height: 100}, fisherman)`.
3. In `deleteStateMachineCommitmentInternal`, since `_latestStateMachineHeight[X] == 100 == height.height`, the code sets `_latestStateMachineHeight[X] = 1`.
4. `IIsmpHost(host).latestStateMachineHeight(X)` now returns `1`. Any caller (relayer, dispatcher, downstream consumer) that queries `stateMachineCommitment({stateMachineId: X, height: 1})` receives an all-zero `StateCommitment` (`state_root = 0x0`, `timestamp = 0`), because that slot was never populated by a real consensus proof — resulting in unverifiable/failing state proofs and an inability to deliver messages for state machine `X` until a new consensus update supersedes height `1`.

### Citations

**File:** evm/src/core/EvmHost.sol (L714-732)
```text
    function deleteStateMachineCommitmentInternal(StateMachineHeight memory height, address fisherman) internal {
        StateCommitment memory stateCommitment = _stateCommitments[height.stateMachineId][height.height];
        delete _stateCommitments[height.stateMachineId][height.height];
        delete _stateCommitmentsUpdateTime[height.stateMachineId][height.height];
        // technically any state commitment can be vetoed, safety check that it's the latest before resetting it.
        if (_latestStateMachineHeight[height.stateMachineId] == height.height) {
            _latestStateMachineHeight[height.stateMachineId] = 1;
        }

        // track the fisherman responsible for rewards on hyperbridge through state proofs
        _vetoes[height.stateMachineId][height.height] = fisherman;

        emit StateCommitmentVetoed({
            stateMachineId: this.stateMachineId(_hostParams.hyperbridge, height.stateMachineId),
            stateCommitment: stateCommitment,
            height: height.height,
            fisherman: fisherman
        });
    }
```
