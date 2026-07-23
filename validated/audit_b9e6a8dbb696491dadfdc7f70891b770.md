Audit Report

## Title
USDC-Blacklisted LP Address Permanently Locks Principal in `removeLiquidity` — (File: `metric-core/contracts/libraries/LiquidityLib.sol`)

## Summary
`LiquidityLib.removeLiquidity` transfers withdrawn tokens directly to `owner` via `safeTransfer`. If `owner` is on the USDC (or USDT) blacklist, every call reverts and rolls back all share-accounting changes, leaving the LP's principal permanently locked with no alternative withdrawal path. USDC/USDT non-standard behavior is explicitly in scope per contest rules.

## Finding Description
`MetricOmmPool.removeLiquidity` enforces `msg.sender == owner` and delegates to `LiquidityLib.removeLiquidity`: [1](#0-0) 

Inside `LiquidityLib.removeLiquidity`, all bin-state accounting updates (`binState.token0BalanceScaled`, `binState.token1BalanceScaled`, `binTotalShares[binIdx]`, `positionBinShares[posKey]`) occur within the loop: [2](#0-1) 

After the loop, the push transfers are issued: [3](#0-2) 

Because `safeTransfer` is used, a revert from USDC's blacklist check propagates upward and rolls back the entire transaction — including all accounting updates. The LP's shares remain intact in `_positionBinShares` and `_binTotalShares`, but every subsequent call to `removeLiquidity` will also revert identically. There is no `recipient` parameter, no pull-claim mapping, and no admin rescue path. `removeLiquidity` carries no `whenNotPaused` guard (unlike `swap` at line 224), so pausing the pool provides no relief either. [4](#0-3) 

## Impact Explanation
An LP whose address is added to the USDC blacklist after depositing loses all access to their principal. The pool's bin balances correctly reflect the owed amounts, but those amounts can never be transferred out. This is a direct, irrecoverable loss of user principal — a High-severity impact under Sherlock criteria.

## Likelihood Explanation
USDC blacklisting is explicitly in scope per contest rules ("non-standard ERC20 behavior except USDC/USDT"). The trigger requires USDC Centre to blacklist the LP's address due to regulatory action or sanctions linkage. This is a low-probability external event, making overall severity **Medium** (low likelihood × high impact).

## Recommendation
Replace the push-transfer pattern with a pull-claim pattern: in `removeLiquidity`, accumulate owed amounts in a per-address mapping (e.g., `mapping(address => uint256) claimable0/claimable1`) instead of calling `safeTransfer(owner, ...)` directly. Expose a separate `claimTokens(address recipient)` function allowing the owner to pull their balance to any non-blacklisted address. Alternatively, add a `recipient` parameter to `removeLiquidity` (distinct from `owner`) so the LP can direct proceeds to a non-blacklisted address at withdrawal time, mirroring the pattern already used in `swap`.

## Proof of Concept
1. Pool is deployed with USDC as `token0`.
2. LP calls `addLiquidity(owner=LP_ADDR, ...)` — shares are minted, USDC enters the pool.
3. USDC Centre blacklists `LP_ADDR`.
4. LP calls `removeLiquidity(owner=LP_ADDR, ...)`.
5. `LiquidityLib.removeLiquidity` computes `amount0Removed > 0` and calls `IERC20(USDC).safeTransfer(LP_ADDR, amount0Removed)`.
6. USDC's `transfer` reverts because `LP_ADDR` is blacklisted.
7. The entire transaction reverts; LP's shares remain in `_positionBinShares` and `_binTotalShares` unchanged.
8. Steps 4–7 repeat on every future attempt — LP principal is permanently locked.

### Citations

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

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L210-214)
```text
          binState.token0BalanceScaled -= uint104(amount0Scaled);
          // forge-lint: disable-next-line(unsafe-typecast)
          binState.token1BalanceScaled -= uint104(amount1Scaled);
          binTotalShares[binIdx] = binTotalSharesVal - sharesToRemove;
          positionBinShares[posKey] = newUserShares;
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L242-247)
```text
      if (amount0Removed > 0) {
        IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
      }
      if (amount1Removed > 0) {
        IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
      }
```
