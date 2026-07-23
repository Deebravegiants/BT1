### Title
`DepositAllowlistExtension` Checks `owner` Instead of `sender`, Allowing Un-Allowlisted Operators to Bypass Deposit Restrictions — (`metric-periphery/contracts/extensions/DepositAllowlistExtension.sol`)

---

### Summary

`DepositAllowlistExtension.beforeAddLiquidity` silently discards the `sender` argument (the actual caller/operator) and only validates `owner` (the position owner) against the allowlist. Because `addLiquidity` explicitly supports an operator pattern where `msg.sender ≠ owner`, any un-allowlisted operator can deposit into a restricted pool on behalf of an allowlisted owner, fully bypassing the intended access control.

---

### Finding Description

`MetricOmmPool.addLiquidity` is documented to support an operator pattern:

> `msg.sender` pays but need not equal `owner` (operator pattern). [1](#0-0) 

When `addLiquidity` is called, the pool invokes the `beforeAddLiquidity` extension hook, passing both `sender` (the actual `msg.sender` / operator) and `owner` (the position owner): [2](#0-1) 

The `DepositAllowlistExtension.beforeAddLiquidity` implementation, however, silently discards the first parameter (`sender`) and only checks `owner`:

```solidity
function beforeAddLiquidity(address, address owner, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][owner]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
}
``` [3](#0-2) 

The `sender` (the actual token payer / operator) is never validated. This is the direct analog to M-19: the wrong address is checked in the authorization gate.

---

### Impact Explanation

Two broken invariants result:

1. **Allowlist bypass by un-allowlisted operators**: Any address not on the allowlist can call `pool.addLiquidity(owner = allowlistedUser, ...)`. The extension checks `allowedDepositor[pool][allowlistedUser]` → passes. The un-allowlisted operator pays tokens via callback and mints shares to the allowlisted owner's position. The pool admin's intended restriction on who may deposit is silently defeated.

2. **Operator allowlisting is impossible**: If a pool admin intends to allowlist a specific operator contract (e.g., `MetricOmmPoolLiquidityAdder`) as the permitted depositor, this cannot be expressed through the extension — the extension never reads `sender`, so allowlisting the operator address has no effect.

The `MetricOmmPoolLiquidityAdder` explicitly uses the operator pattern, passing `owner` as a separate argument from `msg.sender`: [4](#0-3) 

Any pool that deploys `DepositAllowlistExtension` to enforce a restricted depositor set has that restriction broken for all operator-pattern callers.

---

### Likelihood Explanation

`DepositAllowlistExtension` is a production extension explicitly provided in `metric-periphery` for pool admins to restrict deposits. The operator pattern (`msg.sender ≠ owner`) is the primary use-case of `MetricOmmPoolLiquidityAdder`, which is the canonical periphery entry point. Any pool that combines both — a deposit allowlist and the liquidity adder — is immediately affected. No privileged setup is required beyond a pool admin deploying the extension (a normal, documented deployment path).

---

### Recommendation

Change `beforeAddLiquidity` to check `sender` (the actual caller/operator) instead of `owner`:

```solidity
function beforeAddLiquidity(address sender, address owner, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
}
```

If the intent is to gate by position owner (not operator), the parameter naming and NatSpec must be corrected to reflect that, and the `isAllowedToDeposit` view function updated accordingly. Either way, the current mismatch between the discarded `sender` parameter and the `owner`-only check must be resolved.

---

### Proof of Concept

1. Deploy pool with `DepositAllowlistExtension` attached to `beforeAddLiquidity`.
2. Pool admin allowlists `alice`: `extension.setAllowedToDeposit(pool, alice, true)`.
3. `bob` (not allowlisted) calls `pool.addLiquidity(owner=alice, salt=0, deltas=..., callbackData=..., extensionData=...)` directly.
4. Pool calls `extension.beforeAddLiquidity(sender=bob, owner=alice, ...)`.
5. Extension checks `allowedDepositor[pool][alice]` → `true` → **passes without checking `bob`**.
6. Pool calls `bob.metricOmmModifyLiquidityCallback(...)` → `bob` pays tokens.
7. Shares are minted to `alice`'s position key.
8. `bob` successfully deposited into a restricted pool despite never being allowlisted.

The same path applies when `MetricOmmPoolLiquidityAdder` is the `sender` and the pool admin intended to allowlist only specific operators: the adder's address is never checked, so the allowlist provides no restriction on which operators may deposit. [3](#0-2) [5](#0-4) [6](#0-5)

### Citations

**File:** metric-core/contracts/interfaces/IMetricOmmPool/IMetricOmmPoolActions.sol (L146-148)
```text
  /// @notice Mint shares across bins for `(owner, salt)`; pulls tokens via `IMetricOmmModifyLiquidityCallback` on `msg.sender`.
  /// @dev Callback receives native token amounts the pool expects; underpay reverts `InsufficientTokenBalance`. If `DEPOSIT_ALLOWLIST_PROVIDER` is set, `owner` must pass allowlist. `msg.sender` pays but need not equal `owner` (operator pattern).
  /// @param owner Position owner encoded in the pool’s position key.
```

**File:** metric-core/contracts/ExtensionCalling.sol (L88-99)
```text
  function _beforeAddLiquidity(
    address sender,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata extensionData
  ) internal {
    _callExtensionsInOrder(
      BEFORE_ADD_LIQUIDITY_ORDER,
      abi.encodeCall(IMetricOmmExtensions.beforeAddLiquidity, (sender, owner, salt, deltas, extensionData))
    );
  }
```

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

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L56-68)
```text
  function addLiquidityExactShares(
    address pool,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    uint256 maxAmountToken0,
    uint256 maxAmountToken1,
    bytes calldata extensionData
  ) external payable override returns (uint256 amount0Added, uint256 amount1Added) {
    _validateOwner(owner);
    _validateDeltas(deltas);
    return _addLiquidity(pool, owner, salt, deltas, msg.sender, maxAmountToken0, maxAmountToken1, extensionData);
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

**File:** metric-core/contracts/MetricOmmPool.sol (L206-206)
```text
    if (msg.sender != owner) revert NotPositionOwner();
```
