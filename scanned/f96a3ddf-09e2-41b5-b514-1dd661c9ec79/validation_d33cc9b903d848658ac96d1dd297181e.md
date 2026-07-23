### Title
LP Funds Permanently Locked When Position Owner Is USDC-Blacklisted in `removeLiquidity` — (File: metric-core/contracts/libraries/LiquidityLib.sol)

### Summary

`LiquidityLib.removeLiquidity` uses a push pattern to transfer owed tokens directly to `owner`. If `owner` is blacklisted in USDC (or USDT) after providing liquidity, every call to `removeLiquidity` reverts, permanently locking the LP's principal with no recovery path.

### Finding Description

After computing the scaled amounts to return across all bins, `removeLiquidity` pushes both tokens to `owner` in sequence:

```solidity
// LiquidityLib.sol lines 242-247
if (amount0Removed > 0) {
    IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
}
if (amount1Removed > 0) {
    IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
}
``` [1](#0-0) 

USDC's blacklist causes `transfer` to revert for both the sender and the receiver. If `owner` is blacklisted, `safeTransfer(owner, ...)` reverts unconditionally, rolling back the entire call including all bin-state mutations computed in the loop above.

The pool enforces `msg.sender == owner` in `MetricOmmPool.removeLiquidity`:

```solidity
// MetricOmmPool.sol line 206
if (msg.sender != owner) revert NotPositionOwner();
``` [2](#0-1) 

This means the LP cannot delegate withdrawal to a clean address. Positions are keyed by `keccak256(abi.encode(owner, salt, bin))` with no transfer mechanism, so the shares are permanently bound to the blacklisted address. [3](#0-2) 

A secondary effect: if token0 is USDC and the LP is blacklisted, the token0 transfer fails first, which also prevents the token1 transfer from executing — the LP loses access to **both** tokens even if token1 is not USDC.

### Impact Explanation

The LP's shares remain recorded in `_positionBinShares` and `_binTotalShares` but can never be redeemed. The underlying token balances are locked inside the pool's bins indefinitely. This is a direct, permanent loss of user principal with no on-chain recovery path. [4](#0-3) 

### Likelihood Explanation

USDC blacklisting is a documented real-world event (e.g., OFAC-sanctioned addresses). An LP can be blacklisted at any time after depositing. The pool has no mechanism to detect this condition in advance or to route tokens to an alternative address after the fact. Likelihood is low but the impact is total loss of principal, placing this at **Medium** severity under Sherlock's framework.

### Recommendation

Replace the push pattern with a pull pattern: record owed amounts in a claimable mapping and let the LP (or any address they authorize) call a separate `claim` function that transfers to an arbitrary recipient. Alternatively, allow `removeLiquidity` to accept an explicit `recipient` address distinct from `owner`, so a blacklisted LP can still direct funds to a clean address.

### Proof of Concept

1. Alice provides liquidity to a USDC/WETH pool, creating position `(alice, salt, bin)`.
2. Alice's address is later added to USDC's blacklist.
3. Alice calls `removeLiquidity`; the pool computes `amount0Removed` (USDC) and `amount1Removed` (WETH).
4. `IERC20(ctx.token0).safeTransfer(alice, amount0Removed)` reverts — USDC rejects transfers to blacklisted addresses.
5. The entire transaction reverts; Alice's shares remain in `_positionBinShares` unchanged.
6. Alice cannot call `removeLiquidity` from any other address (`msg.sender != owner` guard).
7. Alice's USDC **and** WETH are permanently locked in the pool. [5](#0-4) [6](#0-5)

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L161-251)
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
    unchecked {
      uint256 length = deltas.binIdxs.length;
      if (length == 0) return (0, 0);

      uint256 totalToken0ToRemoveScaled = 0;
      uint256 totalToken1ToRemoveScaled = 0;

      BinBalanceDelta[] memory binBalanceDeltas = new BinBalanceDelta[](length);

      for (uint256 i = 0; i < length; i++) {
        int256 binIdx = deltas.binIdxs[i];
        uint256 sharesToRemove = deltas.shares[i];

        if (binIdx < ctx.lowestBin || binIdx > ctx.highestBin) {
          revert IMetricOmmPoolActions.InvalidBinIndex(binIdx);
        }
        if (sharesToRemove == 0) continue;

        {
          // safe because -128 <= LOWEST_BIN <= HIGHEST_BIN <= 127 (enforced by factory)
          // forge-lint: disable-next-line(unsafe-typecast)
          bytes32 posKey = _positionBinKey(owner, salt, int8(binIdx));
          uint256 binTotalSharesVal = binTotalShares[binIdx];
          uint256 userShares = positionBinShares[posKey];

          if (userShares < sharesToRemove) {
            revert IMetricOmmPoolActions.InsufficientLiquidity(sharesToRemove, userShares);
          }
          uint256 newUserShares = userShares - sharesToRemove;
          if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }

          BinState storage binState = binStates[binIdx];
          uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
          uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;

          // casting to uint104 is safe because amount0Scaled and amount1Scaled are less than token(0|1)BalanceScaled
          // forge-lint: disable-next-line(unsafe-typecast)
          binState.token0BalanceScaled -= uint104(amount0Scaled);
          // forge-lint: disable-next-line(unsafe-typecast)
          binState.token1BalanceScaled -= uint104(amount1Scaled);
          binTotalShares[binIdx] = binTotalSharesVal - sharesToRemove;
          positionBinShares[posKey] = newUserShares;

          totalToken0ToRemoveScaled += amount0Scaled;
          totalToken1ToRemoveScaled += amount1Scaled;

          binBalanceDeltas[i] = BinBalanceDelta({
            // safe because amount0Scaled is bounded by uint104 bin balances.
            // forge-lint: disable-next-line(unsafe-typecast)
            delta0Scaled: -int256(amount0Scaled),
            // safe because amount1Scaled is bounded by uint104 bin balances.
            // forge-lint: disable-next-line(unsafe-typecast)
            delta1Scaled: -int256(amount1Scaled)
          });
        }
      }

      if (totalToken0ToRemoveScaled > 0) {
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken0 = uint128(uint256(binTotals.scaledToken0) - totalToken0ToRemoveScaled);
      }
      if (totalToken1ToRemoveScaled > 0) {
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken1 = uint128(uint256(binTotals.scaledToken1) - totalToken1ToRemoveScaled);
      }

      (amount0Removed, amount1Removed) =
        _deltasScaledToExternal(totalToken0ToRemoveScaled, totalToken1ToRemoveScaled, ctx, Math.Rounding.Floor);

      if (amount0Removed > 0) {
        IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
      }
      if (amount1Removed > 0) {
        IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
      }

      emit IMetricOmmPoolActions.LiquidityRemoved(owner, salt, deltas.binIdxs, binBalanceDeltas, deltas.shares);
    }
  }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L256-259)
```text
  function _positionBinKey(address owner, uint80 salt, int8 bin) internal pure returns (bytes32 key) {
    // forge-lint: disable-next-line(asm-keccak256)
    return keccak256(abi.encode(owner, salt, bin));
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
