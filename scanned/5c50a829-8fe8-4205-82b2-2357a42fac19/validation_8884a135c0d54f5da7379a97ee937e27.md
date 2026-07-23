### Title
`SwapAllowlistExtension.beforeSwap` validates the intermediary router address instead of the actual end-user swapper, enabling allowlist bypass via `MetricOmmSimpleRouter` — (`metric-periphery/contracts/extensions/SwapAllowlistExtension.sol`)

---

### Summary

`SwapAllowlistExtension` is designed to gate `pool.swap` by individual swapper identity. However, the `sender` argument it receives and checks is `msg.sender` of the pool's `swap` call — which is the `MetricOmmSimpleRouter` contract address when users route through it, not the actual end user. This is the direct structural analog of the external `investorExists` bug: a guard validates the intermediary caller instead of the economically relevant actor passed as a parameter.

---

### Finding Description

`MetricOmmPool.swap` passes `msg.sender` as the `sender` argument to `_beforeSwap`:

```solidity
// metric-core/contracts/MetricOmmPool.sol:230-240
_beforeSwap(
  msg.sender,   // <-- whoever called pool.swap (router or direct user)
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

`ExtensionCalling._beforeSwap` forwards this verbatim to every configured extension:

```solidity
// metric-core/contracts/ExtensionCalling.sol:95-98
_callExtensionsInOrder(
  BEFORE_SWAP_ORDER,
  abi.encodeCall(IMetricOmmExtensions.beforeSwap, (sender, owner, salt, deltas, extensionData))
);
```

`SwapAllowlistExtension.beforeSwap` then checks `allowedSwapper[pool][sender]`:

```solidity
// metric-periphery/contracts/extensions/SwapAllowlistExtension.sol:31-41
function beforeSwap(address sender, address, bool, int128, uint128, uint256, uint128, uint128, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllSwappers[msg.sender] && !allowedSwapper[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToSwap();
    }
    return IMetricOmmExtensions.beforeSwap.selector;
}
```

When a user calls `MetricOmmSimpleRouter.exactInputSingle` (or any `exact*` variant), the router calls `pool.swap(params.recipient, ...)` directly:

```solidity
// metric-periphery/contracts/MetricOmmSimpleRouter.sol:72-80
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

So `msg.sender` inside `pool.swap` is the **router address**, not the actual user. The `sender` forwarded to `beforeSwap` is therefore the router, and `allowedSwapper[pool][router]` is what gets evaluated — not `allowedSwapper[pool][actual_user]`.

---

### Impact Explanation

Two concrete broken invariants result:

**Scenario A — Allowlist bypass (Critical):** A pool admin deploys a pool with `SwapAllowlistExtension` to restrict swaps to KYC'd or permissioned users. They allowlist the router (or set `allowAllSwappers = true` for the router) so that legitimate users can use the periphery. Any unpermissioned user can now call `MetricOmmSimpleRouter.exactInputSingle` and swap freely, because the check passes on the router address. The entire allowlist is nullified for router-mediated swaps.

**Scenario B — Denial of service for legitimate users (Medium):** If the pool admin does NOT allowlist the router (only individual user addresses), then every allowlisted user who attempts to swap through the router is blocked with `NotAllowedToSwap`. They must call `pool.swap` directly, losing access to slippage protection, multi-hop routing, and deadline enforcement provided by the periphery.

Both outcomes break the core invariant that `SwapAllowlistExtension` gates the economically relevant swapper.

---

### Likelihood Explanation

- `MetricOmmSimpleRouter` is the primary public-facing swap interface; most users are expected to route through it.
- `SwapAllowlistExtension` is a production periphery contract explicitly designed for per-pool access control.
- The pool admin has no way to configure the extension to check the actual user when the router is the intermediary — the bug is structural, not a misconfiguration.
- The `generate_scanned_questions.py` audit playbook explicitly flags this exact path: *"Because public users may enter through the router, the hook must gate the same actor the pool designers thought they were allowlisting."*

---

### Recommendation

The `beforeSwap` hook receives both `sender` (the direct pool caller) and `recipient`. Neither is the actual end user when the router is involved. The fix requires the router to encode the real user identity in `extensionData` and the extension to decode it, **or** the pool interface must be extended to carry a `payer`/`originator` field distinct from `msg.sender`.

A minimal mitigation: document that `SwapAllowlistExtension` gates the direct pool caller (router address), and require pool admins to allowlist the router only when all users of that router are permitted — effectively making the allowlist router-granular rather than user-granular. However, this fundamentally changes the security model the extension advertises.

The correct fix mirrors the external report's recommendation: replace the `sender` check with a check on the actual originating user, passed explicitly through `extensionData` by a trusted router, and verified against a known-router registry.

---

### Proof of Concept

1. Deploy a pool with `SwapAllowlistExtension` configured.
2. Pool admin calls `swapExtension.setAllowedToSwap(pool, address(router), true)` — allowlisting the router so legitimate users can use it.
3. Unpermissioned user `attacker` calls `router.exactInputSingle({pool: pool, recipient: attacker, ...})`.
4. Router calls `pool.swap(attacker, ...)` — `msg.sender` inside pool is `router`.
5. `beforeSwap` receives `sender = router`; `allowedSwapper[pool][router] == true` → check passes.
6. Attacker receives output tokens despite never being individually allowlisted.

Relevant code locations: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** metric-core/contracts/MetricOmmPool.sol (L230-241)
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

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L67-86)
```text
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
