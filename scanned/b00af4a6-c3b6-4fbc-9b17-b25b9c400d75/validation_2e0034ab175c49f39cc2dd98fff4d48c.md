### Title
LP Liquidity Permanently Locked When Owner Address Is USDC-Blacklisted — (`metric-core/contracts/libraries/LiquidityLib.sol`)

### Summary

`removeLiquidity` transfers pool tokens directly to the position `owner` with no alternative recipient path. When a pool token is USDC and the LP's address is subsequently blacklisted, every `removeLiquidity` call reverts, permanently locking the LP's deposited principal with no protocol-level recovery path.

### Finding Description

In `LiquidityLib.removeLiquidity`, after computing the LP's pro-rata share of bin balances, the function unconditionally pushes tokens to `owner`:

```solidity
// metric-core/contracts/libraries/LiquidityLib.sol lines 242-247
if (amount0Removed > 0) {
    IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
}
if (amount1Removed > 0) {
    IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
}
``` [1](#0-0) 

The caller is enforced to equal `owner` at the pool level:

```solidity
// MetricOmmPool.sol line 206
if (msg.sender != owner) revert NotPositionOwner();
``` [2](#0-1) 

There is no parameter to redirect output to a different recipient, no pull-based claim mechanism, and no position-transfer primitive. The position key is `keccak256(abi.encode(owner, salt, bin))`, permanently binding the LP claim to the original depositor address: [3](#0-2) 

Because all state mutations (bin balance decrements, share burns) and the `safeTransfer` execute atomically in one transaction with no `try/catch`, a revert on the transfer rolls back the entire call. The LP's shares remain recorded but are permanently unreachable.

### Impact Explanation

An LP who deposited into a USDC pool and is later blacklisted by USDC loses their entire deposited principal. There is no escape hatch: they cannot call `removeLiquidity` (transfer reverts), cannot transfer their position to a clean address (no transfer primitive exists), and no admin or factory function can rescue the funds on their behalf. The LP's capital is permanently locked inside the pool's bin accounting.

### Likelihood Explanation

USDC blacklisting is an explicitly in-scope token behavior. The scenario requires: (1) a pool with USDC as token0 or token1 (common, as USDC is a primary quote asset), and (2) the LP's address being blacklisted after deposit (e.g., due to sanctions). Both conditions are realistic and have occurred on-chain in other protocols. No attacker action is required — the blacklisting is an external event that triggers the lock.

### Recommendation

Decouple the withdrawal recipient from the position owner. Add an optional `recipient` parameter to `removeLiquidity` (defaulting to `owner` when zero), or implement a pull-based model where computed amounts are credited to an internal balance mapping that the LP can claim to any non-blacklisted address. This mirrors the mitigation suggested in the reference report.

```solidity
// Suggested signature change
function removeLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    address recipient,          // new: where tokens are sent
    bytes calldata extensionData
) external returns (uint256 amount0Removed, uint256 amount1Removed);
```

### Proof of Concept

1. Pool is deployed with USDC as `token0`.
2. LP calls `addLiquidity` and deposits USDC; shares are minted to `owner = LP_ADDRESS`.
3. USDC blacklists `LP_ADDRESS`.
4. LP calls `removeLiquidity(LP_ADDRESS, salt, deltas, "")`.
5. `LiquidityLib.removeLiquidity` computes `amount0Removed > 0` and calls `IERC20(USDC).safeTransfer(LP_ADDRESS, amount0Removed)`.
6. USDC reverts because `LP_ADDRESS` is blacklisted.
7. The entire transaction reverts; LP's shares remain in `_positionBinShares[posKey]` but are permanently inaccessible.
8. No alternative call path exists to recover the funds.

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L242-247)
```text
      if (amount0Removed > 0) {
        IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
      }
      if (amount1Removed > 0) {
        IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
      }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L256-258)
```text
  function _positionBinKey(address owner, uint80 salt, int8 bin) internal pure returns (bytes32 key) {
    // forge-lint: disable-next-line(asm-keccak256)
    return keccak256(abi.encode(owner, salt, bin));
```

**File:** metric-core/contracts/MetricOmmPool.sol (L206-206)
```text
    if (msg.sender != owner) revert NotPositionOwner();
```
