### Title
Freezing the host does not pause the consensus unbonding clock, causing `handleConsensus` to permanently brick the host with `ConsensusClientExpired` after any admin pause approaching the unstaking period - (File: `evm/src/core/HandlerV2.sol`, `evm/src/core/EvmHost.sol`)

### Summary
This is a direct analog of the BendDAO finding: an absolute, real-world elapsed-time check does not account for the duration the protocol was administratively paused, so unpausing exposes participants to an unavoidable penalty determined purely by how long the pause lasted, not by any real fault.

### Finding Description
`EvmHost.setFrozenState()` lets the admin or handler put the host into `FrozenStatus.All`/`Incoming`/`Outgoing` for emergency maintenance [1](#0-0) . This freeze mechanism does not touch `_consensusUpdateTimestamp`, which is only set in the constructor, in `setConsensusState`, and via `storeConsensusState` when a consensus proof is actually processed [2](#0-1) [3](#0-2) .

Meanwhile, `HandlerV2.handleConsensus()` — the entry point any relayer uses to submit a consensus proof and reachable by any unprivileged caller — computes elapsed real time since the last consensus update and reverts if it has passed the configured `unStakingPeriod`:

```solidity
function handleConsensus(IHost host, bytes calldata proof) external notFrozen(host) {
    uint256 delay = block.timestamp - host.consensusUpdateTime();
    if (delay >= host.unStakingPeriod()) revert ConsensusClientExpired();
    ...
``` [4](#0-3) 

`consensusUpdateTime()` simply returns the raw, un-paused timestamp: `return _consensusUpdateTimestamp;` [5](#0-4) .

This is structurally identical to the BendDAO bug: `_updateBorrowIndex` computed `cumulatedBorrowInterest` from `assetData.lastUpdateTimestamp` without accounting for the fact that the position was paused and users could not act during that window. Here, `handleConsensus` computes `delay` from `_consensusUpdateTimestamp` without accounting for the fact that the host itself was frozen (via `notFrozen(host)` on this very function, and via `EvmHost.dispatch`'s `notFrozen` modifier [6](#0-5) [7](#0-6) ) and no relayer could have submitted a consensus proof during the freeze, i.e. the wait was entirely out of the relayers'/users' control.

If governance freezes the host (e.g., `FrozenStatus.All` or `FrozenStatus.Incoming`) for an emergency lasting close to or longer than `unStakingPeriod`, then upon unfreezing the very first `handleConsensus` call will revert with `ConsensusClientExpired` — because the elapsed wall-clock time (which fully includes the frozen duration) already exceeds the unstaking period. Because `EvmHost` is a one-shot consensus-state initializer (`_canReinitConsensus()` only permits admin re-init when `_consensusState` is empty, i.e. only once ever, before the first `storeConsensusState`) [8](#0-7) , there is no on-chain, permissionless path to reset `_consensusUpdateTimestamp` once a real consensus state has ever been set — the host is left permanently unable to accept new consensus proofs through this deployment.

### Impact Explanation
This is a route-unable-to-deliver-messages / permanent freezing-of-funds class issue: once `ConsensusClientExpired` triggers, `handleConsensus` (and therefore every message dependent on fresh consensus state, since `notFrozen`/challenge-period logic all key off state advanced via consensus) can never succeed again on that `EvmHost` deployment. All in-flight requests, funded fees, and escrowed assets tied to that host become permanently undeliverable/unrecoverable through the normal protocol path, since there is no permissionless recovery — only a full redeploy/migration, which is outside the affected users' control. This matches "a route unable to deliver messages" and "permanent freezing of funds" acceptance criteria.

### Likelihood Explanation
Likelihood is moderate: it requires governance/admin to invoke `setFrozenState` (an intended, documented emergency operation, not a malicious action) for a duration close to `unStakingPeriod`. Since freeze durations are explicitly "intended to be small" but, per the judge's own reasoning in the referenced report, "can be arbitrarily long" during an actual incident (the scenario freezing exists to handle), a long incident response window realistically collides with this unbonded clock. The bug is entirely deterministic once that precondition is met — no attacker action is needed, only time passing while frozen.

### Recommendation
Track a separate "frozen duration" or pause the unbonding/consensus clock while the host is frozen, mirroring the BendDAO mitigation: record the timestamp when `setFrozenState` transitions to a frozen state and when it transitions back to `None`, and subtract the cumulative frozen duration from the `delay` computed in `handleConsensus` (i.e., `delay = block.timestamp - consensusUpdateTime() - totalFrozenDuration`), or advance `_consensusUpdateTimestamp` by the frozen duration when unfreezing. Alternatively, provide an explicit permissionless/admin recovery path to reset `_consensusUpdateTimestamp` after an unfreeze event so a completed freeze cannot silently convert into a permanent bricking condition.

### Proof of Concept
1. Deploy `EvmHost`, initialize with a `unStakingPeriod` of, say, 7 days, and set an initial consensus state via `setConsensusState` (sets `_consensusUpdateTimestamp = block.timestamp`).
2. Admin calls `setFrozenState(FrozenStatus.All)` in response to an incident.
3. Time passes (`vm.warp`) by 7 days + 1 second while frozen — no relayer can call `handleConsensus` due to `notFrozen(host)`.
4. Admin calls `setFrozenState(FrozenStatus.None)` to resume operations.
5. A relayer immediately calls `HandlerV2.handleConsensus(host, proof)`. `delay = block.timestamp - host.consensusUpdateTime()` is now `>= unStakingPeriod`, so the call reverts with `ConsensusClientExpired()` regardless of how valid the submitted proof is.
6. Since `_canReinitConsensus()` returns `false` (consensus state is non-empty), the admin cannot call `setConsensusState` again to reset the timestamp — the host can never accept a consensus update again.

Note: I could not fully verify whether any other admin-only escape hatch (e.g., a governance-guarded re-initializer added elsewhere in the codebase, or an upgrade path) exists to reset `_consensusUpdateTimestamp` post-freeze; the search of `EvmHost.sol` and `HandlerV2.sol` found none, but a background Devin session with full repo access should confirm there is no such override function before treating this as unconditionally unrecoverable.

### Citations

**File:** evm/src/core/EvmHost.sol (L354-357)
```text
    modifier notFrozen() {
        if (_frozen == FrozenStatus.Outgoing || _frozen == FrozenStatus.All) revert FrozenHost();
        _;
    }
```

**File:** evm/src/core/EvmHost.sol (L366-369)
```text
    constructor(address _admin) {
        _consensusUpdateTimestamp = block.timestamp;
        _hostParams.admin = _admin;
    }
```

**File:** evm/src/core/EvmHost.sol (L417-422)
```text
    /**
     * @return the last updated time of the consensus client
     */
    function consensusUpdateTime() external view returns (uint256) {
        return _consensusUpdateTimestamp;
    }
```

**File:** evm/src/core/EvmHost.sol (L746-753)
```text
    function setFrozenState(FrozenStatus newState) external {
        address caller = _msgSender();
        if (caller != _hostParams.admin && caller != _hostParams.handler) revert UnauthorizedAction();

        _frozen = newState;

        emit HostFrozen({status: newState});
    }
```

**File:** evm/src/core/EvmHost.sol (L762-764)
```text
    function _canReinitConsensus() internal view virtual returns (bool) {
        return keccak256(_consensusState) == keccak256(bytes(""));
    }
```

**File:** evm/src/core/EvmHost.sol (L776-787)
```text
    function setConsensusState(bytes memory state, StateMachineHeight memory height, StateCommitment memory commitment)
        public
        restrict(_hostParams.admin)
    {
        if (!_canReinitConsensus()) revert UnauthorizedAction();

        _consensusState = state;
        _consensusUpdateTimestamp = block.timestamp;

        _stateCommitments[height.stateMachineId][height.height] = commitment;
        _stateCommitmentsUpdateTime[height.stateMachineId][height.height] = block.timestamp;
        _latestStateMachineHeight[height.stateMachineId] = height.height;
```

**File:** evm/src/core/EvmHost.sol (L921-921)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
```

**File:** evm/src/core/HandlerV2.sol (L144-147)
```text
    function handleConsensus(IHost host, bytes calldata proof) external notFrozen(host) {
        uint256 delay = block.timestamp - host.consensusUpdateTime();
        if (delay >= host.unStakingPeriod()) revert ConsensusClientExpired();

```
