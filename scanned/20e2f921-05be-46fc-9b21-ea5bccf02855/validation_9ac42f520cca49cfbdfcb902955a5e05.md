### Title
`DepositAllowlistExtension` Checks `owner` Instead of `sender`, Allowing Any Caller to Bypass the Deposit Allowlist — (`metric-periphery/contracts/extensions/DepositAllowlistExtension.sol`)

---

### Summary

`DepositAllowlistExtension.beforeAddLiquidity` gates deposits by checking the `owner` (position recipient) address against the allowlist, while ignoring the `sender` (actual caller). Because `MetricOmmPool.addLiquidity` explicitly permits any `msg.sender` to call with an arbitrary `owner` address (the "operator pattern"), a non-allowlisted caller can bypass the allowlist entirely by supplying an allowlisted address as `owner`.

---

### Finding Description

`MetricOmmPool.addLiquidity` contains no `msg.sender == owner` check:

```solidity
// MetricOmmPool.sol L182-196
function addLiquidity(
    address owner,          // ← any address, no ownership check
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (...) {
    ...
    _beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Added, amount1Added) = LiquidityLib.addLiquidity(
        _liquidityContext(), owner, salt, deltas, callbackData, ...
    );
    ...
}
```

The interface NatSpec at line 147 confirms this is intentional: *"msg.sender pays but need not equal owner (operator pattern)."*

`DepositAllowlistExtension.beforeAddLiquidity` receives both `sender` (the original caller) and `owner` (the position recipient), but silently discards `sender` and gates only on `owner`:

```solidity
// DepositAllowlistExtension.sol L32-42
function beforeAddLiquidity(address, address owner, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][owner]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
}
```

Here `msg.sender` is the pool, so the check is `allowedDepositor[pool][owner]`. The `sender` parameter (the actual depositor) is unnamed and never read.

**Attack path:**
1. Pool is deployed with `DepositAllowlistExtension` enabled; Alice is allowlisted (`allowedDepositor[pool][alice] = true`); Bob is not.
2. Bob calls `pool.addLiquidity(alice, salt, deltas, callbackData, extensionData)` directly.
3. The extension evaluates `allowedDepositor[pool][alice]` → `true` → passes.
4. Bob's callback (`metricOmmModifyLiquidityCallback`) is invoked on `msg.sender = Bob`; Bob pays the tokens.
5. Shares are credited to `(alice, salt, bin)` in `_positionBinShares`.
6. Bob has successfully deposited into a restricted pool without being allowlisted.

By contrast, `SwapAllowlistExtension.beforeSwap` correctly checks `sender`:

```solidity
// SwapAllowlistExtension.sol L31-41
function beforeSwap(address sender, address, bool, int128, uint128, uint256, uint128, uint128, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllSwappers[msg.sender] && !allowedSwapper[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToSwap();
    }
    ...
}
```

The deposit extension uses the wrong actor.

---

### Impact Explanation

Any unprivileged caller can deposit into a pool protected by `DepositAllowlistExtension` by routing through an allowlisted `owner` address. The pool admin's access control boundary is fully bypassed. Pools configured for KYC, regulatory compliance, or curated LP sets are rendered open to any depositor. This is a direct admin-boundary break: an unprivileged path circumvents a pool-admin-configured guard.

---

### Likelihood Explanation

Exploitation requires only a direct call to `pool.addLiquidity` with an allowlisted address as `owner`. No special privileges, flash loans, or complex setup are needed. Any caller who can observe the allowlist (public mapping) and implement the `metricOmmModifyLiquidityCallback` can exploit this immediately.

---

### Recommendation

Change `DepositAllowlistExtension.beforeAddLiquidity` to check `sender` (the actual depositor/caller) instead of `owner` (the position recipient):

```solidity
function beforeAddLiquidity(address sender, address, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
}
```

This mirrors the correct pattern already used in `SwapAllowlistExtension.beforeSwap`.

---

### Proof of Concept

```solidity
// Attacker (Bob) bypasses DepositAllowlistExtension on a pool that only allows Alice

// Setup: pool has DepositAllowlistExtension; Alice is allowlisted, Bob is not
depositExtension.setAllowedToDeposit(address(pool), alice, true);
// Bob is NOT allowlisted

// Bob calls addLiquidity directly with alice as owner
// Bob must implement metricOmmModifyLiquidityCallback to pay tokens
vm.prank(bob);
pool.addLiquidity(
    alice,          // owner — allowlisted, passes extension check
    salt,
    deltas,
    callbackData,   // Bob's callback pays the tokens
    extensionData
);

// Result: Bob deposited into a restricted pool
// Alice has shares she didn't request; Bob bypassed the allowlist
uint256 aliceShares = positionBinShares[keccak256(abi.encode(alice, salt, bin))];
assertGt(aliceShares, 0); // passes — allowlist bypassed
```

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** metric-periphery/contracts/extensions/DepositAllowlistExtension.sol (L32-42)
```text
  function beforeAddLiquidity(address, address owner, uint80, LiquidityDelta calldata, bytes calldata)
    external
    view
    override
    returns (bytes4)
  {
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][owner]) {
      revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
  }
```

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

**File:** metric-core/contracts/interfaces/IMetricOmmPool/IMetricOmmPoolActions.sol (L146-148)
```text
  /// @notice Mint shares across bins for `(owner, salt)`; pulls tokens via `IMetricOmmModifyLiquidityCallback` on `msg.sender`.
  /// @dev Callback receives native token amounts the pool expects; underpay reverts `InsufficientTokenBalance`. If `DEPOSIT_ALLOWLIST_PROVIDER` is set, `owner` must pass allowlist. `msg.sender` pays but need not equal `owner` (operator pattern).
  /// @param owner Position owner encoded in the pool’s position key.
```

**File:** metric-periphery/contracts/extensions/SwapAllowlistExtension.sol (L31-41)
```text
  function beforeSwap(address sender, address, bool, int128, uint128, uint256, uint128, uint128, bytes calldata)
    external
    view
    override
    returns (bytes4)
  {
    if (!allowAllSwappers[msg.sender] && !allowedSwapper[msg.sender][sender]) {
      revert IMetricOmmPoolActions.NotAllowedToSwap();
    }
    return IMetricOmmExtensions.beforeSwap.selector;
  }
```
