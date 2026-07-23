### Title
Unvalidated `owner` Parameter in `MetricOmmPool.addLiquidity()` Permanently Locks LP Funds — (`metric-core/contracts/MetricOmmPool.sol`)

### Summary

`MetricOmmPool.addLiquidity()` accepts an arbitrary `owner` address with no zero-address guard. Passing `owner = address(0)` pulls real tokens from the caller via the modify-liquidity callback, credits the position to `address(0)`, and permanently locks those tokens because `removeLiquidity()` enforces `msg.sender == owner`, which can never be satisfied for the zero address.

### Finding Description

`MetricOmmPool.addLiquidity()` is a permissionless function that separates the payer (`msg.sender`) from the position owner (`owner`), enabling an operator pattern. The pool performs no validation that `owner != address(0)`: [1](#0-0) 

Inside `LiquidityLib.addLiquidity`, the position key is derived directly from the supplied `owner`: [2](#0-1) 

Shares are written to `positionBinShares[_positionBinKey(address(0), salt, binIdx)]` and `binTotals` is incremented. The callback then pulls real tokens from `msg.sender`: [3](#0-2) 

Recovery is impossible because `removeLiquidity()` enforces: [4](#0-3) 

`msg.sender` can never equal `address(0)`, so the position can never be burned and the underlying tokens are permanently stranded in the pool.

The periphery wrapper `MetricOmmPoolLiquidityAdder` does guard against this: [5](#0-4) 

But the core pool is a public contract callable directly by any EOA or contract, and the guard is absent there.

### Impact Explanation

Any tokens deposited under `owner = address(0)` are irrecoverably locked. The pool's `binTotals` and `binTotalShares` are incremented, so the tokens appear as LP-owned liquidity, but no address can ever call `removeLiquidity` to reclaim them. This is a direct, permanent loss of user principal with no on-chain recovery path.

### Likelihood Explanation

The operator pattern (`msg.sender` pays, `owner` receives the position) is an explicitly documented and intended feature. Any integrator or user who calls the core pool directly and omits or zero-initialises the `owner` argument loses their deposit. The periphery's guard demonstrates the protocol is aware of the risk but the protection is not enforced at the authoritative layer. Likelihood is low-medium: it requires a direct core-pool call, but the operator pattern makes it a realistic integration mistake.

### Recommendation

Add a zero-address check in `MetricOmmPool.addLiquidity()` before delegating to `LiquidityLib`:

```solidity
function addLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (uint256 amount0Added, uint256 amount1Added) {
    if (owner == address(0)) revert InvalidPositionOwner(); // add this guard
    if (deltas.binIdxs.length == 0) return (0, 0);
    ...
}
```

This mirrors the guard already present in `MetricOmmPoolLiquidityAdder._validateOwner()` and closes the gap at the authoritative layer.

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

// Assume pool is deployed with token0/token1, caller has approved the pool callback.
// Caller implements IMetricOmmModifyLiquidityCallback and holds token0.

contract PoC is IMetricOmmModifyLiquidityCallback {
    function exploit(address pool, address token0) external {
        int256[] memory bins = new int256[](1);
        bins[0] = 4; // above-price bin, requires token0 only
        uint256[] memory shares = new uint256[](1);
        shares[0] = 100_000;

        LiquidityDelta memory d = LiquidityDelta({binIdxs: bins, shares: shares});

        // owner = address(0): tokens pulled from this contract, position credited to zero address
        IMetricOmmPoolActions(pool).addLiquidity(address(0), 0, d, "", "");

        // Tokens are now locked. No address can call removeLiquidity for owner=address(0).
    }

    function metricOmmModifyLiquidityCallback(uint256 a0, uint256 a1, bytes calldata) external override {
        PoolImmutables memory imm = IMetricOmmPool(msg.sender).getImmutables();
        if (a0 > 0) IERC20(imm.token0).transfer(msg.sender, a0);
        if (a1 > 0) IERC20(imm.token1).transfer(msg.sender, a1);
    }
}
```

After `exploit()` completes, `positionBinShares[keccak256(abi.encode(address(0), uint80(0), int8(4)))]` holds the minted shares, `binTotals.scaledToken0` is increased, and the deposited token0 is permanently stranded.

### Citations

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

**File:** metric-core/contracts/MetricOmmPool.sol (L206-206)
```text
    if (msg.sender != owner) revert NotPositionOwner();
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L70-76)
```text
          // safe because -128 <= LOWEST_BIN <= HIGHEST_BIN <= 127 (enforced by factory)
          // forge-lint: disable-next-line(unsafe-typecast)
          bytes32 posKey = _positionBinKey(owner, salt, int8(binIdx));
          uint256 binTotalSharesVal = binTotalShares[binIdx];
          uint256 userShares = positionBinShares[posKey];

          uint256 newUserShares = userShares + sharesToAdd;
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L108-120)
```text
          } else {
            amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
            amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
          }
          if (amount0Scaled > 0) {
            totalToken0ToAddScaled += amount0Scaled;
            binState.token0BalanceScaled = (uint256(binState.token0BalanceScaled) + amount0Scaled).toUint104();
          }
          if (amount1Scaled > 0) {
            totalToken1ToAddScaled += amount1Scaled;
            binState.token1BalanceScaled = (uint256(binState.token1BalanceScaled) + amount1Scaled).toUint104();
          }
          binTotalShares[binIdx] = binTotalSharesVal + sharesToAdd;
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L247-249)
```text
  function _validateOwner(address owner) internal pure {
    if (owner == address(0)) revert InvalidPositionOwner();
  }
```
