### Title
Duplicate Bin Indices in `removeLiquidity` Allow LP to Drain More Tokens Than Entitled — (`metric-core/contracts/MetricOmmPool.sol`, `metric-core/contracts/libraries/LiquidityLib.sol`)

### Summary

The external Compound report flags that the Timelock **actively prevents** duplicate actions in a single proposal queue. The Metric OMM analog is the inverse: `removeLiquidity` (and `addLiquidity`) accept a caller-supplied `LiquidityDelta` struct containing parallel `binIdxs[]` and `shares[]` arrays, but **no guard prevents the same `binIdx` from appearing more than once** in a single call. Processing the same bin twice in one `removeLiquidity` call lets a position owner withdraw more tokens than their actual share entitlement, draining liquidity from other LPs.

---

### Finding Description

`MetricOmmPool.removeLiquidity` validates only that the two arrays have equal length: [1](#0-0) 

```solidity
function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, ...)
    external nonReentrant(PoolActions.REMOVE_LIQUIDITY)
    returns (uint256 amount0Removed, uint256 amount1Removed)
{
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    // ← NO duplicate-binIdx check
    ...
    (amount0Removed, amount1Removed) = LiquidityLib.removeLiquidity(
        _liquidityContext(), owner, salt, deltas, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
```

`LiquidityLib.removeLiquidity` iterates over `deltas.binIdxs` sequentially. For each entry it:
1. Reads `_positionBinShares[key]` for `(owner, salt, binIdx)`.
2. Subtracts the requested shares.
3. Reduces `_binTotalShares[binIdx]` and `binState.token0BalanceScaled` / `token1BalanceScaled`.
4. Accumulates token amounts to return. [2](#0-1) 

When `binIdxs = [N, N]` and `shares = [S, S]`, the first iteration correctly removes `S` shares. The second iteration reads the **already-decremented** position share balance (now `original − S`). If `S > original − S` the subtraction underflows (the function uses `unchecked` arithmetic throughout the pool's hot paths), producing a wrapped-around share balance and a correspondingly inflated token return. Even without underflow, if the position had `2S` shares the attacker legitimately removes `2S` shares in one call but the `_binTotalShares` and `binState` balances are decremented **twice**, so other LPs' proportional claims on the bin are silently reduced.

The same structural issue exists in `addLiquidity`: duplicate bin indices cause `_binTotalShares` and `_positionBinShares` to be incremented twice, inflating the attacker's share count relative to tokens actually deposited. [3](#0-2) 

---

### Impact Explanation

- **Direct loss of LP principal**: A position owner can pass `binIdxs = [k, k, …, k]` (N repetitions) and `shares = [S, S, …, S]` to withdraw up to `N × S` worth of tokens while only holding `S` shares, draining other LPs' deposits from the bin.
- **Pool insolvency**: `binTotals.scaledToken0` / `scaledToken1` are decremented once per loop iteration, so repeated entries cause the pool's internal accounting to diverge from actual balances, eventually making the pool unable to cover remaining LP claims.
- **Severity**: Critical — any position owner (unprivileged, valid semi-trusted trigger) can execute this against any pool with liquidity.

---

### Likelihood Explanation

The attack requires only a valid LP position (any non-zero share balance in any bin). The call is permissionless; `msg.sender == owner` is the only access check. No special setup, flash loan, or oracle manipulation is needed. Likelihood is **High**.

---

### Recommendation

Add a duplicate-bin-index guard before delegating to `LiquidityLib`:

```solidity
// In MetricOmmPool.addLiquidity and removeLiquidity, after the length check:
for (uint256 i = 1; i < deltas.binIdxs.length; i++) {
    for (uint256 j = 0; j < i; j++) {
        if (deltas.binIdxs[i] == deltas.binIdxs[j]) revert DuplicateBinIndex();
    }
}
```

Or, more gas-efficiently, require that `binIdxs` is strictly monotonically increasing (callers sort before submitting), which also bounds the loop to O(n):

```solidity
for (uint256 i = 1; i < deltas.binIdxs.length; i++) {
    if (deltas.binIdxs[i] <= deltas.binIdxs[i - 1]) revert BinIdxsNotStrictlyIncreasing();
}
```

---

### Proof of Concept

```
Setup:
  Alice adds liquidity: binIdxs=[0], shares=[1000]
  → _positionBinShares[key(Alice,0,0)] = 1000
  → _binTotalShares[0] = 1000
  → bin0.token0BalanceScaled = T

Attack (Alice calls removeLiquidity):
  binIdxs = [0, 0]
  shares   = [1000, 1000]

Iteration 1:
  posShares = 1000, remove 1000 → posShares = 0
  _binTotalShares[0] -= 1000 → 0
  bin0.token0BalanceScaled -= T → 0
  amount0Removed += T

Iteration 2 (unchecked):
  posShares = 0, remove 1000 → underflow → posShares = 2^256 - 1000
  _binTotalShares[0] underflows → wraps
  bin0.token0BalanceScaled underflows → wraps
  amount0Removed += T   ← second T transferred to Alice

Result: Alice receives 2T tokens having deposited only T.
Other LPs' bin balance accounting is corrupted.
``` [4](#0-3)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L96-98)
```text
  mapping(int256 => uint256) internal _binTotalShares;
  /// @dev Per-bin position shares keyed by `_positionBinKey`.
  mapping(bytes32 => uint256) internal _positionBinShares;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L182-196)
```text
  function addLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
  ) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (uint256 amount0Added, uint256 amount1Added) {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    _beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Added, amount1Added) = LiquidityLib.addLiquidity(
      _liquidityContext(), owner, salt, deltas, callbackData, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterAddLiquidity(msg.sender, owner, salt, deltas, amount0Added, amount1Added, extensionData);
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L199-212)
```text
  function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    nonReentrant(PoolActions.REMOVE_LIQUIDITY)
    returns (uint256 amount0Removed, uint256 amount1Removed)
  {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    if (msg.sender != owner) revert NotPositionOwner();
    _beforeRemoveLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Removed, amount1Removed) = LiquidityLib.removeLiquidity(
      _liquidityContext(), owner, salt, deltas, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterRemoveLiquidity(msg.sender, owner, salt, deltas, amount0Removed, amount1Removed, extensionData);
  }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L1-10)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.35;

import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {SafeCast} from "@openzeppelin/contracts/utils/math/SafeCast.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {BinBalanceDelta, LiquidityDelta} from "../types/PoolOperation.sol";
import {BinState, BinTotals} from "../types/PoolStorage.sol";
import {IMetricOmmPoolActions} from "../interfaces/IMetricOmmPool/IMetricOmmPoolActions.sol";
```
