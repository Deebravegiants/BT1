Confirmed analog: in `handleConsensus` (`evm/src/core/HandlerV2.sol:158-159`), a new commitment for a state machine is only stored if `latestHeight != 0` — the check that gates whether a chain is "known/whitelisted." Combined with `deleteStateMachineCommitmentInternal` in `EvmHost.sol:704-732`, which resets `_latestStateMachineHeight[stateMachineId]` to the hardcoded value `1` whenever the vetoed height equals the current latest, this reproduces the report's bug class: a default/sentinel value (`1`, standing in for "no real height recorded yet") is silently substituted for the true prior state instead of being derived from actual data, and downstream code trusts it as if it were a legitimate height.

### Title
Vetoing the latest state commitment resets `_latestStateMachineHeight` to a fixed sentinel of `1`, allowing a lower, previously-superseded state commitment to be re-accepted as canonical - (File: evm/src/core/EvmHost.sol)

### Summary
`deleteStateMachineCommitmentInternal` always resets `_latestStateMachineHeight[stateMachineId]` to `1` when the vetoed height was the tracked "latest" height, regardless of what the actual second-most-recent verified height was [1](#0-0) . This mirrors the report's bug class: a hard-coded placeholder is substituted for a value that should have been read from real state (there, `agents[1].agentId` defaulting to `0` instead of the true id; here, the "latest height" defaulting to `1` instead of the true prior height), and a downstream authorization/acceptance check (`agentId` ownership check there; `latestHeight != 0 && intermediate.height > latestHeight` here) is fooled by the sentinel.

### Finding Description
`_latestStateMachineHeight[id]` is documented as: `0` means the state machine is unsupported, and any non-zero value is the latest verified height for that chain [2](#0-1) . When a fisherman vetoes a state commitment via `deleteStateMachineCommitment` → `deleteStateMachineCommitmentInternal`, the code deletes the target height's commitment, and — only if that height equals the current tracked latest — resets `_latestStateMachineHeight[stateMachineId]` to the literal constant `1`:

```solidity
if (_latestStateMachineHeight[height.stateMachineId] == height.height) {
    _latestStateMachineHeight[height.stateMachineId] = 1;
}
``` [3](#0-2) 

This does not restore the actual previous legitimate height (e.g., the height before the vetoed one); it just falls back to `1`, the same initialization value used for brand-new/whitelisted state machines [4](#0-3) . `HandlerV2.handleConsensus` then gates acceptance of new intermediate state commitments purely by comparing against this tracked "latest height":

```solidity
uint256 latestHeight = host.latestStateMachineHeight(intermediate.stateMachineId);
if (latestHeight != 0 && intermediate.height > latestHeight) {
    ...
    host.storeStateMachineCommitment(stateMachineHeight, intermediate.commitment);
}
``` [5](#0-4) 

Because the reset collapses the "true latest" tracking down to `1`, any commitment for a height greater than `1` — including a stale/previously-superseded height that had already been overtaken by later, still-valid consensus updates — becomes acceptable again as if it were new. `storeStateMachineCommitment` unconditionally overwrites `_stateCommitments[id][height]` and `_latestStateMachineHeight[id]` with whatever height is passed [6](#0-5) , so an old commitment can be re-stored at a lower height than the chain's true tip, and `_latestStateMachineHeight` can even be regressed backwards (e.g., from height 1000 down to height 50), reopening a window for previously-timed-out or previously-rejected proofs at intermediate heights to be treated as valid/latest.

### Impact Explanation
Once triggered (a fisherman vetoing the currently-tracked latest height, which is a normal, permissioned but not attacker-controlled operation intended for fraud response), the state-machine height tracking silently regresses to a hardcoded `1` instead of the real prior height. This can let a relayer resubmit an older, previously superseded intermediate state (any commitment with height > 1) through `handleConsensus`, since the guard `intermediate.height > latestHeight` no longer reflects the chain's true progress. This directly affects consensus/state verification integrity that `handlePostRequests`, `handleGetResponses`, and timeout handling all rely on (`host.stateMachineCommitment(...)`, `host.stateMachineCommitmentUpdateTime(...)`), meaning forged or already-superseded state roots could be accepted as canonical for the affected destination, enabling incorrect membership/non-membership proofs to be validated — a form of unsound state commitment acceptance.

### Likelihood Explanation
The veto path (`deleteStateMachineCommitment`) is only reachable via `restrict(_hostParams.handler)`, i.e., invoked by the trusted handler flow following a fisherman's fraud-proof submission — not by an arbitrary unprivileged actor. However, this is a normal, expected part of protocol operation (fishermen are meant to veto fraudulent commitments), not a "malicious admin" scenario, so it falls within the intended threat model. Once a veto of the current latest height occurs (a legitimate, anticipated event), the vulnerable window opens automatically for any relayer to exploit by submitting a stale-height consensus update — no additional privilege is required for that second step.

### Recommendation
Do not reset `_latestStateMachineHeight` to a hardcoded `1`. Instead, either (a) track and restore the actual next-highest surviving height for that state machine (e.g., by walking back the recorded queue in `StateCommitmentQueue`), or (b) keep the vetoed height as a floor without ever moving `_latestStateMachineHeight` backwards below its pre-veto value, ensuring only strictly higher, freshly-verified heights can be accepted afterward.

### Proof of Concept
1. Host state machine `X` has been advanced via consensus updates up to height `1000`, so `_latestStateMachineHeight[X] == 1000`.
2. A fisherman successfully vetoes height `1000` (assume it was fraudulent) by calling `deleteStateMachineCommitment(height=1000, fisherman)`.
3. Because `_latestStateMachineHeight[X] == 1000 == height.height`, the code sets `_latestStateMachineHeight[X] = 1` [7](#0-6) .
4. A relayer now calls `handleConsensus` with a proof containing an `IntermediateState` for `X` at height `50` (a height that was already finalized and consumed by earlier client state, or even a forged/rolled-back branch accepted by the consensus client's own liveness rules).
5. The check `latestHeight != 0 && intermediate.height > latestHeight` passes (`50 > 1`), so `storeStateMachineCommitment` is called, overwriting the tracked latest height back down to `50` and installing a stale/incorrect state root as the "current" commitment for `X` [8](#0-7) .
6. Downstream `handlePostRequests`/`handleGetResponses` calls referencing `height=50` now validate proofs against this potentially stale/incorrect root as if it were the legitimate latest state, undermining state-proof integrity for state machine `X`.

### Citations

**File:** evm/src/core/EvmHost.sol (L505-510)
```text
    /**
     * @return the latest state machine height for the given stateMachineId. If it returns 0, the state machine is unsupported.
     */
    function latestStateMachineHeight(uint256 id) external view returns (uint256) {
        return _latestStateMachineHeight[id];
    }
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

**File:** evm/src/core/EvmHost.sol (L687-699)
```text
    function storeStateMachineCommitment(StateMachineHeight memory height, StateCommitment memory commitment)
        external
        restrict(_hostParams.handler)
    {
        _stateCommitments[height.stateMachineId][height.height] = commitment;
        _stateCommitmentsUpdateTime[height.stateMachineId][height.height] = block.timestamp;
        _latestStateMachineHeight[height.stateMachineId] = height.height;

        emit StateMachineUpdated({
            stateMachineId: this.stateMachineId(_hostParams.hyperbridge, height.stateMachineId), 
            height: height.height
        });
    }
```

**File:** evm/src/core/EvmHost.sol (L704-724)
```text
    function deleteStateMachineCommitment(StateMachineHeight memory height, address fisherman)
        external
        restrict(_hostParams.handler)
    {
        deleteStateMachineCommitmentInternal(height, fisherman);
    }

    /**
     * @dev Delete the state commitment at given state height.
     */
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
```

**File:** evm/src/core/HandlerV2.sol (L156-164)
```text
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
