### Title
LP principal permanently frozen when position owner is blacklisted by USDC/USDT — (`metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

`removeLiquidity` hardcodes token transfers to `owner` with no `recipient` parameter, and simultaneously enforces `msg.sender == owner`. If the position owner is blacklisted by USDC or USDT after depositing, the `safeTransfer` to `owner` reverts on every withdrawal attempt, permanently freezing the LP's principal inside the pool.

---

### Finding Description

`MetricOmmPool.removeLiquidity` enforces a strict identity check:

```solidity
if (msg.sender != owner) revert NotPositionOwner();
``` [1](#0-0) 

After burning shares and computing the owed token amounts, `LiquidityLib.removeLiquidity` transfers directly to `owner` with no alternative recipient:

```solidity
if (amount0Removed > 0) {
    IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
}
if (amount1Removed > 0) {
    IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
}
``` [2](#0-1) 

The function signature accepts no `recipient` argument:

```solidity
function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
``` [3](#0-2) 

The interface NatSpec confirms the design: *"Requires `msg.sender == owner` (`NotPositionOwner` otherwise). No callback: tokens are transferred out directly."* [4](#0-3) 

By contrast, `swap` already accepts a `recipient` parameter that decouples the caller from the token destination: [5](#0-4) 

There is no mechanism — no position transfer, no delegate-removal, no alternative withdrawal path — that allows an owner to redirect their owed tokens to a different address.

---

### Impact Explanation

If a position owner's address is blacklisted by USDC or USDT (both explicitly in scope per the contest's allowed-impact gate) after depositing liquidity:

- Every call to `removeLiquidity` reverts at the `safeTransfer` step because USDC/USDT revert on transfers to blacklisted addresses.
- The shares are **not** burned (the revert rolls back all state changes), so the position remains recorded but permanently unwithdrawable.
- The underlying token principal is locked in the pool contract forever with no recovery path.

This is a direct loss of user principal — the LP's deposited tokens are irrecoverable.

---

### Likelihood Explanation

USDC and USDT blacklisting is a real, documented mechanism used by Circle and Tether in response to regulatory orders, sanctions, or exploit responses. It is a low-probability event for any individual address, but the protocol has no defense against it. The window of exposure is the entire duration of an LP position, which can be indefinite. Severity is **Medium** (low probability, high impact — permanent principal loss).

---

### Recommendation

Add an optional `recipient` parameter to `removeLiquidity` so the position owner can redirect token output to a non-blacklisted address:

```solidity
// MetricOmmPool.sol
function removeLiquidity(
    address owner,
    address recipient,   // <-- new
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata extensionData
) external nonReentrant(PoolActions.REMOVE_LIQUIDITY) returns (...) {
    if (msg.sender != owner) revert NotPositionOwner();
    ...
    LiquidityLib.removeLiquidity(
        _liquidityContext(), owner, recipient, salt, deltas, ...
    );
}

// LiquidityLib.sol
if (amount0Removed > 0) IERC20(ctx.token0).safeTransfer(recipient, amount0Removed);
if (amount1Removed > 0) IERC20(ctx.token1).safeTransfer(recipient, amount1Removed);
```

This mirrors the existing `swap` design where `msg.sender` (the authorized caller) and `recipient` (the token destination) are decoupled.

---

### Proof of Concept

1. Alice (`owner = 0xAlice`) calls `addLiquidity` via `MetricOmmPoolLiquidityAdder`, depositing 100,000 USDC into bin 0.
2. USDC Centre blacklists `0xAlice` (e.g., due to a regulatory freeze).
3. Alice calls `removeLiquidity(0xAlice, salt, deltas, "")`.
4. `MetricOmmPool` passes the call to `LiquidityLib.removeLiquidity`.
5. Shares are burned, `amount0Removed = 100,000 USDC` is computed.
6. `IERC20(USDC).safeTransfer(0xAlice, 100_000e6)` reverts — USDC blacklist check fails.
7. The entire transaction reverts; Alice's shares remain in storage, her 100,000 USDC is permanently locked in the pool.
8. No alternative function exists to redirect the transfer to a non-blacklisted address.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L206-206)
```text
    if (msg.sender != owner) revert NotPositionOwner();
```

**File:** metric-core/contracts/MetricOmmPool.sol (L217-224)
```text
  function swap(
    address recipient,
    bool zeroForOne,
    int128 amountSpecified,
    uint128 priceLimitX64,
    bytes calldata callbackData,
    bytes calldata extensionData
  ) external whenNotPaused nonReentrant(PoolActions.SWAP) returns (int128, int128) {
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

**File:** metric-core/contracts/interfaces/IMetricOmmPool/IMetricOmmPoolActions.sol (L164-166)
```text
  /// @notice Burn shares across bins for `(owner, salt)` and send underlying tokens to `owner`.
  /// @dev Requires `msg.sender == owner` (`NotPositionOwner` otherwise). No callback: tokens are transferred out directly.
  /// @param owner Must equal `msg.sender`.
```

**File:** metric-core/contracts/interfaces/IMetricOmmPool/IMetricOmmPoolActions.sol (L172-174)
```text
  function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    returns (uint256 amount0Removed, uint256 amount1Removed);
```
