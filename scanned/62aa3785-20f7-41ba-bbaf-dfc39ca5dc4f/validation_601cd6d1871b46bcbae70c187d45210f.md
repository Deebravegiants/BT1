### Title
USDC-Blacklisted LP Address Permanently Locks Principal in `removeLiquidity` — (File: `metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

`LiquidityLib.removeLiquidity` uses a push-transfer pattern, sending owed tokens directly to `owner` via `safeTransfer`. If `owner` is on the USDC (or USDT) blacklist, every call to `removeLiquidity` reverts, permanently locking the LP's principal in the pool with no alternative withdrawal path.

---

### Finding Description

`MetricOmmPool.removeLiquidity` enforces `msg.sender == owner` and then delegates to `LiquidityLib.removeLiquidity`, which computes the LP's share of each bin and transfers the proceeds directly to `owner`: [1](#0-0) 

Inside the library, after all bin-state accounting is complete, the push transfers are issued: [2](#0-1) 

Because `safeTransfer` is used, a revert from the token contract (e.g., USDC's blacklist check) propagates upward and rolls back the entire transaction, including the share-accounting updates on lines 210–214 and the `binTotals` updates on lines 230–237. [3](#0-2) 

The result is a permanent deadlock: the LP's shares remain recorded in `_positionBinShares` and `_binTotalShares`, but every attempt to redeem them reverts. There is no alternative recipient parameter, no pull-claim mapping, and no admin rescue path in the pool.

`removeLiquidity` carries no `whenNotPaused` guard (unlike `swap`), so even pausing the pool does not help — the blacklisted owner still cannot withdraw. [4](#0-3) 

---

### Impact Explanation

An LP whose address is added to the USDC (or USDT) blacklist after depositing liquidity permanently loses access to their principal. The pool's bin balances correctly reflect the owed amounts, but those amounts can never be transferred out. This constitutes a direct, irrecoverable loss of user principal — a High-severity impact under Sherlock criteria.

---

### Likelihood Explanation

USDC blacklisting is explicitly in scope per the contest rules ("non-standard ERC20 behavior except USDC/USDT"). The trigger requires USDC Centre to blacklist the LP's address (e.g., due to regulatory action or the address being linked to sanctioned activity). This is a low-probability external event, making the overall severity **Medium** (low likelihood × high impact).

---

### Recommendation

Replace the push-transfer pattern with a pull-claim pattern:

1. In `removeLiquidity`, instead of calling `safeTransfer(owner, ...)`, accumulate the owed amounts in a per-address mapping (e.g., `mapping(address => uint256) public claimable0` / `claimable1`).
2. Expose a separate `claimTokens(address recipient)` function that lets the owner pull their balance to any non-blacklisted address they control.

Alternatively, add a `recipient` parameter to `removeLiquidity` (distinct from `owner`) so the LP can direct proceeds to a non-blacklisted address at withdrawal time, mirroring the pattern already used in `swap`.

---

### Proof of Concept

1. Pool is deployed with USDC as `token0`.
2. LP calls `addLiquidity(owner=LP_ADDR, ...)` — shares are minted, USDC enters the pool.
3. USDC Centre blacklists `LP_ADDR` (e.g., regulatory freeze).
4. LP calls `removeLiquidity(owner=LP_ADDR, ...)`.
5. `LiquidityLib.removeLiquidity` computes `amount0Removed > 0` and calls `IERC20(USDC).safeTransfer(LP_ADDR, amount0Removed)`.
6. USDC's `transfer` reverts because `LP_ADDR` is blacklisted.
7. The entire transaction reverts; LP's shares remain in `_positionBinShares`.
8. Step 4–7 repeats on every future attempt — LP principal is permanently locked. [2](#0-1)

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

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L204-214)
```text
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
