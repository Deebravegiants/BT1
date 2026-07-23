Audit Report

## Title
Missing Zero-Address Check for `owner` in `addLiquidity()` Permanently Locks Deposited Tokens — (File: metric-core/contracts/MetricOmmPool.sol)

## Summary
`MetricOmmPool.addLiquidity` accepts an `owner` parameter with no zero-address guard. If `owner == address(0)` is passed, the pool invokes the callback, accepts real token transfers, and keys LP shares under `_positionBinShares[keccak256(abi.encode(address(0), salt, binIdx))]`. Because `removeLiquidity` enforces `msg.sender != owner` and `msg.sender` can never equal `address(0)` in the EVM, the deposited tokens are permanently irrecoverable. The only zero-address guard (`InvalidPositionOwner`) exists exclusively in the periphery and does not protect direct callers of the core pool.

## Finding Description
`MetricOmmPool.addLiquidity` (L182–196) passes `owner` directly to `LiquidityLib.addLiquidity` with no validation: [1](#0-0) 

Inside `LiquidityLib.addLiquidity`, the position key is computed as `keccak256(abi.encode(owner, salt, bin))` (L72, L258), shares are written to `positionBinShares[posKey]` (L121), `binState.token0/1BalanceScaled` and `binTotals.scaledToken0/1` are updated (L114, L118, L135, L138), and the callback is invoked to pull real tokens from `msg.sender` (L147–154): [2](#0-1) 

`removeLiquidity` then enforces: [3](#0-2) 

Since `msg.sender` is never `address(0)` in the EVM, any position minted to `address(0)` is permanently irremovable. The `InvalidPositionOwner` guard exists only in `MetricOmmPoolLiquidityAdder._validateOwner`: [4](#0-3) 

A grep across all `metric-core` Solidity files confirms zero occurrences of `InvalidPositionOwner` or any `owner != address(0)` check in the core pool path.

## Impact Explanation
Any contract that calls `MetricOmmPool.addLiquidity` with `owner == address(0)` will transfer real token amounts into the pool via callback settlement. The pool's `binTotals` and `_binStates` correctly account for the tokens, but no address can ever call `removeLiquidity` to reclaim them — `msg.sender != address(0)` is an EVM invariant. This is a direct, irreversible loss of user principal with no recovery path, matching the "direct loss of user principal" allowed impact.

## Likelihood Explanation
Low. The caller must explicitly pass `address(0)` as `owner`. However, `MetricOmmPool` is a public `external` contract callable by any contract, not only the official periphery. Integrators building custom periphery contracts or calling the core pool directly may omit the zero-address check that the official periphery provides. The condition is repeatable and requires no privileged access.

## Recommendation
Add a zero-address guard at the top of `addLiquidity` in `metric-core/contracts/MetricOmmPool.sol`:

```solidity
function addLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (uint256 amount0Added, uint256 amount1Added) {
+   if (owner == address(0)) revert InvalidPositionOwner();
    if (deltas.binIdxs.length == 0) return (0, 0);
    ...
}
```

The `InvalidPositionOwner` error already exists in the periphery interface and can be declared in the core pool's error set.

## Proof of Concept
1. Deploy a contract `Attacker` implementing `metricOmmModifyLiquidityCallback` that transfers tokens to the pool on callback.
2. Approve the pool for token0 and token1 from `Attacker`.
3. Call `MetricOmmPool.addLiquidity(address(0), salt, deltas, callbackData, "")` from `Attacker`.
4. Observe: callback fires, tokens transfer, `_positionBinShares[keccak256(abi.encode(address(0), salt, binIdx))]` is set, `binTotals.scaledToken0/1` increases.
5. Attempt `MetricOmmPool.removeLiquidity(address(0), salt, deltas, "")` from any EOA or contract — reverts with `NotPositionOwner()` because `msg.sender != address(0)`.
6. Tokens are permanently locked; no recovery path exists.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L188-195)
```text
  ) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (uint256 amount0Added, uint256 amount1Added) {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    _beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Added, amount1Added) = LiquidityLib.addLiquidity(
      _liquidityContext(), owner, salt, deltas, callbackData, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterAddLiquidity(msg.sender, owner, salt, deltas, amount0Added, amount1Added, extensionData);
```

**File:** metric-core/contracts/MetricOmmPool.sol (L206-206)
```text
    if (msg.sender != owner) revert NotPositionOwner();
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L144-155)
```text
      if (amount0Added > 0 || amount1Added > 0) {
        uint256 balance0Before = IERC20(ctx.token0).balanceOf(address(this));
        uint256 balance1Before = IERC20(ctx.token1).balanceOf(address(this));
        IMetricOmmModifyLiquidityCallback(msg.sender)
          .metricOmmModifyLiquidityCallback(amount0Added, amount1Added, callbackData);
        if (amount0Added > 0 && balance0Before + amount0Added > IERC20(ctx.token0).balanceOf(address(this))) {
          revert IMetricOmmPoolActions.InsufficientTokenBalance();
        }
        if (amount1Added > 0 && balance1Before + amount1Added > IERC20(ctx.token1).balanceOf(address(this))) {
          revert IMetricOmmPoolActions.InsufficientTokenBalance();
        }
      }
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L247-249)
```text
  function _validateOwner(address owner) internal pure {
    if (owner == address(0)) revert InvalidPositionOwner();
  }
```
