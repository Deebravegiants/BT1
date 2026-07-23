### Title
`DepositAllowlistExtension.beforeAddLiquidity` Ignores `sender` and Checks `owner`, Allowing Blocked Depositors to Bypass the Allowlist - (File: metric-periphery/contracts/extensions/DepositAllowlistExtension.sol)

### Summary

The `DepositAllowlistExtension` is documented as "Gates `addLiquidity` by depositor address, per pool." Its internal mapping is named `allowedDepositor` and its admin setter is `setAllowedToDeposit(address pool_, address depositor, bool allowed)`. Despite this, the `beforeAddLiquidity` hook silently drops the `sender` parameter (the actual `msg.sender` of the pool call — the token payer) and gates only on `owner` (the LP position recipient). Because `addLiquidity` explicitly supports an operator pattern where `msg.sender != owner`, any address blocked by the allowlist can still call `addLiquidity` with an allowed `owner`, paying tokens and routing the LP position to that address.

### Finding Description

`IMetricOmmExtensions.beforeAddLiquidity` receives two address arguments:

```
function beforeAddLiquidity(address sender, address owner, ...) external returns (bytes4);
```

`sender` is `msg.sender` of the pool call (the payer); `owner` is the position recipient. The pool passes both:

```solidity
// MetricOmmPool.sol line 191
_beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
```

`DepositAllowlistExtension.beforeAddLiquidity` discards `sender` entirely (unnamed first parameter) and checks only `owner`:

```solidity
// DepositAllowlistExtension.sol lines 32-42
function beforeAddLiquidity(address, address owner, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][owner]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
}
```

A blocked address `A` (not in `allowedDepositor`) can call:

```
pool.addLiquidity(owner = B, ...)   // B is on the allowlist
```

The extension sees `owner = B`, finds `allowedDepositor[pool][B] == true`, and passes. `A` pays the tokens; `B` receives the LP shares. If `A` controls `B` (a secondary wallet), `B` then calls `removeLiquidity` and returns the tokens to `A`. The allowlist is fully circumvented.

Compare with `SwapAllowlistExtension`, which correctly checks `sender`:

```solidity
// SwapAllowlistExtension.sol line 37
if (!allowAllSwappers[msg.sender] && !allowedSwapper[msg.sender][sender]) {
    revert IMetricOmmPoolActions.NotAllowedToSwap();
}
```

### Impact Explanation

The `DepositAllowlistExtension` is the primary on-chain mechanism for pools that require KYC/compliance gating on deposits. With this bug, any address excluded from the allowlist can still deposit into the pool by routing through an allowed `owner` address it controls. The allowlist provides no real barrier: blocked addresses can deposit, earn LP fees, and withdraw — defeating the entire purpose of the extension. Pools relying on this extension for regulatory compliance are exposed to unrestricted participation by blocked parties.

### Likelihood Explanation

Exploitation requires no special privileges, no flash loans, and no complex setup. Any blocked address that controls (or can coordinate with) a single allowlisted address can execute the bypass in one transaction via `addLiquidity`. The operator pattern is explicitly supported by the periphery (`MetricOmmPoolLiquidityAdder.addLiquidityExactShares` with a separate `owner` parameter), making the attack surface wide and the exploit trivial.

### Recommendation

Check `sender` (the actual caller/payer) instead of `owner` in `beforeAddLiquidity`:

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

This mirrors the correct pattern already used in `SwapAllowlistExtension`.

### Proof of Concept

1. Deploy a pool with `DepositAllowlistExtension` configured for `beforeAddLiquidity`.
2. Pool admin calls `setAllowedToDeposit(pool, B, true)` — only `B` is allowed; `A` is not.
3. `A` (blocked) calls `pool.addLiquidity(owner = B, salt, deltas, callbackData, "")`.
4. Extension receives `sender = A` (ignored), `owner = B` (allowed) → passes.
5. `A` pays tokens via `metricOmmModifyLiquidityCallback`; `B` receives LP shares.
6. `B` calls `pool.removeLiquidity(owner = B, ...)` → tokens returned to `B`, forwarded to `A`.
7. `A` has effectively deposited and withdrawn from the pool despite being blocked. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** metric-periphery/contracts/extensions/DepositAllowlistExtension.sol (L10-14)
```text
/// @title DepositAllowlistExtension
/// @notice Gates `addLiquidity` by depositor address, per pool.
contract DepositAllowlistExtension is BaseMetricExtension, IDepositAllowlistExtension {
  mapping(address pool => mapping(address depositor => bool)) public allowedDepositor;
  mapping(address pool => bool) public allowAllDepositors;
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

**File:** metric-core/contracts/interfaces/extensions/IMetricOmmExtensions.sol (L14-20)
```text
  function beforeAddLiquidity(
    address sender,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata extensionData
  ) external returns (bytes4);
```

**File:** metric-core/contracts/MetricOmmPool.sol (L188-196)
```text
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
