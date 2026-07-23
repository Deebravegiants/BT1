Looking at the `ExtensionCalling.sol` and `MetricOmmPool.sol` contracts, I can identify a direct structural analog to M-16.

---

### Title
Immutable Extension With Reverting External Dependency Permanently Bricks All Pool Operations, Locking LP Funds — (`metric-core/contracts/ExtensionCalling.sol`)

### Summary

`_callExtensionsInOrder` iterates through up to 7 immutable extension addresses and calls each one with no error isolation. If any single extension's external dependency reverts (due to an upgrade, deprecation, or compromise of a contract the extension depends on), every pool operation — `swap`, `addLiquidity`, and `removeLiquidity` — permanently reverts. Because extensions are stored as constructor-time immutables, there is no governance path to remove or replace a broken extension, and LP principal becomes permanently locked.

### Finding Description

`ExtensionCalling._callExtensionsInOrder` dispatches to each configured extension in sequence:

```solidity
// metric-core/contracts/ExtensionCalling.sol  lines 75-86
function _callExtensionsInOrder(uint256 order, bytes memory data) private {
    if (order == 0) return;
    while (true) {
        uint256 extensionIndex = order & 0x7;
        if (extensionIndex == 0) break;
        address extension = _extensionAddress(extensionIndex);
        if (extension == address(0)) revert PanicEmptyExtension();
        CallExtension.callExtension(extension, data);   // ← no try/catch
        order >>= 3;
    }
}
``` [1](#0-0) 

`CallExtension.callExtension` is invoked without a `try/catch` wrapper. A revert from any extension propagates directly to the caller.

This helper is invoked unconditionally inside every user-facing hook:

| Hook | Called from |
|---|---|
| `_beforeSwap` / `_afterSwap` | `swap`, `simulateSwapAndRevert` |
| `_beforeAddLiquidity` / `_afterAddLiquidity` | `addLiquidity` |
| `_beforeRemoveLiquidity` / `_afterRemoveLiquidity` | `removeLiquidity` | [2](#0-1) 

All seven extension slots are stored as `address internal immutable` values set once in the constructor and never changeable:

```solidity
// metric-core/contracts/ExtensionCalling.sol  lines 17-23
address internal immutable EXTENSION_1;
...
address internal immutable EXTENSION_7;
``` [3](#0-2) 

`removeLiquidity` in `MetricOmmPool` carries no `whenNotPaused` guard, but it still calls both `_beforeRemoveLiquidity` and `_afterRemoveLiquidity`:

```solidity
// metric-core/contracts/MetricOmmPool.sol  lines 199-212
function removeLiquidity(...) external nonReentrant(PoolActions.REMOVE_LIQUIDITY) ... {
    ...
    _beforeRemoveLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Removed, amount1Removed) = LiquidityLib.removeLiquidity(...);
    _afterRemoveLiquidity(msg.sender, owner, salt, deltas, amount0Removed, amount1Removed, extensionData);
}
``` [4](#0-3) 

There is no emergency-withdrawal path that bypasses extensions, and the factory's only pool-level lever is `setPause` / `collectFees`, neither of which helps LPs retrieve their tokens when extensions revert. [5](#0-4) 

### Impact Explanation

A pool that registers an extension which calls any external contract (a velocity-guard oracle, a whitelist registry, a stop-loss price feed) is permanently bricked if that external contract is upgraded to change its ABI, paused for an extended period, or self-destructed. Because extensions are immutable and every user-facing function routes through them, the following become permanently impossible:

- LPs withdrawing their token0/token1 principal (`removeLiquidity`)
- Traders executing swaps (`swap`)
- New liquidity being added (`addLiquidity`)

The factory cannot replace the extension; pausing the pool does not help LPs; there is no escape hatch. This is a direct loss of LP principal — identical in structure to the Reserve Protocol M-16 finding where a single broken collateral permanently locked all RToken redemptions.

### Likelihood Explanation

Extensions are set at pool-creation time by the pool deployer and are intended to call external contracts (gates, stop-losses, velocity guards per the README). Any of those external contracts can fail post-deployment through routine upgrades, emergency freezes, or exploits — all scenarios explicitly enumerated in M-16. The trigger requires no privileged action after pool creation; it is an unprivileged external event.

### Recommendation

1. **Wrap extension calls in `try/catch`** inside `_callExtensionsInOrder`. On revert, either skip the extension (with an event) or revert with a structured error that the factory can act on.
2. **Add a factory-controlled emergency-disable flag per extension slot** so a broken extension can be bypassed without redeploying the pool.
3. **Provide an extension-bypass path for `removeLiquidity`** (e.g., when `pauseLevel == 2`) so LPs can always recover principal even if hooks are broken.

### Proof of Concept

1. Pool is deployed with `EXTENSION_1` pointing to a velocity-guard contract that calls an external price oracle.
2. The oracle contract is upgraded; its `getPrice()` function is renamed, causing the extension to revert on every call.
3. `BEFORE_REMOVE_LIQUIDITY_ORDER` includes extension index 1, so `_callExtensionsInOrder` calls `EXTENSION_1`, which reverts.
4. Every call to `removeLiquidity` reverts at `_beforeRemoveLiquidity`.
5. Every call to `swap` reverts at `_beforeSwap`.
6. Extensions are immutable — no governance action can remove `EXTENSION_1`.
7. All LP token0/token1 balances tracked in `binTotals` are permanently inaccessible. [1](#0-0) [4](#0-3)

### Citations

**File:** metric-core/contracts/ExtensionCalling.sol (L17-23)
```text
  address internal immutable EXTENSION_1;
  address internal immutable EXTENSION_2;
  address internal immutable EXTENSION_3;
  address internal immutable EXTENSION_4;
  address internal immutable EXTENSION_5;
  address internal immutable EXTENSION_6;
  address internal immutable EXTENSION_7;
```

**File:** metric-core/contracts/ExtensionCalling.sol (L75-86)
```text
  function _callExtensionsInOrder(uint256 order, bytes memory data) private {
    if (order == 0) return;

    while (true) {
      uint256 extensionIndex = order & 0x7;
      if (extensionIndex == 0) break;
      address extension = _extensionAddress(extensionIndex);
      if (extension == address(0)) revert PanicEmptyExtension();
      CallExtension.callExtension(extension, data);
      order >>= 3;
    }
  }
```

**File:** metric-core/contracts/ExtensionCalling.sol (L88-147)
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

  function _afterAddLiquidity(
    address sender,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    uint256 amount0Added,
    uint256 amount1Added,
    bytes calldata extensionData
  ) internal {
    _callExtensionsInOrder(
      AFTER_ADD_LIQUIDITY_ORDER,
      abi.encodeCall(
        IMetricOmmExtensions.afterAddLiquidity, (sender, owner, salt, deltas, amount0Added, amount1Added, extensionData)
      )
    );
  }

  function _beforeRemoveLiquidity(
    address sender,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata extensionData
  ) internal {
    _callExtensionsInOrder(
      BEFORE_REMOVE_LIQUIDITY_ORDER,
      abi.encodeCall(IMetricOmmExtensions.beforeRemoveLiquidity, (sender, owner, salt, deltas, extensionData))
    );
  }

  function _afterRemoveLiquidity(
    address sender,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    uint256 amount0Removed,
    uint256 amount1Removed,
    bytes calldata extensionData
  ) internal {
    _callExtensionsInOrder(
      AFTER_REMOVE_LIQUIDITY_ORDER,
      abi.encodeCall(
        IMetricOmmExtensions.afterRemoveLiquidity,
        (sender, owner, salt, deltas, amount0Removed, amount1Removed, extensionData)
      )
    );
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

**File:** metric-core/contracts/MetricOmmPool.sol (L455-461)
```text
  function setPause(uint8 newLevel) external onlyFactory {
    if (newLevel > 2) revert InvalidPauseLevel();
    if (newLevel == pauseLevel) return;
    uint8 prev = pauseLevel;
    pauseLevel = newLevel;
    emit PauseLevelUpdated(prev, newLevel);
  }
```
