### Title
`SwapAllowlistExtension` checks the router's address instead of the end user's, allowing any user to bypass the per-user swap allowlist via `MetricOmmSimpleRouter` — (`metric-periphery/contracts/extensions/SwapAllowlistExtension.sol`)

---

### Summary

`SwapAllowlistExtension.beforeSwap` gates swaps by checking `sender`, which is `msg.sender` of the pool's `swap` call. When a user routes through `MetricOmmSimpleRouter`, `sender` becomes the router contract address, not the actual end user. A pool admin who allowlists the router (required for any router-mediated swap to succeed) inadvertently grants every user unrestricted swap access, defeating the purpose of the per-user allowlist entirely.

---

### Finding Description

The pool's `swap` function passes `msg.sender` as the `sender` argument to `_beforeSwap`: [1](#0-0) 

`ExtensionCalling._beforeSwap` forwards that value verbatim to every configured extension: [2](#0-1) 

`SwapAllowlistExtension.beforeSwap` then checks `allowedSwapper[pool][sender]`: [3](#0-2) 

When a user calls `MetricOmmSimpleRouter.exactInputSingle`, the router calls `pool.swap(...)` directly, so `msg.sender` seen by the pool — and therefore `sender` seen by the extension — is the **router contract**, not the end user: [4](#0-3) 

The same substitution occurs for `exactInput`, `exactOutputSingle`, and `exactOutput`. In every case the pool sees `msg.sender = router`.

The pool admin faces an impossible choice:

| Admin action | Effect |
|---|---|
| Do **not** allowlist the router | All router-mediated swaps revert for every user, including allowed ones |
| Allowlist the router | Every user on the network can bypass the per-user restriction by routing through the router |

There is no configuration that allows specific users to swap via the router while blocking others.

This is the direct analog of the ERC-1404 M-08 bug: the restriction checks only one identity (the immediate caller) while the economically relevant actor (the end user) is never validated.

---

### Impact Explanation

A pool configured with `SwapAllowlistExtension` to restrict swaps to a curated set of addresses (e.g., KYC'd counterparties, whitelisted market makers) can be bypassed by any unprivileged user simply by calling `MetricOmmSimpleRouter` instead of the pool directly. The allowlist gate is rendered completely ineffective for all router-mediated swap paths. Real token balances move: the bypassing user receives output tokens from the pool and the pool receives input tokens, constituting an unauthorized swap against a pool whose admin intended to restrict access.

---

### Likelihood Explanation

`MetricOmmSimpleRouter` is a public, permissionless contract. Any user who discovers the bypass can exploit it immediately without any privileged access. The only precondition is that the pool has `SwapAllowlistExtension` configured and the router is allowlisted (which is necessary for any legitimate router user to swap). The bypass requires no special tokens, no flash loans, and no admin cooperation.

---

### Recommendation

The extension must validate the **end user** identity, not the immediate caller. Two complementary approaches:

1. **Pass the original initiator through the router.** Modify `MetricOmmSimpleRouter` to encode `msg.sender` (the actual user) into `extensionData` and have `SwapAllowlistExtension.beforeSwap` decode and check that value when `sender` is a known router.

2. **Check both `sender` and a user field in extension data.** Extend the `beforeSwap` interface so the router always forwards the originating user address, and the extension checks that address against the allowlist instead of (or in addition to) `sender`.

Either way, the extension must be able to distinguish "router acting on behalf of an allowed user" from "router acting on behalf of a blocked user."

---

### Proof of Concept

```solidity
// Setup: pool with SwapAllowlistExtension; only `allowedUser` is on the allowlist.
// The router must be allowlisted for any router swap to work.
swapExtension.setAllowedToSwap(address(pool), address(router), true);
// allowedUser is also allowlisted (direct swaps work for them).
swapExtension.setAllowedToSwap(address(pool), allowedUser, true);
// blockedUser is NOT on the allowlist.

// Direct swap by blockedUser → correctly reverts NotAllowedToSwap
vm.prank(blockedUser);
vm.expectRevert(IMetricOmmPoolActions.NotAllowedToSwap.selector);
pool.swap(blockedUser, true, 1000, 0, "", "");

// Router-mediated swap by blockedUser → succeeds, bypassing the allowlist
vm.prank(blockedUser);
token0.approve(address(router), type(uint256).max);
uint256 amountOut = router.exactInputSingle(
    IMetricOmmSimpleRouter.ExactInputSingleParams({
        pool: address(pool),
        tokenIn: address(token0),
        tokenOut: address(token1),
        zeroForOne: true,
        amountIn: 1000,
        amountOutMinimum: 0,
        recipient: blockedUser,
        deadline: block.timestamp + 1,
        priceLimitX64: 0,
        extensionData: ""
    })
);
// blockedUser receives token1 despite not being on the allowlist.
assertGt(amountOut, 0);
```

The pool's `swap` call originates from the router (`msg.sender = router`), so `sender = router` is passed to `beforeSwap`. Since the router is allowlisted, the check passes and `blockedUser` receives output tokens. [5](#0-4) [6](#0-5) [1](#0-0)

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
