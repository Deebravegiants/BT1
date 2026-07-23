Audit Report

## Title
SwapAllowlistExtension Checks Router Address Instead of Actual User, Enabling Allowlist Bypass via MetricOmmSimpleRouter — (`metric-periphery/contracts/extensions/SwapAllowlistExtension.sol`)

## Summary
`SwapAllowlistExtension.beforeSwap` gates swaps on the `sender` parameter, which the pool sets to `msg.sender` of the `pool.swap()` call. When `MetricOmmSimpleRouter` is the direct caller of `pool.swap()`, the extension checks the router's address rather than the end user's address. If the pool admin adds the router to the allowlist to enable standard periphery swaps, every address — including those explicitly excluded — can bypass the restriction by routing through `MetricOmmSimpleRouter`. This is structurally inconsistent with `DepositAllowlistExtension`, which correctly checks the `owner` parameter (the actual position owner) and therefore works correctly through `MetricOmmPoolLiquidityAdder`.

## Finding Description
**Root cause — wrong actor checked in `beforeSwap`:**

`SwapAllowlistExtension.beforeSwap` checks `allowedSwapper[msg.sender][sender]`, where `sender` is the first argument passed by the pool: [1](#0-0) 

`MetricOmmPool.swap` passes `msg.sender` (the direct caller of `pool.swap`) as that first argument: [2](#0-1) 

`MetricOmmSimpleRouter.exactInputSingle` calls `pool.swap()` directly, making the router the `msg.sender` inside the pool: [3](#0-2) 

The router stores the actual end user in transient storage via `_setNextCallbackContext(..., msg.sender, ...)` for payment purposes, but this user identity is never forwarded to the extension. The extension therefore sees only the router address.

**Contrast with the correct deposit allowlist:**

`DepositAllowlistExtension.beforeAddLiquidity` ignores the first argument (`sender`) and checks the second argument (`owner`) — the actual position owner: [4](#0-3) 

The pool passes an explicit `owner` argument through `addLiquidity`, which `MetricOmmPoolLiquidityAdder` forwards from the caller-supplied parameter. The swap path has no equivalent: there is no authenticated "swapper" identity passed through `pool.swap()` beyond `msg.sender`.

**The two broken configurations:**

| Router in allowlist? | Result |
|---|---|
| Yes | Any user bypasses the allowlist by routing through `MetricOmmSimpleRouter` |
| No | Individually allowlisted users cannot use the router at all (DoS on the supported periphery path) |

Neither configuration achieves the intended policy of "only allowlisted users may swap, including via the router."

## Impact Explanation
A curated pool (e.g., KYC-only, institutional-only) that deploys `SwapAllowlistExtension` to restrict trading to specific counterparties cannot enforce that restriction when `MetricOmmSimpleRouter` is in scope. If the router is added to the allowlist to support the standard periphery path, every address — including those explicitly excluded — can trade at oracle prices in the pool. This constitutes an admin-boundary break: the pool admin's access-control policy is bypassed by an unprivileged path through the supported periphery router. The impact is that restricted users gain full swap access to a pool intended to be gated, executing trades at oracle-derived prices against LP capital that was deposited under the assumption of access control.

## Likelihood Explanation
Medium. The scenario requires a pool configured with `SwapAllowlistExtension` and the router added to the allowlist. Adding the router is the natural and expected step any pool admin would take when they want allowlisted users to be able to use the standard router. Once the router is allowlisted, the bypass is available to every address with no special privileges, no capital requirements beyond the swap amount, and no time constraints. The bypass is repeatable indefinitely.

## Recommendation
**Short term:** Pass the actual initiating user through the swap path. The router already stores `msg.sender` in transient storage before calling `pool.swap()`. One approach: the router could also write the payer/initiator into `extensionData` (authenticated by the router's own address as `msg.sender` of the extension call), and `SwapAllowlistExtension` could read and verify that hint when `msg.sender` (the pool) is a known router. Alternatively, the pool could accept an optional authenticated `swapper` hint in `extensionData` that the extension reads.

**Long term:** Adopt a consistent actor-identification model across all extension hooks. The deposit allowlist correctly uses `owner` (the economically attributed party); the swap allowlist should use an equivalent authenticated initiator, not the raw `msg.sender` of `pool.swap`. Document the actor semantics for each hook in the extension interface so extension authors cannot accidentally check the wrong address.

## Proof of Concept
```
1. Deploy MetricOmmPool with SwapAllowlistExtension configured on beforeSwap.
2. Pool admin calls setAllowedToSwap(pool, router, true)
   — intending to allow allowlisted users to swap via the router.
3. Pool admin does NOT call setAllowedToSwap(pool, attacker, true).
4. Attacker calls MetricOmmSimpleRouter.exactInputSingle({pool: pool, ...}).
5. Router calls pool.swap(recipient, zeroForOne, amountIn, priceLimitX64, "", extensionData).
6. Pool calls extension.beforeSwap(router, recipient, ...).
7. Extension checks allowedSwapper[pool][router] == true → passes.
8. Attacker's swap executes at oracle price in the curated pool.
   The per-user allowlist is completely bypassed.
```

Foundry test outline:
- Deploy pool with `SwapAllowlistExtension` as `beforeSwap` extension.
- `setAllowedToSwap(pool, address(router), true)`.
- Call `router.exactInputSingle(...)` from an address not in the allowlist.
- Assert the swap succeeds (no `NotAllowedToSwap` revert), confirming bypass.
- Repeat calling `pool.swap(...)` directly from the same address and assert it reverts with `NotAllowedToSwap`, confirming the bypass is router-specific.

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
