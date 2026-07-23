### Title
Missing `owner != address(0)` Validation in `MetricOmmPool.addLiquidity()` Permanently Locks LP Tokens — (`metric-core/contracts/MetricOmmPool.sol`)

---

### Summary

`MetricOmmPool.addLiquidity()` accepts an arbitrary `owner` address without validating it is non-zero. The periphery contract `MetricOmmPoolLiquidityAdder` enforces this check, but the pool itself does not. A caller who invokes the pool directly with `owner = address(0)` will have their tokens pulled via the callback and permanently locked, because `removeLiquidity` enforces `msg.sender == owner`, making the position irrecoverable.

---

### Finding Description

`MetricOmmPool.addLiquidity()` performs only two structural checks before proceeding: [1](#0-0) 

```solidity
function addLiquidity(
  address owner,
  ...
) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (...) {
  if (deltas.binIdxs.length == 0) return (0, 0);
  if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
  // ← no check: owner != address(0)
  ...
  (amount0Added, amount1Added) = LiquidityLib.addLiquidity(
    _liquidityContext(), owner, salt, deltas, callbackData, ...
  );
```

There is no `require(owner != address(0))` guard. The position is keyed by `(owner, salt, bin)` in `_positionBinShares`, so a zero-address owner creates a valid but permanently inaccessible position.

`removeLiquidity` enforces a strict ownership check: [2](#0-1) 

```solidity
if (msg.sender != owner) revert NotPositionOwner();
```

Since no EOA or contract can act as `address(0)`, the position can never be removed and the deposited tokens are permanently locked in the pool.

The periphery `MetricOmmPoolLiquidityAdder` does enforce this invariant: [3](#0-2) 

```solidity
function _validateOwner(address owner) internal pure {
  if (owner == address(0)) revert InvalidPositionOwner();
}
```

This guard is called in `addLiquidityExactShares` and `addLiquidityWeighted`: [4](#0-3) 

But it is absent from the pool itself. Any caller that bypasses the periphery and calls `pool.addLiquidity(address(0), ...)` directly will lose their tokens.

---

### Impact Explanation

A caller who passes `owner = address(0)` to `MetricOmmPool.addLiquidity()` directly:

1. Triggers the `metricOmmModifyLiquidityCallback`, which pulls real token0 and/or token1 from the payer.
2. Records the position under key `(address(0), salt, bin)` in `_positionBinShares` and `_binTotalShares`.
3. Can never recover the tokens — `removeLiquidity` requires `msg.sender == address(0)`, which is impossible.

The deposited tokens are permanently locked in the pool. This is a direct loss of LP principal with no recovery path.

---

### Likelihood Explanation

The pool is a public contract. Any integrator, router, or user who calls `addLiquidity` directly (without routing through `MetricOmmPoolLiquidityAdder`) is exposed. Buggy integrations, front-end errors, or direct contract calls can all trigger this path. The periphery's guard is not enforced at the core layer, creating a silent invariant gap.

---

### Recommendation

Add a zero-address check for `owner` directly in `MetricOmmPool.addLiquidity()`, mirroring the periphery guard:

```diff
  function addLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
  ) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (uint256 amount0Added, uint256 amount1Added) {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
+   if (owner == address(0)) revert InvalidPositionOwner();
    ...
```

---

### Proof of Concept

1. Attacker (or buggy integrator) calls `pool.addLiquidity(address(0), salt, deltas, callbackData, "")` directly.
2. The pool passes all structural checks (non-empty deltas, matching lengths).
3. `LiquidityLib.addLiquidity` is called; the callback fires and pulls token0/token1 from `msg.sender`.
4. Position shares are recorded under `_positionBinShares[keccak256(abi.encode(address(0), salt, bin))]`.
5. Any subsequent call to `pool.removeLiquidity(address(0), salt, deltas, "")` reverts with `NotPositionOwner` because `msg.sender != address(0)`.
6. The deposited tokens remain in the pool forever with no recovery mechanism.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L188-196)
```text
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

**File:** metric-core/contracts/MetricOmmPool.sol (L206-206)
```text
    if (msg.sender != owner) revert NotPositionOwner();
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L65-67)
```text
    _validateOwner(owner);
    _validateDeltas(deltas);
    return _addLiquidity(pool, owner, salt, deltas, msg.sender, maxAmountToken0, maxAmountToken1, extensionData);
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L247-249)
```text
  function _validateOwner(address owner) internal pure {
    if (owner == address(0)) revert InvalidPositionOwner();
  }
```
