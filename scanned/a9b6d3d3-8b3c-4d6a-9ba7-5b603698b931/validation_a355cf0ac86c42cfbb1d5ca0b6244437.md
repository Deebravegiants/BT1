### Title
`DepositAllowlistExtension` Gates on `owner` Instead of `sender`, Allowing Non-Allowlisted Users to Bypass the Deposit Guard — (`metric-periphery/contracts/extensions/DepositAllowlistExtension.sol`)

---

### Summary

`DepositAllowlistExtension.beforeAddLiquidity` silently discards the `sender` argument (the actual caller and token payer) and checks only the `owner` argument (the position beneficiary). Because `MetricOmmPool.addLiquidity` explicitly supports an operator pattern where `msg.sender ≠ owner`, any non-allowlisted address can call `addLiquidity(owner = <any allowlisted address>, ...)`, pass the allowlist check, pay tokens from its own balance, and mint LP shares into the allowlisted address — completely defeating the gate.

---

### Finding Description

`MetricOmmPool.addLiquidity` accepts a caller-supplied `owner` that need not equal `msg.sender`:

```solidity
// MetricOmmPool.sol L182-195
function addLiquidity(
    address owner,          // position beneficiary — caller-supplied
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (...) {
    ...
    _beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
    ...
}
```

The pool passes both `msg.sender` (as `sender`) and `owner` to the extension hook. `DepositAllowlistExtension.beforeAddLiquidity` receives both but discards `sender` entirely:

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

The first parameter — `sender`, the actual payer — is unnamed and ignored. Only `owner` is checked. This is the inverse of the correct behavior: the allowlist is supposed to gate the depositor (the entity paying tokens), not the position beneficiary.

Compare with `SwapAllowlistExtension`, which correctly gates on `sender`:

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

The deposit extension has the exact opposite binding — `sender` is discarded, `owner` is checked — making the deposit allowlist trivially bypassable.

---

### Impact Explanation

1. **Allowlist bypass**: Any non-allowlisted address can call `pool.addLiquidity(owner = <any allowlisted address>, ...)` directly. The hook checks `owner` (allowlisted → passes), the non-allowlisted caller pays tokens via the modify-liquidity callback, and LP shares are minted to the allowlisted address. The gate is completely defeated.

2. **Forced LP positions / griefing**: The allowlisted address receives LP shares it never requested. If the allowlisted address is a smart contract without a `removeLiquidity` path, the underlying tokens are permanently trapped in the pool under that address's position key.

3. **Allowlist semantics inverted**: The pool admin's intent — "only approved depositors may inject liquidity" — is not enforced. Non-approved actors can freely inject tokens and alter pool depth, affecting swap pricing and fee accrual for all LPs.

---

### Likelihood Explanation

- The `addLiquidity` operator pattern (`msg.sender ≠ owner`) is explicitly documented and supported by the pool interface.
- Any non-allowlisted address can exploit this with a single direct call to the pool — no special setup, flash loan, or privileged access required.
- The attacker only needs to know one allowlisted address (e.g., any existing LP whose position is publicly visible on-chain).
- The `MetricOmmPoolLiquidityAdder` also exposes `addLiquidityExactShares(pool, owner, ...)` which routes through the same broken hook, widening the attack surface.

---

### Recommendation

Check `sender` (the actual payer/caller) instead of `owner` in `beforeAddLiquidity`:

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

This mirrors the correct pattern already used in `SwapAllowlistExtension.beforeSwap`. If the intent is to gate both the payer and the position beneficiary, check both `sender` and `owner`.

---

### Proof of Concept

```
Setup:
  - Pool configured with DepositAllowlistExtension
  - allowedDepositor[pool][alice] = true   (alice is allowlisted)
  - bob is NOT allowlisted

Attack:
  1. bob calls pool.addLiquidity(
         owner        = alice,   // allowlisted — hook passes
         salt         = 99,
         deltas       = { binIdxs: [4], shares: [10_000] },
         callbackData = "",
         extensionData = ""
     )
  2. beforeAddLiquidity hook checks allowedDepositor[pool][alice] → true → no revert
  3. Pool calls bob.metricOmmModifyLiquidityCallback(amount0, amount1, "")
     bob transfers tokens to the pool from his own balance
  4. Pool mints 10_000 shares in bin 4 under key (alice, salt=99)

Result:
  - bob (non-allowlisted) successfully deposited tokens into the pool
  - alice holds an LP position she did not create
  - The deposit allowlist provided zero protection against bob
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** metric-core/contracts/interfaces/IMetricOmmPool/IMetricOmmPoolActions.sol (L146-148)
```text
  /// @notice Mint shares across bins for `(owner, salt)`; pulls tokens via `IMetricOmmModifyLiquidityCallback` on `msg.sender`.
  /// @dev Callback receives native token amounts the pool expects; underpay reverts `InsufficientTokenBalance`. If `DEPOSIT_ALLOWLIST_PROVIDER` is set, `owner` must pass allowlist. `msg.sender` pays but need not equal `owner` (operator pattern).
  /// @param owner Position owner encoded in the pool’s position key.
```
