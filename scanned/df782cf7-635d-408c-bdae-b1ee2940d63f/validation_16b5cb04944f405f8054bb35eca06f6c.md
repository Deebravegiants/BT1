### Title
LP Position Permanently Locked When Owner Is USDC-Blacklisted in `removeLiquidity` — (`File: metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

`LiquidityLib.removeLiquidity` unconditionally pushes token0 and token1 directly to `owner` via `safeTransfer`. If either pool token is USDC and the LP's address is USDC-blacklisted, every call to `removeLiquidity` reverts, permanently locking the LP's principal inside the pool with no alternative withdrawal path.

---

### Finding Description

In `LiquidityLib.removeLiquidity`, after all internal accounting is updated (bin balances, `binTotalShares`, `positionBinShares`), the function unconditionally pushes the owed tokens to `owner`:

```solidity
if (amount0Removed > 0) {
    IERC20(ctx.token0).safeTransfer(owner, amount0Removed);   // line 243
}
if (amount1Removed > 0) {
    IERC20(ctx.token1).safeTransfer(owner, amount1Removed);   // line 246
}
``` [1](#0-0) 

USDC implements an address blacklist. When `owner` is blacklisted, `safeTransfer` reverts, rolling back the entire transaction. Because `removeLiquidity` enforces `msg.sender == owner`:

```solidity
if (msg.sender != owner) revert NotPositionOwner();
``` [2](#0-1) 

no third party can call `removeLiquidity` on behalf of the blacklisted LP, and there is no alternative claim or pull-payment path anywhere in the protocol. The LP's shares remain recorded in `_positionBinShares` and `_binTotalShares`, but the underlying tokens can never be retrieved.

The deployed configuration confirms USDC is a primary pool token across all supported chains: [3](#0-2) 

---

### Impact Explanation

**High.** A USDC-blacklisted LP permanently loses access to their full token0 and token1 principal. The pool's `binTotals` still account for those tokens, so the pool remains solvent for other LPs, but the blacklisted LP's share of the pool is irrecoverable. This is a direct, permanent loss of user principal with no on-chain remedy.

---

### Likelihood Explanation

**Low.** USDC blacklisting is an infrequent administrative action by Circle. However, it is a documented, real-world event (e.g., OFAC-sanctioned addresses), and USDC is the explicit quote token for every pool in the protocol's production configuration. The combination of a common pool token with a blacklist feature and a forced-push withdrawal pattern makes this a credible, if rare, scenario.

---

### Recommendation

Replace the push-transfer pattern in `removeLiquidity` with a pull (claim) pattern:

1. Instead of calling `safeTransfer` inside `removeLiquidity`, credit the owed amounts to a per-owner internal balance mapping (e.g., `mapping(address => mapping(address => uint256)) pendingWithdrawals`).
2. Add a separate `claimTokens(address token)` function that lets the owner pull their credited balance at any time.

This decouples the accounting update from the token transfer, so a blacklisted address does not block the state update, and the owner can attempt the claim later (e.g., after being removed from the blacklist) or route through a different mechanism.

---

### Proof of Concept

1. Alice provides liquidity to a USDC/WBTC pool. Her shares are recorded in `_positionBinShares`.
2. Circle blacklists Alice's address on USDC.
3. Alice calls `removeLiquidity`. The function computes `amount1Removed > 0` (USDC owed) and reaches:
   ```solidity
   IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
   ```
   USDC's `transfer` reverts with a blacklist error. The entire transaction reverts.
4. Alice cannot use any other address because `msg.sender != owner` is enforced:
   ```solidity
   if (msg.sender != owner) revert NotPositionOwner();
   ```
5. Alice's shares remain in `_positionBinShares` indefinitely. Her USDC and WBTC principal are permanently locked in the pool. [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

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

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L239-247)
```text
      (amount0Removed, amount1Removed) =
        _deltasScaledToExternal(totalToken0ToRemoveScaled, totalToken1ToRemoveScaled, ctx, Math.Rounding.Floor);

      if (amount0Removed > 0) {
        IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
      }
      if (amount1Removed > 0) {
        IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
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

**File:** smart-contracts-poc/script/config/networks.json (L42-44)
```json
          "baseTokenAddress": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
          "quoteTokenAddress": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"
        },
```
