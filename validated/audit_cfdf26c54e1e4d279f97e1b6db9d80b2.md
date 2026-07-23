### Title
SwapAllowlistExtension Bypass via MetricOmmSimpleRouter — Any User Can Circumvent Per-User Swap Allowlist - (File: `metric-periphery/contracts/extensions/SwapAllowlistExtension.sol`)

### Summary

`SwapAllowlistExtension.beforeSwap` gates swaps by checking the `sender` argument, which is `msg.sender` of the pool's `swap` call. When a user routes through the public `MetricOmmSimpleRouter`, `sender` becomes the router's address rather than the actual user's address. This creates an irreconcilable dilemma: if the router is allowlisted (to support router-mediated swaps for legitimate users), any non-allowlisted user can bypass the per-user gate by routing through the router.

### Finding Description

`SwapAllowlistExtension.beforeSwap` checks the `sender` parameter against the per-pool allowlist:

```solidity
function beforeSwap(address sender, address, bool, int128, uint128, uint256, uint128, uint128, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllSwappers[msg.sender] && !allowedSwapper[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToSwap();
    }
    return IMetricOmmExtensions.beforeSwap.selector;
}
``` [1](#0-0) 

The pool passes `msg.sender` of the `swap` call as `sender` to `_beforeSwap`:

```solidity
_beforeSwap(
    msg.sender,   // ← direct caller of pool.swap
    recipient,
    ...
);
``` [2](#0-1) 

When a user calls `MetricOmmSimpleRouter.exactInputSingle`, the router calls `pool.swap(...)` directly, making `msg.sender = router`:

```solidity
(int128 amount0Delta, int128 amount1Delta) = IMetricOmmPoolActions(params.pool)
    .swap(params.recipient, params.zeroForOne, ...);
``` [3](#0-2) 

The extension therefore sees `sender = router address`, not the actual end-user. The `ExtensionCalling._beforeSwap` faithfully forwards this `sender` to the extension: [4](#0-3) 

This creates a structural bypass: if the pool admin allowlists the router address (a necessary step to allow any router-mediated swap for legitimate users), every user — including non-allowlisted ones — can call `exactInputSingle` or `exactInput` through the router and pass the allowlist check, because the extension only sees the router's address.

The analog to the xINTX report is exact: just as `transfer()` was not disabled in `StakedINTX.sol`, the `MetricOmmSimpleRouter` is a public, permissionless contract that any user can call. The allowlist extension does not account for this intermediary, so the secondary-market-style bypass is available to any user who routes through the router.

### Impact Explanation

A pool configured with `SwapAllowlistExtension` to restrict trading to a curated set of addresses (e.g., KYC'd counterparties, whitelisted market makers, or protocol-controlled addresses) can be fully bypassed by any user routing through `MetricOmmSimpleRouter`. The non-allowlisted user receives the same swap output as an allowlisted user, with no penalty or restriction. This breaks the core access-control invariant of the extension and can lead to unauthorized trading, unauthorized extraction of LP value, or violation of regulatory/compliance requirements the pool admin intended to enforce.

### Likelihood Explanation

The `MetricOmmSimpleRouter` is the primary user-facing swap interface in the periphery. Any pool admin who wants to support router-mediated swaps for legitimate users must allowlist the router, at which point the bypass is immediately available to all users. Even if the admin does not allowlist the router, legitimate allowlisted users cannot use the router at all, making the extension incompatible with the standard periphery flow. The bypass is reachable by any unprivileged user with no special setup.

### Recommendation

The `SwapAllowlistExtension` must gate the actual end-user identity, not the direct caller of `pool.swap`. Two approaches:

1. **Pass original user through transient storage**: The router already uses transient storage to pass the payer address for the liquidity adder callback. A similar mechanism can store the original `msg.sender` of the router call and expose it via a standard interface that the extension reads during `beforeSwap`.

2. **Check both sender and a declared user**: Extend the `extensionData` convention so the router encodes the original user's address, and the extension verifies it. This requires a coordinated standard between router and extension.

The `DepositAllowlistExtension` does not share this flaw because it gates the `owner` parameter (the position recipient), which is correctly passed through even when `msg.sender` is the `MetricOmmPoolLiquidityAdder`. [5](#0-4) 

### Proof of Concept

```
Setup:
  - Deploy pool with SwapAllowlistExtension configured
  - Pool admin calls setAllowedToSwap(pool, router, true)
    (to allow legitimate users to swap via the router)
  - Pool admin does NOT call setAllowedToSwap(pool, attacker, true)

Attack:
  1. attacker (non-allowlisted EOA) calls:
       MetricOmmSimpleRouter.exactInputSingle({
           pool: pool,
           recipient: attacker,
           zeroForOne: true,
           amountIn: X,
           ...
       })
  2. Router calls pool.swap(...) with msg.sender = router
  3. Pool calls _beforeSwap(sender=router, ...)
  4. SwapAllowlistExtension.beforeSwap checks allowedSwapper[pool][router] → true → passes
  5. Swap executes; attacker receives output tokens

Result:
  attacker successfully swaps in a pool that was supposed to block them.
  The allowlist is completely bypassed.
``` [6](#0-5) [7](#0-6)

### Citations

**File:** metric-periphery/contracts/extensions/SwapAllowlistExtension.sol (L11-42)
```text
contract SwapAllowlistExtension is BaseMetricExtension, ISwapAllowlistExtension {
  mapping(address pool => mapping(address swapper => bool)) public allowedSwapper;
  mapping(address pool => bool) public allowAllSwappers;

  constructor(address factory_) BaseMetricExtension(factory_) {}

  function setAllowedToSwap(address pool_, address swapper, bool allowed) external onlyPoolAdmin(pool_) {
    allowedSwapper[pool_][swapper] = allowed;
    emit AllowedToSwapSet(pool_, swapper, allowed);
  }

  function setAllowAllSwappers(address pool_, bool allowed) external onlyPoolAdmin(pool_) {
    allowAllSwappers[pool_] = allowed;
    emit AllowAllSwappersSet(pool_, allowed);
  }

  function isAllowedToSwap(address pool_, address swapper) external view returns (bool) {
    return allowAllSwappers[pool_] || allowedSwapper[pool_][swapper];
  }

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
}
```

**File:** metric-core/contracts/MetricOmmPool.sol (L230-240)
```text
    _beforeSwap(
      msg.sender,
      recipient,
      zeroForOne,
      amountSpecified,
      priceLimitX64,
      packedSlot0Initial,
      bidPriceX64,
      askPriceX64,
      extensionData
    );
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L46-86)
```text
  function metricOmmSwapCallback(int256 amount0Delta, int256 amount1Delta, bytes calldata data) external override {
    if (amount0Delta <= 0 && amount1Delta <= 0) revert InvalidSwapDeltas();

    _requireExpectedCallbackCaller(msg.sender);

    uint8 callbackMode = _getCallbackMode();

    if (callbackMode == CALLBACK_MODE_JUST_PAY) {
      _justPayCallback(amount0Delta, amount1Delta);
      return;
    }
    if (callbackMode == CALLBACK_MODE_EXACT_OUTPUT_ITERATE) {
      _exactOutputIterateCallback(amount0Delta, amount1Delta, data);
      return;
    }
    revert InvalidCallbackMode(callbackMode);
  }

  // ============ External: exact input ============

  /// @inheritdoc IMetricOmmSimpleRouter
  function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut) {
    _checkDeadline(params.deadline);
    uint128 priceLimitX64 = MetricOmmSwapPath.normalizePriceLimit(params.zeroForOne, params.priceLimitX64);

    _setNextCallbackContext(params.pool, CALLBACK_MODE_JUST_PAY, msg.sender, params.tokenIn);
    (int128 amount0Delta, int128 amount1Delta) = IMetricOmmPoolActions(params.pool)
      .swap(
        params.recipient,
        params.zeroForOne,
        MetricOmmSwapInputs.asAmountSpecifiedIn(params.amountIn),
        priceLimitX64,
        "",
        params.extensionData
      );
    int128 out = MetricOmmSwapResults.extractAmountOut(params.zeroForOne, amount0Delta, amount1Delta);
    amountOut = MetricOmmSwapInputs.int128ToUint128(out);
    if (amountOut < params.amountOutMinimum) revert InsufficientOutput(amountOut, params.amountOutMinimum);

    _clearExpectedCallbackPool();
  }
```

**File:** metric-core/contracts/ExtensionCalling.sol (L149-177)
```text
  function _beforeSwap(
    address sender,
    address recipient,
    bool zeroForOne,
    int128 amountSpecified,
    uint128 priceLimitX64,
    uint256 packedSlot0Initial,
    uint128 bidPriceX64,
    uint128 askPriceX64,
    bytes calldata extensionData
  ) internal {
    _callExtensionsInOrder(
      BEFORE_SWAP_ORDER,
      abi.encodeCall(
        IMetricOmmExtensions.beforeSwap,
        (
          sender,
          recipient,
          zeroForOne,
          amountSpecified,
          priceLimitX64,
          packedSlot0Initial,
          bidPriceX64,
          askPriceX64,
          extensionData
        )
      )
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
