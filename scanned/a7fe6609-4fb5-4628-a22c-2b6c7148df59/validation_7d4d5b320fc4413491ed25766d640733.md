### Title
No Minimum Timelock Enforcement Allows Pool Admin to Instantly Disable Stop-Loss Protection — (`metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol`)

---

### Summary

`OracleValueStopLossExtension` enforces a per-pool `timelock` that is supposed to give LPs a reaction window before the admin can change the `drawdownE6` or `decayPerSecondE8` parameters. However, there is no minimum value enforced on `timelock` — it can be initialized to `0` or reduced to `0` after waiting the current timelock period. With `timelock == 0`, the admin can propose and execute a `drawdownE6 = 0` change in the same block, which causes `_afterSwapOracleStopLoss` to return early unconditionally, completely disabling the stop-loss for all future swaps.

---

### Finding Description

`initialize` accepts any `uint32 timelock` value including `0` with no validation: [1](#0-0) 

`proposeOracleStopLossTimelock` similarly accepts any `newTimelock` including `0`: [2](#0-1) 

The delay computation in `_afterTimelock` is:

```solidity
return uint32(block.timestamp + oracleStopLossConfig[pool_].timelock);
``` [3](#0-2) 

When `timelock == 0`, `executeAfter == block.timestamp`. The elapsed check `block.timestamp < executeAfter` is immediately false, so `_requireElapsed` passes in the same block as the proposal: [4](#0-3) 

`_validateDrawdown` only rejects values strictly above `1e6`; `drawdownE6 == 0` is accepted: [5](#0-4) 

Once `drawdownE6` is set to `0`, the entire stop-loss check short-circuits on every swap: [6](#0-5) 

---

### Impact Explanation

The `OracleValueStopLossExtension` is the sole on-chain mechanism that blocks swaps when per-bin LP value per share falls below a drawdown floor. Disabling it removes the only guard against value-drain attacks (e.g., oracle manipulation causing the pool to trade at a bad price). LPs who joined the pool relying on the stop-loss have no on-chain recourse once `drawdownE6 == 0` is committed; all subsequent swaps proceed regardless of how far the per-share value has fallen. This constitutes broken core pool functionality causing potential loss of LP principal.

---

### Likelihood Explanation

Two paths exist:

1. **At deployment:** The factory passes `timelock = 0` in the `initialize` call. No factory-level validation prevents this. Any pool created with this extension and `timelock = 0` is immediately vulnerable.
2. **Post-deployment:** A pool admin with an existing non-zero timelock proposes `newTimelock = 0`, waits the current timelock period, executes the change, then immediately proposes and executes `drawdownE6 = 0` in a single block.

Path 1 requires no waiting and is reachable at pool creation. Path 2 requires the admin to wait one timelock cycle, but once `timelock == 0` is committed, all future parameter changes are instant and irreversible without another timelock cycle.

---

### Recommendation

1. Enforce a non-zero minimum timelock at `initialize` and in `proposeOracleStopLossTimelock`. A reasonable floor (e.g., `MIN_TIMELOCK = 1 days`) should be a contract constant.
2. Reject `drawdownE6 == 0` in `_validateDrawdown` (or treat it as "disabled" only if explicitly documented and gated separately), so the stop-loss cannot be silently neutered via a parameter change.

```solidity
uint32 private constant MIN_TIMELOCK = 1 days;

function _validateTimelock(uint32 timelock) private pure {
    if (timelock < MIN_TIMELOCK) revert OracleStopLossTimelockTooShort(timelock);
}
```

Apply `_validateTimelock` in both `initialize` and `executeOracleStopLossTimelock`.

---

### Proof of Concept

```solidity
// Pool deployed with timelock = 0 at initialization
extension.initialize(pool, abi.encode(uint32(100_000), uint32(58), uint32(0)));
// timelock == 0 → _afterTimelock returns block.timestamp

// Admin proposes drawdown = 0 (passes _validateDrawdown since 0 <= 1e6)
vm.prank(admin);
extension.proposeOracleStopLossDrawdown(pool, 0);
// executeAfter == block.timestamp → _requireElapsed passes immediately

// Admin executes in the same block
vm.prank(admin);
extension.executeOracleStopLossDrawdown(pool);

// drawdownE6 == 0 → _afterSwapOracleStopLoss returns on line 217 for every swap
// Stop-loss is permanently disabled; no swap will ever revert for value drain
```

### Citations

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L56-62)
```text
    (uint32 drawdownE6, uint32 decayPerSecondE8, uint32 timelock) = abi.decode(data, (uint32, uint32, uint32));
    _validateDrawdown(drawdownE6);
    _validateDecay(decayPerSecondE8);

    oracleStopLossConfig[pool] = PoolStopLossConfig({
      drawdownE6: drawdownE6, decayPerSecondE8: decayPerSecondE8, timelock: timelock, initialized: true
    });
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L78-84)
```text
  function proposeOracleStopLossTimelock(address pool_, uint32 newTimelock) external onlyPoolAdmin(pool_) {
    PoolStopLossSchedule storage sched = _initializedSchedule(pool_);
    uint32 executeAfter = _afterTimelock(pool_);
    sched.pendingTimelock = newTimelock;
    sched.pendingTimelockExecuteAfter = executeAfter;
    emit OracleStopLossTimelockProposed(pool_, newTimelock, executeAfter);
  }
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L216-217)
```text
    uint256 drawdown = cfg.drawdownE6;
    if (drawdown == 0) return;
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L297-299)
```text
  function _afterTimelock(address pool_) private view returns (uint32) {
    return uint32(block.timestamp + oracleStopLossConfig[pool_].timelock);
  }
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L301-303)
```text
  function _requireElapsed(uint32 executeAfter) private view {
    if (block.timestamp < executeAfter) revert OracleStopLossTimelockNotElapsed(executeAfter, block.timestamp);
  }
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L305-307)
```text
  function _validateDrawdown(uint256 drawdownE6) private pure {
    if (drawdownE6 > E6) revert OracleStopLossDrawdownTooLarge(drawdownE6);
  }
```
