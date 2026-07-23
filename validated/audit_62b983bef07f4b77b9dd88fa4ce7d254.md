Audit Report

## Title
USDC-Blacklisted LP Address Permanently Locks Principal in `removeLiquidity` — (File: `metric-core/contracts/libraries/LiquidityLib.sol`)

## Summary
`LiquidityLib.removeLiquidity` transfers owed tokens directly to `owner` via `safeTransfer`. If `owner` is on the USDC (or USDT) blacklist, every call reverts and rolls back all share-accounting changes, leaving the LP's principal permanently locked with no alternative withdrawal path.

## Finding Description
`MetricOmmPool.removeLiquidity` enforces `msg.sender == owner` at line 206, then delegates to `LiquidityLib.removeLiquidity`. Inside the library, bin-state accounting (share deductions at lines 210–214, `binTotals` updates at lines 230–237) executes first, followed by push transfers at lines 242–247:

```solidity
if (amount0Removed > 0) {
    IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
}
if (amount1Removed > 0) {
    IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
}
```

A revert from USDC's blacklist check inside `transfer` propagates upward and rolls back the entire transaction, including all storage mutations. The LP's shares remain intact in `_positionBinShares` and `_binTotalShares`, but every subsequent call to `removeLiquidity` hits the same revert. There is no `recipient` parameter in `removeLiquidity` (unlike `swap`, which accepts a separate `recipient`), no pull-claim mapping, and no admin rescue path. `removeLiquidity` also carries no `whenNotPaused` guard, so pausing the pool does not help.

## Impact Explanation
An LP whose address is added to the USDC blacklist after depositing loses all access to their principal. The pool's bin balances correctly reflect the owed amounts, but those amounts can never be transferred out. This is a direct, irrecoverable loss of user principal — a High-severity impact per Sherlock criteria.

## Likelihood Explanation
USDC blacklisting is explicitly in scope per contest rules ("non-standard ERC20 behavior except USDC/USDT"). The trigger requires USDC Centre to blacklist the LP's address (e.g., regulatory action or sanctions). This is a low-probability external event, making overall severity **Medium** (low likelihood × high impact).

## Recommendation
Replace the push-transfer pattern with a pull-claim pattern: accumulate owed amounts in a per-address mapping during `removeLiquidity`, and expose a separate `claimTokens(address recipient)` function. Alternatively, add a `recipient` parameter to `removeLiquidity` (distinct from `owner`) so the LP can direct proceeds to a non-blacklisted address, mirroring the pattern already used in `swap`.

## Proof of Concept
1. Pool is deployed with USDC as `token0`.
2. LP calls `addLiquidity(owner=LP_ADDR, ...)` — shares are minted, USDC enters the pool.
3. USDC Centre blacklists `LP_ADDR`.
4. LP calls `removeLiquidity(owner=LP_ADDR, ...)`.
5. `LiquidityLib.removeLiquidity` computes `amount0Removed > 0` and calls `IERC20(USDC).safeTransfer(LP_ADDR, amount0Removed)` at line 243.
6. USDC's `transfer` reverts because `LP_ADDR` is blacklisted.
7. The entire transaction reverts; LP's shares remain in `_positionBinShares`.
8. Steps 4–7 repeat on every future attempt — LP principal is permanently locked.