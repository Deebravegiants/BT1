### Title
Immutable Extension Addresses With No Recovery Mechanism Can Permanently Lock LP Withdrawals or Block Swaps — (`metric-core/contracts/ExtensionCalling.sol`)

### Summary

Extension contract addresses are stored as `immutable` values in `MetricOmmPool`. `_callExtensionsInOrder` propagates every extension revert directly to the caller with no try/catch. Because extensions cannot be replaced or disabled after deployment, a single extension that begins reverting — due to a bug, proxy upgrade, or self-destruct — permanently bricks every pool operation that extension is wired to. If the broken extension is on the `removeLiquidity` path, LP principal is locked with no on-chain recovery path.

### Finding Description

`ExtensionCalling` stores up to seven extension addresses as Solidity `immutable` values set once in the constructor:

```solidity
address internal immutable EXTENSION_1;
// … EXTENSION_2 … EXTENSION_7
uint256 internal immutable BEFORE_REMOVE_LIQUIDITY_ORDER;
uint256 internal immutable AFTER_REMOVE_LIQUIDITY_ORDER;
```

`_callExtensionsInOrder` iterates the packed order word and calls each extension via `CallExtension.callExtension`:

```solidity
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
```

`CallExtension.callExtension` propagates the revert unconditionally:

```solidity
(bool success, bytes memory result) = extension.call(data);
if (!success) {
    if (result.length > 0) {
        assembly ("memory-safe") { revert(add(result, 32), mload(result)) }
    }
    revert ExtensionCallFailed();
}
```

`removeLiquidity` deliberately omits `whenNotPaused` so LPs can exit during a pause. However, it still calls `_beforeRemoveLiquidity` and `_afterRemoveLiquidity`:

```solidity
function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    nonReentrant(PoolActions.REMOVE_LIQUIDITY)
    returns (uint256 amount0Removed, uint256 amount1Removed)
{
    …
    _beforeRemoveLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Removed, amount1Removed) = LiquidityLib.removeLiquidity(…);
    _afterRemoveLiquidity(msg.sender, owner, salt, deltas, amount0Removed, amount1Removed, extensionData);
}
```

If an extension wired to `BEFORE_REMOVE_LIQUIDITY_ORDER` or `AFTER_REMOVE_LIQUIDITY_ORDER` begins reverting, every `removeLiquidity` call reverts. Because the extension address is immutable, there is no factory or admin path to replace or bypass it. The pool admin can only pause the pool (blocking `swap`), but that does not help — `removeLiquidity` is intentionally unpaused, yet the extension gate still fires.

The same structural issue applies to `swap` (via `_beforeSwap` / `_afterSwap`) and `addLiquidity` (via `_beforeAddLiquidity` / `_afterAddLiquidity`). A broken extension on the `afterSwap` path — for example `OracleValueStopLossExtension`, which performs complex Q64.64 arithmetic and reads live pool state — permanently blocks all swaps with no recovery.

The factory validates extension configuration at deployment (no duplicate addresses, valid order encoding) but does **not** validate that each extension implements the hooks it is wired to. `BaseMetricExtension` defaults every unimplemented hook to `revert ExtensionNotImplemented()`, so a pool wired with an extension on `BEFORE_REMOVE_LIQUIDITY_ORDER` that does not override `beforeRemoveLiquidity` will have `removeLiquidity` permanently revert from the first call.

### Impact Explanation

| Broken extension path | Immediate effect | Recovery |
|---|---|---|
| `beforeSwap` / `afterSwap` | All swaps permanently revert | None — extension is immutable |
| `beforeAddLiquidity` / `afterAddLiquidity` | All deposits permanently revert | None |
| `beforeRemoveLiquidity` / `afterRemoveLiquidity` | All LP withdrawals permanently revert; principal locked | None |

The worst case — an extension on the `removeLiquidity` path — causes pool insolvency: the pool holds LP-owned token balances that can never be claimed. This matches the "broken core pool functionality causing loss of funds or unusable withdraw/swap/liquidity flows" impact gate.

### Likelihood Explanation

Extensions are external contracts. Any of the following non-malicious events can cause a previously working extension to begin reverting:

1. **Proxy upgrade** — `OracleValueStopLossExtension` or any shared extension deployed as a proxy can have its implementation replaced, changing or removing function selectors.
2. **Self-destruct** — if the extension deployer key is compromised, the extension contract can be destroyed; all calls to a destroyed address return empty data, causing `InvalidExtensionResponse` in `CallExtension`.
3. **Runtime arithmetic revert** — `OracleValueStopLossExtension._afterSwapOracleStopLoss` performs unchecked Q64.64 multiplications and divisions against live pool state; edge-case bin metrics (zero shares, extreme watermarks) can trigger overflow or division-by-zero.
4. **External dependency failure** — extensions that call `PoolStateLibrary` or other on-chain state readers can revert if the pool's storage layout changes in a future upgrade.

