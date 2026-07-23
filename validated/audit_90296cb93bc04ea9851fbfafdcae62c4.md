Audit Report

## Title
SwapAllowlistExtension Checks Router Address Instead of Actual Swapper, Enabling Full Allowlist Bypass via MetricOmmSimpleRouter — (`metric-periphery/contracts/extensions/SwapAllowlistExtension.sol`)

## Summary

`SwapAllowlistExtension.beforeSwap` gates swaps by checking the `sender` argument, which the pool sets to its own `msg.sender`. When a user routes through `MetricOmmSimpleRouter`, the pool's `msg.sender` is the router contract, not the actual user. If the pool admin allowlists the router to permit legitimate users to trade through it, every non-allowlisted user can bypass the restriction by also routing through the router, rendering the allowlist completely ineffective for router-mediated swaps.

## Finding Description

`SwapAllowlistExtension.beforeSwap` checks `allowedSwapper[msg.sender][sender]`, where `msg.sender` is the pool (correct key) and `sender` is whoever called the pool: [1](#0-0) 

`MetricOmmSimpleRouter.exactInputSingle` calls `pool.swap(...)` directly, making the router the pool's `msg.sender`: [2](#0-1) 

The pool passes its own `msg.sender` as `sender` to `_beforeSwap`, which forwards it verbatim to every configured extension. When routing through the periphery, `sender` = router address, not the originating EOA.

**Call chain for a router-mediated swap (broken):**
```
EOA → MetricOmmSimpleRouter.exactInputSingle(params)
  router calls pool.swap(params.recipient, ...)
  pool: msg.sender = router
  pool calls _beforeSwap(sender=router, ...)
  SwapAllowlistExtension.beforeSwap(sender=router, ...)
    checks allowedSwapper[pool][router]  ← wrong actor
```

This creates an irresolvable dilemma for any pool admin who wants to use both the allowlist and the router:

| Router allowlisted? | Allowlisted user via router | Non-allowlisted user via router |
|---|---|---|
| No | Blocked (router not in list) | Blocked |
| Yes | Passes | **Passes — bypass** |

By contrast, `DepositAllowlistExtension.beforeAddLiquidity` correctly checks `owner` (the explicit position-owner parameter), not `sender` (the intermediary caller): [3](#0-2) 

The swap path has no equivalent explicit "swapper" parameter — it relies on `msg.sender`, which becomes the router when routing through periphery.

## Impact Explanation

A pool configured as a curated/restricted venue (e.g., KYC-only, institutional-only) using `SwapAllowlistExtension` is fully bypassable by any unprivileged user routing through `MetricOmmSimpleRouter`. The pool admin cannot simultaneously allow legitimate users to use the router and block non-allowlisted users. This constitutes broken core pool functionality: the allowlist access-control invariant — "a curated pool must enforce the same allowlist policy regardless of which supported public entrypoint reaches it" — is broken, exposing LP funds to unauthorized counterparties.

## Likelihood Explanation

High. `MetricOmmSimpleRouter` is the primary user-facing swap interface. Any pool that enables the swap allowlist and expects users to route through the official periphery is immediately vulnerable. No special conditions or privileged access are required — any EOA can call `exactInputSingle` on the router. The same issue applies to `exactInput`, `exactOutputSingle`, and `exactOutput`.

## Recommendation

The extension must check the actual initiating user, not the intermediary. Two approaches:

1. **Extension-data forwarding**: Have the router encode the original `msg.sender` into `extensionData` and have `SwapAllowlistExtension` decode and verify it (verifiable via `msg.sender == router`).
2. **Separate swapper parameter**: Add an explicit `swapper` field to the swap interface (analogous to `owner` in `addLiquidity`) so the pool can pass the true initiator through the extension chain independently of `msg.sender`.

The deposit allowlist's pattern of checking `owner` (not `sender`) is the correct model to follow.

## Proof of Concept

```solidity
// Pool admin sets up allowlist: only `alice` may swap
swapExtension.setAllowedToSwap(address(pool), alice, true);

// Alice swaps directly — PASSES (sender = alice, alice is allowlisted)
vm.prank(alice);
pool.swap(alice, zeroForOne, amount, priceLimit, "", "");

// Pool admin must allowlist the router so alice can use it:
swapExtension.setAllowedToSwap(address(pool), address(router), true);

// Alice swaps via router — PASSES (expected)
vm.prank(alice);
router.exactInputSingle(ExactInputSingleParams({
    pool: address(pool), recipient: alice, ...
}));

// Bob (not allowlisted) swaps via router — BYPASS:
vm.prank(bob);
router.exactInputSingle(ExactInputSingleParams({
    pool: address(pool), recipient: bob, ...
}));
// ↑ PASSES — bob bypasses the allowlist because sender = router, which is allowlisted
```

### Citations

**File:** metric-periphery/contracts/extensions/SwapAllowlistExtension.sol (L37-39)
```text
    if (!allowAllSwappers[msg.sender] && !allowedSwapper[msg.sender][sender]) {
      revert IMetricOmmPoolActions.NotAllowedToSwap();
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
