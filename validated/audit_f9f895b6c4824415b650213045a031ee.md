Audit Report

## Title
`DepositAllowlistExtension` gates on `owner` instead of `sender`, allowing any caller to bypass the deposit allowlist — (`metric-periphery/contracts/extensions/DepositAllowlistExtension.sol`)

## Summary

`DepositAllowlistExtension.beforeAddLiquidity` silently discards the `sender` argument and instead checks `allowedDepositor[msg.sender][owner]`, where `msg.sender` is the pool. Because `MetricOmmPool.addLiquidity` accepts a caller-controlled `owner` with no requirement that it equals `msg.sender`, any unprivileged address can supply an allowlisted address as `owner`, pass the check, pay the tokens themselves via the callback, and add liquidity to a restricted pool. The deposit allowlist is entirely unenforceable.

## Finding Description

`MetricOmmPool.addLiquidity` accepts an arbitrary `owner` with no `msg.sender == owner` guard:

```solidity
// MetricOmmPool.sol L182-196
function addLiquidity(
    address owner,   // ← caller-controlled, never validated against msg.sender
    ...
) external nonReentrant(PoolActions.ADD_LIQUIDITY) ... {
    _beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Added, amount1Added) = LiquidityLib.addLiquidity(
        _liquidityContext(), owner, salt, ...
    );
}
```

`ExtensionCalling._beforeAddLiquidity` correctly encodes both `sender` (`msg.sender`) and `owner` and passes them to the extension:

```solidity
// ExtensionCalling.sol L95-98
_callExtensionsInOrder(
    BEFORE_ADD_LIQUIDITY_ORDER,
    abi.encodeCall(IMetricOmmExtensions.beforeAddLiquidity, (sender, owner, salt, deltas, extensionData))
);
```

However, `DepositAllowlistExtension.beforeAddLiquidity` discards `sender` (unnamed first parameter) and checks `owner`:

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

Inside the extension, `msg.sender` is the pool. The check resolves to `allowedDepositor[pool][owner]`. An attacker (Bob) who is not allowlisted calls `pool.addLiquidity(owner=alice, ...)` where Alice is allowlisted. The extension evaluates `allowedDepositor[pool][alice]` → `true` → no revert. `LiquidityLib.addLiquidity` then credits shares to Alice's position key and calls `IMetricOmmModifyLiquidityCallback(msg.sender).metricOmmModifyLiquidityCallback(...)` — Bob pays the tokens. Bob's non-allowlisted funds enter the pool; the allowlist check was satisfied by Alice's status, not Bob's.

The `removeLiquidity` path correctly enforces `msg.sender != owner` → `revert NotPositionOwner()`, confirming the design intent that `sender` and `owner` are distinct and that the sender should be validated — but this guard is absent in `addLiquidity` and the extension fails to compensate.

## Impact Explanation

This is an admin-boundary break: a pool admin deploys `DepositAllowlistExtension` to enforce KYC/compliance or institutional access control on deposits. The bug makes this restriction unenforceable. Any unprivileged EOA or contract can deposit into the restricted pool by naming any allowlisted address as `owner`. Non-allowlisted funds enter the pool in violation of the admin-set invariant. The allowlist mapping `allowedDepositor` and `allowAllDepositors` are rendered meaningless for their stated purpose.

## Likelihood Explanation

`addLiquidity` is a public function requiring no special role. The only prerequisite is knowledge of one allowlisted address, which is trivially discoverable from the public `allowedDepositor` mapping or on-chain `AllowedToDepositSet` events. No flash loan, price manipulation, or privileged access is required. Any EOA or contract can execute the bypass in a single transaction, repeatably.

## Recommendation

Change `DepositAllowlistExtension.beforeAddLiquidity` to check `sender` (the actual depositor and token payer) rather than `owner` (the position beneficiary):

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

This mirrors the correct pattern: `sender` is the address that initiates the deposit and pays the tokens via the callback; `owner` is merely the beneficiary of the resulting LP shares.

## Proof of Concept

1. Pool is deployed with `DepositAllowlistExtension`. Admin calls `setAllowedToDeposit(pool, alice, true)`. Bob is not allowlisted.
2. Bob calls `pool.addLiquidity(owner=alice, salt=1, deltas, callbackData, "")` directly.
3. Pool calls `_beforeAddLiquidity(sender=bob, owner=alice, ...)` → extension receives `(bob, alice, ...)`.
4. Extension discards `bob`, evaluates `allowedDepositor[pool][alice]` → `true` → no revert.
5. `LiquidityLib.addLiquidity` credits shares to position key `keccak256(alice, 1, binIdx)`.
6. Pool calls `IMetricOmmModifyLiquidityCallback(bob).metricOmmModifyLiquidityCallback(...)` → Bob pays the tokens.
7. Bob has deposited into the restricted pool. The allowlist check was satisfied by Alice's allowlisted status, not Bob's. The access control invariant is broken.

Foundry test: deploy pool with extension, `vm.prank(admin); ext.setAllowedToDeposit(pool, alice, true);`, then `vm.prank(bob); pool.addLiquidity(alice, ...)` — assert no revert and that `positionBinShares[keccak256(alice,salt,bin)] > 0`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L144-154)
```text
      if (amount0Added > 0 || amount1Added > 0) {
        uint256 balance0Before = IERC20(ctx.token0).balanceOf(address(this));
        uint256 balance1Before = IERC20(ctx.token1).balanceOf(address(this));
        IMetricOmmModifyLiquidityCallback(msg.sender)
          .metricOmmModifyLiquidityCallback(amount0Added, amount1Added, callbackData);
        if (amount0Added > 0 && balance0Before + amount0Added > IERC20(ctx.token0).balanceOf(address(this))) {
          revert IMetricOmmPoolActions.InsufficientTokenBalance();
        }
        if (amount1Added > 0 && balance1Before + amount1Added > IERC20(ctx.token1).balanceOf(address(this))) {
          revert IMetricOmmPoolActions.InsufficientTokenBalance();
        }
```