None of these require malicious pool setup; they are operational risks for any production pool with extensions.

### Recommendation

1. **Wrap extension calls in try/catch for non-critical hooks** (e.g., `afterSwap`, `afterAddLiquidity`, `afterRemoveLiquidity`). Only `before*` hooks that enforce access control need hard reverts.
2. **Add a factory-level emergency extension override** — a mapping from pool to a disabled-extension bitmask that `_callExtensionsInOrder` checks before calling each slot.
3. **Alternatively, store extension addresses in mutable factory storage** (keyed by pool) rather than pool immutables, so the factory owner can replace a broken extension under a timelock.
4. **Validate at deployment** that each extension actually implements every hook it is wired to (call each hook in a `try` block during `createPool` initialization).

### Proof of Concept

```
1. Deploy MetricOmmPool with ExtensionX wired to BEFORE_REMOVE_LIQUIDITY_ORDER.
2. LPs add liquidity; pool accumulates token0 and token1 balances.
3. ExtensionX begins reverting (proxy upgrade, self-destruct, or arithmetic edge case).
4. Any LP calls removeLiquidity(owner, salt, deltas, "").
   → _beforeRemoveLiquidity fires → CallExtension.callExtension(ExtensionX, …) → revert.
5. removeLiquidity permanently reverts for all LPs.
6. Pool admin calls factory.pausePool(pool) → pause level 1.
   → swap is blocked, but removeLiquidity still calls _beforeRemoveLiquidity → still reverts.
7. No on-chain path exists to replace EXTENSION_1…7 (immutable) or skip the broken slot.
8. All LP principal is permanently locked in the pool contract.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** metric-core/contracts/ExtensionCalling.sol (L17-35)
```text
  address internal immutable EXTENSION_1;
  address internal immutable EXTENSION_2;
  address internal immutable EXTENSION_3;
  address internal immutable EXTENSION_4;
  address internal immutable EXTENSION_5;
  address internal immutable EXTENSION_6;
  address internal immutable EXTENSION_7;
  /// @dev Order of extension calls for before add liquidity.
  uint256 internal immutable BEFORE_ADD_LIQUIDITY_ORDER;
  /// @dev Order of extension calls for after add liquidity.
  uint256 internal immutable AFTER_ADD_LIQUIDITY_ORDER;
  /// @dev Order of extension calls for before remove liquidity.
  uint256 internal immutable BEFORE_REMOVE_LIQUIDITY_ORDER;
  /// @dev Order of extension calls for after remove liquidity.
  uint256 internal immutable AFTER_REMOVE_LIQUIDITY_ORDER;
  /// @dev Order of extension calls for before swap.
  uint256 internal immutable BEFORE_SWAP_ORDER;
  /// @dev Order of extension calls for after swap.
  uint256 internal immutable AFTER_SWAP_ORDER;
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

**File:** metric-core/contracts/ExtensionCalling.sol (L118-147)
```text
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

**File:** metric-core/contracts/libraries/CallExtension.sol (L8-32)
```text
  function callExtension(address extension, bytes memory data) internal {
    (bool success, bytes memory result) = extension.call(data);
    if (!success) {
      if (result.length > 0) {
        assembly ("memory-safe") {
          revert(add(result, 32), mload(result))
        }
      }
      revert ExtensionCallFailed();
    }
    if (result.length < 32) {
      revert InvalidExtensionResponse();
    }
    bytes4 returnedSelector;
    assembly ("memory-safe") {
      returnedSelector := mload(add(result, 32))
    }
    bytes4 expectedSelector;
    assembly ("memory-safe") {
      expectedSelector := mload(add(data, 32))
    }
    if (returnedSelector != expectedSelector) {
      revert InvalidExtensionResponse();
    }
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

**File:** metric-periphery/contracts/extensions/base/BaseMetricExtension.sol (L63-79)
```text
  function beforeRemoveLiquidity(address, address, uint80, LiquidityDelta calldata, bytes calldata)
    external
    virtual
    onlyPool
    returns (bytes4)
  {
    revert ExtensionNotImplemented();
  }

  function afterRemoveLiquidity(address, address, uint80, LiquidityDelta calldata, uint256, uint256, bytes calldata)
    external
    virtual
    onlyPool
    returns (bytes4)
  {
    revert ExtensionNotImplemented();
  }
```
