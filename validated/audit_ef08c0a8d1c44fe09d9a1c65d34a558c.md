### Title
Missing `timelock` Validation in `OracleValueStopLossExtension.initialize()` and `proposeOracleStopLossTimelock()` Allows Pool Admin to Instantly Bypass LP Protection Timelock - (File: metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol)

### Summary
`OracleValueStopLossExtension.initialize()` validates `drawdownE6` and `decayPerSecondE8` but does not validate the `timelock` parameter. `proposeOracleStopLossTimelock()` similarly accepts any `uint32` value with no lower-bound check. A pool initialized with `timelock = 0`, or one whose admin reduces the timelock to zero over time, allows the pool admin to propose and execute drawdown/decay changes in the same block, collapsing the LP-protection delay to zero.

### Finding Description

The NatSpec of `OracleValueStopLossExtension` explicitly states: *"Drawdown and decay changes are timelocked so LPs can react."* The timelock is the sole mechanism that gives LPs time to exit before the admin can weaken or disable the stop-loss.

**`initialize()` — no timelock validation:**

```solidity
// metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol L56-62
(uint32 drawdownE6, uint32 decayPerSecondE8, uint32 timelock) = abi.decode(data, (uint32, uint32, uint32));
_validateDrawdown(drawdownE6);   // ✓ validated
_validateDecay(decayPerSecondE8); // ✓ validated
// timelock — NOT validated, can be 0
oracleStopLossConfig[pool] = PoolStopLossConfig({
    drawdownE6: drawdownE6, decayPerSecondE8: decayPerSecondE8, timelock: timelock, initialized: true
});
``` [1](#0-0) 

**`proposeOracleStopLossTimelock()` — no lower-bound check on `newTimelock`:**

```solidity
// L78-84
function proposeOracleStopLossTimelock(address pool_, uint32 newTimelock) external onlyPoolAdmin(pool_) {
    PoolStopLossSchedule storage sched = _initializedSchedule(pool_);
    uint32 executeAfter = _afterTimelock(pool_);   // block.timestamp + currentTimelock
    sched.pendingTimelock = newTimelock;

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
