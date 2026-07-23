Audit Report

## Title
SwapAllowlistExtension Checks Router Identity Instead of End User, Allowing Any User to Bypass Swap Allowlist - (File: metric-periphery/contracts/extensions/SwapAllowlistExtension.sol)

## Summary
`SwapAllowlistExtension.beforeSwap` gates swaps by checking `allowedSwapper[pool][sender]`, where `sender` is the `msg.sender` of `pool.swap()`. When users route through `MetricOmmSimpleRouter`, `sender` is the router's address, not the end user's. Any pool that allowlists the router to support router-based swaps inadvertently grants swap access to every user who calls through the router, regardless of individual allowlist status.

## Finding Description
`SwapAllowlistExtension.beforeSwap` receives `sender` as its first argument and checks `allowedSwapper[msg.sender][sender]`, where `msg.sender` is the pool (the extension's caller): [1](#0-0) 

`MetricOmmPool.swap()` passes its own `msg.sender` as the `sender` argument to `_beforeSwap`: [2](#0-1) 

`ExtensionCalling._beforeSwap` ABI-encodes that `sender` verbatim as the first argument to the extension hook: [3](#0-2) 

When a user calls `MetricOmmSimpleRouter.exactInputSingle`, the router is `msg.sender` of `pool.swap()`: [4](#0-3) 

The extension therefore receives `sender = router`, evaluates `allowedSwapper[pool][router]`, and if the router is allowlisted, the check passes for every user who calls through the router — regardless of whether that user is individually allowlisted. For a pool with `SwapAllowlistExtension` to support router-based swaps at all, the pool admin must allowlist the router. Once the router is allowlisted, the allowlist is effectively open to the public via the router path. The existing guard (`allowedSwapper[pool][sender]`) is structurally insufficient because it cannot distinguish between the router acting on its own behalf and the router acting as a pass-through for an arbitrary end user.

## Impact Explanation
This is an admin-boundary break: the pool admin's per-address access control (intended for KYC, compliance, or restricted trading) is bypassed by an unprivileged path through the public `MetricOmmSimpleRouter` contract. Any user can trade on a restricted pool they were never individually allowlisted for, rendering `SwapAllowlistExtension` ineffective for any pool that also supports router-based swaps. The corrupted value is the extension's access-control decision: `allowedSwapper[pool][router]` evaluates to `true` when it should be gating on the end user's address.

## Likelihood Explanation
Medium. The bypass requires the router to be allowlisted, which is the natural and necessary configuration for any pool that wants to support router-based swaps. A pool admin who sets up `SwapAllowlistExtension` for compliance while also wanting to support the router would naturally allowlist the router, unknowingly opening the bypass to all users. The condition is self-inflicted by correct operational usage, not an exotic edge case.

## Recommendation
The extension must gate on the end user's address, not the immediate caller of `swap()`. Options:
1. **Pass the end user's address through `extensionData`**: the router encodes `msg.sender` into `extensionData`; the extension decodes and checks it. This requires router cooperation but keeps the extension self-contained.
2. **Two-level check**: introduce separate allowlist entries for routers (immediate callers) and end users (supplied via `extensionData`), so allowlisting the router does not implicitly grant access to all users.
3. **Document the limitation**: if the current behavior is intentional, document that allowlisting the router grants all users swap access, and provide a separate per-user gating mechanism for compliance use cases.

## Proof of Concept
1. Pool admin deploys a pool with `SwapAllowlistExtension` registered in `beforeSwap` order.
2. Pool admin calls `setAllowedToSwap(pool, router, true)` to enable router-based swaps.
3. Pool admin does **not** call `setAllowedToSwap(pool, attacker, true)`.
4. `attacker` calls `MetricOmmSimpleRouter.exactInputSingle(...)` targeting the restricted pool.
5. Router calls `pool.swap(recipient, zeroForOne, amount, priceLimit, "", extensionData)` — `msg.sender = router`.
6. Pool calls `_beforeSwap(router, ...)` → extension receives `sender = router`.
7. Extension evaluates `allowedSwapper[pool][router]` = `true` → no revert.
8. Swap executes successfully; `attacker` trades on a pool they were never individually allowlisted for. [5](#0-4) [4](#0-3)

### Citations

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

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L71-80)
```text
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
```
