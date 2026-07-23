Audit Report

## Title
Free Share Minting in Fully-Drained Bins Dilutes Existing LP Claims — (`metric-core/contracts/libraries/LiquidityLib.sol`)

## Summary

In `LiquidityLib.addLiquidity`, when a bin has been fully drained by swaps (`token0BalanceScaled == 0` and `token1BalanceScaled == 0`) but still carries a positive `binTotalShares`, the proportional share-amount calculation yields zero for both tokens. Shares and bin-state are written to storage unconditionally, but the token-payment callback is gated on a non-zero aggregate owed amount and is therefore skipped entirely. An attacker can mint an arbitrary number of shares at zero cost and later withdraw a proportional fraction of tokens that flow back into the bin when the price reverses, directly stealing from existing LPs.

## Finding Description

In the `else` branch of the share-amount calculation (lines 108–111 of `LiquidityLib.sol`), when `binTotalSharesVal > 0` and both bin balances are zero:

```solidity
amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
// = ceilDiv(0 * sharesToAdd, binTotalSharesVal) = 0
amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
// = ceilDiv(0 * sharesToAdd, binTotalSharesVal) = 0
```

Both scaled amounts are zero, so neither `totalToken0ToAddScaled` nor `totalToken1ToAddScaled` is incremented. However, share accounting is written unconditionally immediately after (lines 120–121):

```solidity
binTotalShares[binIdx] = binTotalSharesVal + sharesToAdd;
positionBinShares[posKey] = newUserShares;
```

After the loop, the callback guard (lines 144–155) evaluates `amount0Added > 0 || amount1Added > 0`, which is false, so `metricOmmModifyLiquidityCallback` is never called and no tokens are transferred. The attacker's shares are committed to storage with zero payment.

Swap logic updates `binState.token0BalanceScaled` / `token1BalanceScaled` but never touches `_binTotalShares`, so a fully-drained bin with positive share count is a reachable, persistent on-chain state. When the price reverses and swaps refill the bin, `removeLiquidity` (lines 204–206) distributes the refilled balance proportionally across all shares including the attacker's free ones, transferring tokens the attacker never deposited.

## Impact Explanation

Direct theft of LP principal. Existing LPs who deposited real capital receive a smaller fraction of refilled bin tokens than they are owed. The loss is proportional to the attacker's free share count relative to the pre-existing `binTotalShares`. This constitutes pool insolvency: the pool's bin-balance accounting no longer covers legitimate LP claims. Severity: Critical/High.

## Likelihood Explanation

Bins being fully drained is a normal market event in any active pool. No privileged access is required; `addLiquidity` is open to any caller with any `owner` address. The attacker only needs to monitor `BinSwapped` events, detect when a bin's scaled balance reaches zero while `_binTotalShares` remains positive, and call `addLiquidity` before the price reverses. The attack is repeatable across any pool and any bin.

## Recommendation

Add a guard in `LiquidityLib.addLiquidity` inside the `else` branch (after computing `amount0Scaled` and `amount1Scaled`) that reverts when `binTotalSharesVal > 0` and both computed amounts are zero:

```solidity
} else {
    amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
    amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
    if (amount0Scaled == 0 && amount1Scaled == 0) revert DrainedBin();
}
```

This enforces the invariant that shares in a non-empty bin must always represent a non-zero token claim, mirroring the behavior of the `binTotalSharesVal == 0` branch which always computes a positive token amount.

## Proof of Concept

1. Pool deployed with bins `[-1, 0, 1]`. Alice calls `addLiquidity` for bin `1` (above current price), depositing token0 and receiving 10,000 shares. `_binTotalShares[1] = 10_000`, `_binStates[1].token0BalanceScaled > 0`.
2. A series of `!zeroForOne` swaps fully consume bin `1`: `_binStates[1].token0BalanceScaled = 0`, `_binStates[1].token1BalanceScaled = 0`. `_binTotalShares[1]` remains `10_000` (swaps never modify share accounting).
3. Bob calls `addLiquidity(owner=Bob, salt=0, deltas={binIdxs:[1], shares:[10_000]}, ...)`.
   - `binTotalSharesVal = 10_000 > 0` → proportional branch taken.
   - `amount0Scaled = ceilDiv(0, 10_000) = 0`; `amount1Scaled = 0`.
   - `_binTotalShares[1]` written to `20_000`; `_positionBinShares[key(Bob,0,1)]` written to `10_000`.
   - `amount0Added = 0`, `amount1Added = 0` → callback skipped. **No tokens paid.**
4. Price reverses; `zeroForOne` swaps refill bin `1` with 1,000 units of token0 (scaled). `_binStates[1].token0BalanceScaled = 1_000`.
5. Bob calls `removeLiquidity` for his 10,000 shares:
   - `amount0Scaled = 1_000 * 10_000 / 20_000 = 500` → Bob receives 500 units of token0 he never paid for.
   - Alice removes her 10,000 shares and receives only 500 units instead of the 1,000 she is owed.