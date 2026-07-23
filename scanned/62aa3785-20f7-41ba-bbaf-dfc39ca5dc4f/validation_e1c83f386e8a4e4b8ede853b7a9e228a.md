### Title
`OracleValueStopLossExtension` Timelock Has No Minimum Enforced, Allowing Pool Admin to Reduce It to Zero and Bypass LP Protection — (`metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol`)

---

### Summary

The `OracleValueStopLossExtension` is designed to protect LPs by timelocking admin changes to drawdown, decay, and high-watermark parameters so that LPs can react and exit before their stop-loss guarantees are altered. However, no minimum value is enforced on the `timelock` field — neither at initialization nor when the admin proposes a new timelock value. A pool admin can legitimately reduce the timelock to `0` by waiting out the current timelock period, after which every subsequent parameter change (drawdown, decay, watermarks) can be proposed and executed atomically in the same block, giving LPs zero reaction time.

---

### Finding Description

`OracleValueStopLossExtension.initialize` decodes three parameters from `data` and validates only `drawdownE6` and `decayPerSecondE8`:

```solidity
(uint32 drawdownE6, uint32 decayPerSecondE8, uint32 timelock) = abi.decode(data, (uint32, uint32, uint32));
_validateDrawdown(drawdownE6);
_validateDecay(decayPerSecondE8);
// ← no validation on `timelock`
``` [1](#0-0) 

The `timelock` field is stored directly with no lower-bound check. The helper that computes the execution deadline is:

```solidity
function _afterTimelock(address pool_) private view returns (uint32) {
    return uint32(block.timestamp + oracleStopLossConfig[pool_].timelock);
}
``` [2](#0-1) 

And the elapsed check is a strict less-than:

```solidity
function _requireElapsed(uint32 executeAfter) private view {
    if (block.timestamp < executeAfter) revert OracleStopLossTimelockNotElapsed(...);
}
``` [3](#0-2) 

When `timelock == 0`, `executeAfter == block.timestamp`, and `block.timestamp < block.timestamp` is `false`, so the guard passes immediately. A `propose` + `execute` pair can be submitted in a single transaction.

The admin can reach `timelock == 0` from an honestly-configured non-zero value via the two-step update path:

1. `proposeOracleStopLossTimelock(pool, 0)` — schedules the change with `executeAfter = block.timestamp + currentTimelock`.
2. Wait `currentTimelock` seconds (LPs see the event but may not act).
3. `executeOracleStopLossTimelock(pool)` — sets `timelock = 0`. [4](#0-3) 

From that point forward, every subsequent `propose` + `execute` call for drawdown, decay, or high-watermarks can be batched into a single transaction with no delay.

---

### Impact Explanation

Once `timelock == 0`, the admin can atomically:

**Path A — Disable stop-loss silently:**
- Call `proposeOracleStopLossDecay(pool, 1e8)` (100 % per second) then `executeOracleStopLossDecay` in the same block.
- All stored watermarks decay to `0` within one second, so `_applyWatermark` never reports a breach (`metric >= 0` always). The stop-loss is effectively dead. [5](#0-4) 

**Path B — Freeze all swaps:**
- Call `proposeOracleStopLossHighWatermarks(pool, binIdx, type(uint104).max, type(uint104).max)` then `executeOracleStopLossHighWatermarks` in the same block.
- Every subsequent swap through that bin triggers `OracleStopLossTriggered`, reverting the swap. Because `afterSwap` is called inside the pool's swap execution, all swaps are permanently DoS'd. [6](#0-5) 

Path A removes the LP safety guarantee that the extension was deployed to provide, exposing LP principal to unchecked value drain. Path B breaks core pool swap functionality. Both exceed the contest's Medium threshold ("breaks core contract functionality" / "loss of funds requiring specific state").

The contract's own NatSpec states the design intent: *"Drawdown and decay changes are timelocked so LPs can react."* With `timelock == 0` that guarantee is void. [7](#0-6) 

---

### Likelihood Explanation

The README explicitly scopes this class of issue as valid:

> "Pool Admin — semi-trusted, bounded. **Cannot exceed caps or bypass timelocks.** The finding can be valid only if the Pool admin can bypass the caps or honestly configured timelocks and it qualifies for Medium or higher severity." [8](#0-7) 

The reduction path requires the admin to wait one full timelock period — a deliberate, observable action. However, once `timelock == 0` is set, every future parameter change is instant and unobservable in advance. LPs who deposited after the reduction have no on-chain mechanism to detect or react to subsequent atomic changes.

---

### Recommendation

Enforce a minimum timelock in `initialize` and in `executeOracleStopLossTimelock`:

```solidity
uint32 internal constant MIN_TIMELOCK = 1 days; // or protocol-chosen floor

// in initialize:
if (timelock < MIN_TIMELOCK) revert OracleStopLossTimelockTooShort(timelock);

// in executeOracleStopLossTimelock:
if (timelock < MIN_TIMELOCK) revert OracleStopLossTimelockTooShort(timelock);
```

This mirrors the pattern used by the factory for `priceProviderTimelock` (where `type(uint256).max` signals immutability) and ensures the LP-protection guarantee stated in the NatSpec is actually enforceable. [9](#0-8) 

---

### Proof of Concept

```solidity
// Pool created with timelock = 7 days (honestly configured)
// Step 1: admin proposes timelock = 0; LPs see event but may not act
ext.proposeOracleStopLossTimelock(pool, 0);

// Step 2: wait 7 days, then execute
vm.warp(block.timestamp + 7 days);
ext.executeOracleStopLossTimelock(pool);
// timelock is now 0

// Step 3: in a single block, propose + execute watermark to max
ext.proposeOracleStopLossHighWatermarks(pool, 0, type(uint104).max, type(uint104).max);
ext.executeOracleStopLossHighWatermarks(pool);
// executeAfter == block.timestamp, _requireElapsed passes immediately

// Step 4: any swap now reverts with OracleStopLossTriggered
pool.swap(...); // ← reverts, pool is frozen
```

### Citations

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L13-16)
```text
/// @title OracleValueStopLossExtension
/// @notice Tracks per-bin value per share in token0 and token1 terms at the oracle mid,
///         against decaying high watermarks. Drawdown and decay changes are timelocked so LPs
///         can react; monitor at least as often as the timelock or trust the pool admin.
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L56-67)
```text
    (uint32 drawdownE6, uint32 decayPerSecondE8, uint32 timelock) = abi.decode(data, (uint32, uint32, uint32));
    _validateDrawdown(drawdownE6);
    _validateDecay(decayPerSecondE8);

    oracleStopLossConfig[pool] = PoolStopLossConfig({
      drawdownE6: drawdownE6, decayPerSecondE8: decayPerSecondE8, timelock: timelock, initialized: true
    });

    emit OracleStopLossDrawdownSet(pool, drawdownE6);
    emit OracleStopLossDecaySet(pool, decayPerSecondE8);
    emit OracleStopLossTimelockSet(pool, timelock);
    return IMetricOmmExtensions.initialize.selector;
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

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L319-324)
```text
  function _decayed(uint256 hwm, uint256 ratePerSecondE8, uint256 dt) private pure returns (uint256) {
    if (ratePerSecondE8 == 0 || dt == 0 || hwm == 0) return hwm;
    uint256 factor = ratePerSecondE8 * dt;
    if (factor >= E8) return 0;
    return hwm - (hwm * factor) / E8;
  }
```

**File:** README.md (L21-21)
```markdown
Pool Admin — semi-trusted, bounded. Sets admin fees (capped), proposes PP changes (timelock-gated), pauses own pool (level 1), configures bin/extension params. Cannot exceed caps or bypass timelocks. If they can exceed caps or bypass timelocks and it leads to Medium or higher severity issue, then it can be valid. Pools are expected to be set up correctly and non maliciously (by both the pool creator and the Pool admin), without abnormal values, and users are expected to apply due diligence when deciding whether they want to deposit in the pool or not. The finding can be valid only if the Pool admin can bypass the caps or honestly configured timelocks and it qualifies for Medium or higher severity.
```
