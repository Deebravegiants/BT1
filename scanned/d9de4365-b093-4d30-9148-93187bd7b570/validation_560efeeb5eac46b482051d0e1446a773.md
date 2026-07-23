### Title
SwapAllowlistExtension Checks Router Identity Instead of End User, Allowing Any User to Bypass Swap Allowlist - (File: metric-periphery/contracts/extensions/SwapAllowlistExtension.sol)

### Summary
`SwapAllowlistExtension.beforeSwap` receives `sender` = `msg.sender` of the pool's `swap()` call. When users route through `MetricOmmSimpleRouter`, `sender` is the router's address, not the end user's. If the router is allowlisted — which is required for any pool that wants to support router-based swaps — every unprivileged user can bypass the swap allowlist entirely by routing through the router.

### Finding Description
`SwapAllowlistExtension.beforeSwap` checks `allowedSwapper[msg.sender][sender]`, where `msg.sender` is the pool (the extension's caller) and `sender` is the first argument forwarded from the pool: [1](#0-0) 

That `sender` argument originates in `MetricOmmPool.swap()`, which passes its own `msg.sender` into `_beforeSwap`: [2](#0-1) 

`_beforeSwap` then ABI-encodes it verbatim as the first argument to the extension hook: [3](#0-2) 

When a user calls `MetricOmmSimpleRouter.exactInputSingle`, the router is `msg.sender` of `pool.swap()`: [4](#0-3) 

So the extension receives `sender = router`, checks `allowedSwapper[pool][router]`, and if the router is allowlisted, the check passes for **every** user who calls through the router — regardless of whether that user is individually allowlisted.

This is the direct structural analog of M-02: just as `MsgValueSimulator` forwarded the `isSystemCall` flag to the destination (letting users call system contracts they should not reach), the router forwards its own identity as `sender` to the extension (letting users bypass the allowlist they should not be able to bypass). The intermediary — `MsgValueSimulator` there, `MetricOmmSimpleRouter` here — acts as an unintended privilege escalation path.

For a pool with `SwapAllowlistExtension` to support router-based swaps at all, the pool admin **must** allowlist the router. But once the router is allowlisted, the allowlist is effectively open to the public.

### Impact Explanation
Any user can bypass the swap allowlist on a restricted pool by routing through `MetricOmmSimpleRouter`. Pools configured with `SwapAllowlistExtension` for compliance, KYC, or access-control purposes are rendered ineffective the moment the router is allowlisted. This is an admin-boundary break: the pool admin's per-address access control is bypassed by an unprivileged path through a public periphery contract.

### Likelihood Explanation
Medium. The bypass requires the router to be allowlisted, which is the natural configuration for any pool that wants to support router-based swaps. A pool admin who sets up `SwapAllowlistExtension` to restrict individual swappers while also wanting to support the router would naturally allowlist the router, unknowingly opening the bypass to all users. The `generate_scanned_questions.py` research notes explicitly flag this identity-forwarding concern: [5](#0-4) 

### Recommendation
The extension must gate on the end user's address, not the immediate caller of `swap()`. Options:

1. **Pass the end user's address through `extensionData`**: the router encodes `msg.sender` into `extensionData`; the extension decodes and checks it. This requires router cooperation but keeps the extension self-contained.
2. **Separate per-user gating from router allowlisting**: introduce a two-level check — one for the immediate caller (router) and one for the originating user supplied via `extensionData`.
3. **Document the limitation clearly**: if the current behavior is intentional, document that allowlisting the router grants all users swap access, and provide a separate per-user gating mechanism for compliance use cases.

### Proof of Concept
1. Pool admin deploys a pool with `SwapAllowlistExtension` registered in `beforeSwap` order.
2. Pool admin calls `setAllowedToSwap(pool, router, true)` to enable router-based swaps.
3. Pool admin does **not** call `setAllowedToSwap(pool, attacker, true)`.
4. `attacker` calls `MetricOmmSimpleRouter.exactInputSingle(...)` targeting the restricted pool.
5. Router calls `pool.swap(recipient, zeroForOne, amount, priceLimit, "", "")` — `msg.sender = router`.
6. Pool calls `_beforeSwap(router, ...)` → extension receives `sender = router`.
7. Extension evaluates `allowedSwapper[pool][router]` = `true` → no revert.
8. Swap executes successfully; `attacker` trades on a pool they were never individually allowlisted for. [1](#0-0) [6](#0-5)

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

**File:** metric-core/contracts/MetricOmmPool.sol (L258-258)
```text
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
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

**File:** generate_scanned_questions.py (L656-663)
```python
            short="swap allowlist gate",
            file_function="metric-periphery/contracts/extensions/SwapAllowlistExtension.sol::beforeSwap",
            entrypoint="metric-core/contracts/MetricOmmPool.sol::swap and metric-periphery/contracts/MetricOmmSimpleRouter.sol::exact*",
            call_path="public swap -> beforeSwap hook -> allowAll/allowedSwapper lookup keyed by pool and sender",
            values="the exact swapper identity checked by the hook and whether router-mediated swaps preserve that identity",
            control_hint="Because public users may enter through the router, the hook must gate the same actor the pool designers thought they were allowlisting.",
            validation_focus="Test direct swaps and router swaps on allowlisted pools and assert the hook cannot be bypassed by routing through an intermediate public contract.",
        ),
```
