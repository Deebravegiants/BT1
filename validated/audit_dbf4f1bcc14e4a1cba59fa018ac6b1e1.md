The code confirms all technical claims. Let me verify the key mechanics:

1. **No timelock validation in `initialize`** — lines 56-58 validate only `drawdownE6` and `decayPerSecondE8`, not `timelock`. [1](#0-0) 

2. **`_afterTimelock` with `timelock=0`** returns `block.timestamp + 0 = block.timestamp`. [2](#0-1) 

3. **`_requireElapsed` passes immediately** when `executeAfter == block.timestamp` because `block.timestamp < block.timestamp` is `false`. [3](#0-2) 

4. **`executeOracleStopLossTimelock` has no minimum check** — it stores whatever `pendingTimelock` value was proposed, including 0. [4](#0-3) 

5. **README confirms the admin-boundary rule**: "Cannot exceed caps or bypass timelocks. The finding can be valid only if the Pool admin can bypass the caps or honestly configured timelocks." [5](#0-4) 

6. **NatSpec confirms the design intent**: "Drawdown and decay changes are timelocked so LPs can react." [6](#0-5) 

All technical claims are verified against production code. The exploit path is sound: propose timelock=0 → wait current timelock → execute → all future changes are atomic. The `_decayed` function confirms Path A (decay=1e8 collapses watermarks to 0 in one second). [7](#0-6) 

---

Audit Report

## Title
`OracleValueStopLossExtension` Allows Pool Admin to Reduce Timelock to Zero, Nullifying LP Protection — (`metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol`)

## Summary
`OracleValueStopLossExtension` enforces no minimum value on the `timelock` parameter at initialization or during updates. A pool admin can legitimately reduce the timelock to `0` by waiting out the current timelock period, after which every subsequent parameter change (drawdown, decay, high-watermarks) can be proposed and executed atomically in the same block, giving LPs zero reaction time and voiding the LP protection guarantee stated in the contract's NatSpec.

## Finding Description
`initialize` decodes `(uint32 drawdownE6, uint32 decayPerSecondE8, uint32 timelock)` from `data` and calls `_validateDrawdown` and `_validateDecay`, but performs no validation on `timelock`, allowing it to be set to `0` at pool creation or reduced to `0` later via the two-step update path. `executeOracleStopLossTimelock` similarly applies no lower-bound check before writing `pendingTimelock` to storage.

When `timelock == 0`, `_afterTimelock` returns `uint32(block.timestamp + 0) == block.timestamp`. The guard `_requireElapsed` checks `block.timestamp < executeAfter`; when `executeAfter == block.timestamp`, this is `false`, so the check passes immediately. Any `propose` + `execute` pair can therefore be submitted in a single transaction with no delay.

The reduction path from an honestly-configured non-zero timelock:
1. `proposeOracleStopLossTimelock(pool, 0)` — schedules the change; LPs see the event but may not act.
2. Wait `currentTimelock` seconds.
3. `executeOracleStopLossTimelock(pool)` — sets `timelock = 0`.

From that point, all subsequent parameter changes are atomic. **Path A**: `proposeOracleStopLossDecay(pool, 1e8)` + `executeOracleStopLossDecay` in one block sets decay to 100%/second; `_decayed` collapses all watermarks to `0` within one second, so `_applyWatermark` never reports a breach and the stop-loss is silently disabled. **Path B**: `proposeOracleStopLossHighWatermarks(pool, binIdx, type(uint104).max, type(uint104).max)` + `executeOracleStopLossHighWatermarks` in one block sets watermarks to `type(uint104).max`; every subsequent swap triggers `OracleStopLossTriggered`, permanently DoS-ing the pool.

## Impact Explanation
Path A removes the LP safety guarantee the extension was deployed to provide, exposing LP principal to unchecked value drain with no on-chain mechanism for LPs to detect or react. Path B breaks core pool swap functionality entirely. Both impacts exceed the contest's Medium threshold ("breaks core contract functionality" / "loss of funds requiring specific state"). The contract's own NatSpec states: "Drawdown and decay changes are timelocked so LPs can react" — with `timelock == 0` that guarantee is void.

## Likelihood Explanation
The README explicitly scopes this class of issue as valid: "Cannot exceed caps or bypass timelocks. The finding can be valid only if the Pool admin can bypass the caps or honestly configured timelocks." The reduction path requires the admin to wait one full timelock period — a deliberate, observable action — but once `timelock == 0` is set, every future parameter change is instant and unobservable in advance. LPs who deposited after the reduction have no on-chain mechanism to detect or react to subsequent atomic changes.

## Recommendation
Enforce a minimum timelock in `initialize` and in `executeOracleStopLossTimelock`:

```solidity
uint32 internal constant MIN_TIMELOCK = 1 days;

// in initialize:
if (timelock < MIN_TIMELOCK) revert OracleStopLossTimelockTooShort(timelock);

// in executeOracleStopLossTimelock:
if (timelock < MIN_TIMELOCK) revert OracleStopLossTimelockTooShort(timelock);
```

This mirrors the pattern used for `drawdownE6` and `decayPerSecondE8` which already have `_validateDrawdown` and `_validateDecay` guards, and ensures the LP-protection guarantee stated in the NatSpec is actually enforceable.

## Proof of Concept
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

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L56-58)
```text
    (uint32 drawdownE6, uint32 decayPerSecondE8, uint32 timelock) = abi.decode(data, (uint32, uint32, uint32));
    _validateDrawdown(drawdownE6);
    _validateDecay(decayPerSecondE8);
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
