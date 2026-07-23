### Title
Zero-Address `owner` in `addLiquidity` Permanently Locks LP Principal - (File: metric-core/contracts/libraries/LiquidityLib.sol)

### Summary
`MetricOmmPool.addLiquidity` accepts an arbitrary `owner` address with no zero-address guard. When `owner = address(0)`, real tokens are pulled from the caller via callback and credited to the pool, but the resulting LP shares are minted to the `address(0)` position key. Because `removeLiquidity` enforces `msg.sender == owner`, and `msg.sender` can never be `address(0)`, the deposited principal is permanently locked with no recovery path.

### Finding Description
`MetricOmmPool.addLiquidity` passes `owner` directly into `LiquidityLib.addLiquidity` without any zero-address validation: [1](#0-0) 

Inside `LiquidityLib.addLiquidity`, the position key is computed as `keccak256(abi.encode(owner, salt, bin))`: [2](#0-1) 

Shares are written to `positionBinShares[posKey]` and `binTotalShares[binIdx]` is incremented, then the callback fires and pulls real tokens from `msg.sender`: [3](#0-2) 

`removeLiquidity` enforces `msg.sender == owner` before any state change: [4](#0-3) 

Since `msg.sender` is never `address(0)` on-chain, the `NotPositionOwner` revert fires unconditionally for any attempt to remove the zero-address position, making the deposited tokens permanently irrecoverable.

The periphery `IMetricOmmPoolLiquidityAdder` acknowledges this risk with its own `InvalidPositionOwner` error: [5](#0-4) 

However, the core pool itself — the canonical production surface — has no such guard, leaving any direct caller or third-party router unprotected.

### Impact Explanation
Any tokens deposited via `addLiquidity(address(0), ...)` are credited to `binTotals` (pool accounting is internally consistent) but the corresponding LP claims are permanently inaccessible. The depositor loses 100% of their principal with no on-chain recovery mechanism. The pool is not insolvent — the tokens remain — but the LP's claim is destroyed.

### Likelihood Explanation
The `addLiquidity` interface explicitly supports the operator pattern where `msg.sender != owner`: [6](#0-5) 

A router, aggregator, or integration contract that passes a user-supplied or misconfigured `owner` parameter can silently trigger this. The factory validates `admin != address(0)` and `adminFeeDestination != address(0)` at pool creation: [7](#0-6) 

But no equivalent guard exists on the liquidity path, making the omission inconsistent with the factory's own defensive posture.

### Recommendation
Add a zero-address check at the top of `MetricOmmPool.addLiquidity` (or at the entry of `LiquidityLib.addLiquidity`):

```solidity
if (owner == address(0)) revert InvalidPositionOwner();
```

This mirrors the guard already present in the periphery `IMetricOmmPoolLiquidityAdder` and is consistent with the factory's existing `InvalidAdmin` / `InvalidAdminFeeDestination` checks.

### Proof of Concept

1. Attacker (or buggy router) calls:
   ```solidity
   pool.addLiquidity(
       address(0),   // owner = zero address
       0,            // salt
       deltas,       // valid bin/share arrays
       callbackData,
       ""
   );
   ```
2. `LiquidityLib.addLiquidity` computes `posKey = keccak256(abi.encode(address(0), 0, binIdx))` and writes shares there.
3. The `IMetricOmmModifyLiquidityCallback` fires on `msg.sender`; real tokens are transferred into the pool and `binTotals` is updated.
4. Any subsequent call to `pool.removeLiquidity(address(0), 0, deltas, "")` reverts with `NotPositionOwner` because `msg.sender != address(0)`.
5. The deposited tokens are permanently locked; no admin, factory, or owner function provides a recovery path. [8](#0-7)

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

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L120-155)
```text
          binTotalShares[binIdx] = binTotalSharesVal + sharesToAdd;
          positionBinShares[posKey] = newUserShares;

          binBalanceDeltas[i] = BinBalanceDelta({
            // Safe: per-bin deltas are bounded by uint104 bin balances.
            // forge-lint: disable-next-line(unsafe-typecast)
            delta0Scaled: int256(amount0Scaled),
            // casting to int256 is safe because amount1Scaled is bounded by uint104 bin balances.
            // forge-lint: disable-next-line(unsafe-typecast)
            delta1Scaled: int256(amount1Scaled)
          });
        }
      }

      if (totalToken0ToAddScaled > 0) {
        binTotals.scaledToken0 = (uint256(binTotals.scaledToken0) + totalToken0ToAddScaled).toUint128();
      }
      if (totalToken1ToAddScaled > 0) {
        binTotals.scaledToken1 = (uint256(binTotals.scaledToken1) + totalToken1ToAddScaled).toUint128();
      }

      (amount0Added, amount1Added) =
        _deltasScaledToExternal(totalToken0ToAddScaled, totalToken1ToAddScaled, ctx, Math.Rounding.Ceil);

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

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L161-170)
```text
  function removeLiquidity(
    PoolContext memory ctx,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    BinTotals storage binTotals,
    mapping(int256 => BinState) storage binStates,
    mapping(int256 => uint256) storage binTotalShares,
    mapping(bytes32 => uint256) storage positionBinShares
  ) public returns (uint256 amount0Removed, uint256 amount1Removed) {
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L256-259)
```text
  function _positionBinKey(address owner, uint80 salt, int8 bin) internal pure returns (bytes32 key) {
    // forge-lint: disable-next-line(asm-keccak256)
    return keccak256(abi.encode(owner, salt, bin));
  }
```

**File:** metric-periphery/contracts/interfaces/IMetricOmmPoolLiquidityAdder.sol (L24-26)
```text
  /// @notice Owner argument is zero address for owner-based add path.
  error InvalidPositionOwner();
  /// @notice `LiquidityDelta` arrays have different lengths.
```

**File:** metric-core/contracts/interfaces/IMetricOmmPool/IMetricOmmPoolActions.sol (L146-162)
```text
  /// @notice Mint shares across bins for `(owner, salt)`; pulls tokens via `IMetricOmmModifyLiquidityCallback` on `msg.sender`.
  /// @dev Callback receives native token amounts the pool expects; underpay reverts `InsufficientTokenBalance`. If `DEPOSIT_ALLOWLIST_PROVIDER` is set, `owner` must pass allowlist. `msg.sender` pays but need not equal `owner` (operator pattern).
  /// @param owner Position owner encoded in the pool’s position key.
  /// @param salt Namespace byte width for the key (`uint80`).
  /// @param deltas Parallel `binIdxs` / `shares` arrays (see `LiquidityDelta`).
  /// @param callbackData Opaque bytes forwarded unmodified to the modify-liquidity callback.
  /// @param extensionData Opaque bytes forwarded to liquidity extensions (beforeAddLiquidity / afterAddLiquidity).
  /// @return amount0Added Total token0 actually pulled from the callback into the pool (native).
  /// @return amount1Added Total token1 actually pulled from the callback into the pool (native).
  /// @dev Reverts `LiquidityDeltaLengthMismatch` when `binIdxs` and `shares` lengths differ.
  function addLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
  ) external returns (uint256 amount0Added, uint256 amount1Added);
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L548-554)
```text
  function _validatePoolParameters(PoolParameters calldata params) internal view {
    if (params.token0 == address(0) || params.token1 == address(0) || params.token0 == params.token1) {
      revert InvalidTokenConfig();
    }
    if (params.admin == address(0)) revert InvalidAdmin();
    _validatePriceProvider(params.token0, params.token1, params.priceProvider);
    if (params.adminFeeDestination == address(0)) revert InvalidAdminFeeDestination();
```
