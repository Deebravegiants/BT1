### Title
`SwapAllowlistExtension` receives the router address as `sender` instead of the actual end-user, allowing any user to bypass per-user swap access control via `MetricOmmSimpleRouter` — (`metric-periphery/contracts/extensions/SwapAllowlistExtension.sol`)

---

### Summary

`MetricOmmPool.swap()` always passes `msg.sender` as the `sender` argument to `beforeSwap` / `afterSwap` extension hooks. When a user routes through `MetricOmmSimpleRouter`, `msg.sender` at the pool is the **router contract**, not the actual end-user. `SwapAllowlistExtension.beforeSwap()` checks `allowedSwapper[pool][sender]`, so it evaluates the router's allowlist status, not the individual user's. If the router is allowlisted, every user on-chain can bypass per-user swap restrictions on any pool that uses this extension.

---

### Finding Description

**Root cause — `MetricOmmPool.swap()` always uses `msg.sender` as `sender`:** [1](#0-0) 

`msg.sender` is the direct pool caller. When the user goes through `MetricOmmSimpleRouter.exactInputSingle()` / `exactInput()` / `exactOutputSingle()` / `exactOutput()`, the direct caller is the router, so `sender = address(router)`.

**`SwapAllowlistExtension.beforeSwap()` checks `sender` (= router), not the actual user:** [2](#0-1) 

The check `allowedSwapper[msg.sender][sender]` resolves to `allowedSwapper[pool][router]`. If the router is allowlisted, the gate passes for **every** user who calls through it, regardless of whether that individual user is on the allowlist.

**Router sets `msg.sender` as the payer/sender context, not the end-user:** [3](#0-2) 

The router stores `msg.sender` (the actual user) only in the transient callback context for payment purposes. The pool never receives the actual user's address as `sender`.

**`IMetricOmmExtensions.beforeSwap` signature — `sender` is the only identity field:** [4](#0-3) 

There is no separate `originator` or `payer` field in the hook signature. Extensions have no on-chain way to recover the actual end-user when the direct caller is a router.

---

### Impact Explanation

A pool configured with `SwapAllowlistExtension` and `allowAllSwappers = false` is intended to restrict swaps to a curated set of addresses (e.g., specific market-maker contracts, KYC'd addresses, or protocol-owned bots). If the pool admin allowlists `MetricOmmSimpleRouter` — a natural step to let users interact via the standard UI — every address on-chain can bypass the per-user restriction by calling through the router. Consequences:

- **Unauthorized toxic flow**: Arbitrageurs excluded from the allowlist can now drain LP value through the router.
- **Access-control invariant broken**: The pool's stated restriction (`allowedSwapper`) no longer reflects who can actually swap.
- **LP principal at risk**: LPs who deposited under the assumption that only trusted counterparties could trade against them face unexpected losses.

---

### Likelihood Explanation

- `SwapAllowlistExtension` is a first-party periphery contract explicitly documented and deployed alongside the protocol.
- Pool admins routinely allowlist the canonical router to enable normal user access; the documentation does not warn that doing so grants unrestricted access to all users.
- Any user who discovers the bypass can exploit it permissionlessly with a single `exactInputSingle` call.

---

### Recommendation

1. **Pass the actual payer through the hook**: Add an `originator` field to `beforeSwap` / `afterSwap` that the router populates via `callbackData` or a separate transient slot, and have the pool forward it to extensions.
2. **Alternatively, document the limitation clearly**: State that `sender` is always the direct pool caller and that `SwapAllowlistExtension` gates by contract, not by end-user. Warn admins that allowlisting the router grants access to all router users.
3. **Short-term mitigation**: Pool admins should not allowlist `MetricOmmSimpleRouter` on restricted pools; instead, require users to call the pool directly or deploy a purpose-built allowlisted wrapper.

---

### Proof of Concept

```
Setup:
  pool = MetricOmmPool with SwapAllowlistExtension, allowAllSwappers = false
  allowedSwapper[pool][router] = true   ← admin allowlists the router
  allowedSwapper[pool][alice]  = false  ← alice is NOT individually allowed
  allowedSwapper[pool][bob]    = true   ← bob is individually allowed

Attack:
  alice calls router.exactInputSingle({pool: pool, ...})
    → pool.swap(recipient, ...) with msg.sender = router
    → beforeSwap(sender=router, ...)
    → SwapAllowlistExtension checks allowedSwapper[pool][router] == true → PASSES
    → alice's swap executes against the restricted pool

Result:
  alice, an address the pool admin explicitly excluded, successfully swaps.
  The allowlist invariant is broken; LP funds are exposed to unauthorized flow.
``` [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

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

**File:** metric-core/contracts/interfaces/extensions/IMetricOmmExtensions.sol (L50-60)
```text
  function beforeSwap(
    address sender,
    address recipient,
    bool zeroForOne,
    int128 amountSpecified,
    uint128 priceLimitX64,
    uint256 packedSlot0Initial,
    uint128 bidPriceX64,
    uint128 askPriceX64,
    bytes calldata extensionData
  ) external returns (bytes4);
```
