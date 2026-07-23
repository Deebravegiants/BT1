Audit Report

## Title
`SwapAllowlistExtension.beforeSwap` checks the intermediary router address instead of the actual end-user swapper, enabling allowlist bypass — (`metric-periphery/contracts/extensions/SwapAllowlistExtension.sol`)

## Summary
`SwapAllowlistExtension` is documented as gating `swap` by swapper address per pool, but the `sender` it receives and checks is `msg.sender` of `pool.swap` — which is `MetricOmmSimpleRouter` when users route through it, not the actual end user. If the pool admin allowlists the router so legitimate users can access the periphery, any unpermissioned address can bypass the allowlist entirely by calling through the router. If the admin does not allowlist the router, all individually-allowlisted users are blocked from using the router.

## Finding Description
`MetricOmmPool.swap` passes `msg.sender` as the `sender` argument to `_beforeSwap`:

```solidity
// metric-core/contracts/MetricOmmPool.sol:230-240
_beforeSwap(
  msg.sender,   // router address when called via MetricOmmSimpleRouter
  recipient,
  ...
);
```

`ExtensionCalling._beforeSwap` forwards this verbatim to every configured extension via `_callExtensionsInOrder`:

```solidity
// metric-core/contracts/ExtensionCalling.sol:160-176
_callExtensionsInOrder(
  BEFORE_SWAP_ORDER,
  abi.encodeCall(IMetricOmmExtensions.beforeSwap, (sender, recipient, ...))
);
```

`SwapAllowlistExtension.beforeSwap` then checks `allowedSwapper[msg.sender][sender]` where `msg.sender` is the pool and `sender` is the router:

```solidity
// metric-periphery/contracts/extensions/SwapAllowlistExtension.sol:37
if (!allowAllSwappers[msg.sender] && !allowedSwapper[msg.sender][sender]) {
    revert IMetricOmmPoolActions.NotAllowedToSwap();
}
```

`MetricOmmSimpleRouter.exactInputSingle` calls `pool.swap(params.recipient, ...)` directly, making the router `msg.sender` inside `pool.swap`:

```solidity
// metric-periphery/contracts/MetricOmmSimpleRouter.sol:72-80
(int128 amount0Delta, int128 amount1Delta) = IMetricOmmPoolActions(params.pool)
  .swap(params.recipient, params.zeroForOne, ...);
```

The same pattern applies to `exactInput`, `exactOutputSingle`, and `exactOutput`. There is no mechanism in the interface or the router to pass the actual originating user identity to the extension — `extensionData` is caller-supplied and untrusted. Existing guards (`allowedSwapper`, `allowAllSwappers`) operate on the wrong address and cannot be configured to fix this without changing the contract.

## Impact Explanation
**Allowlist bypass (Critical):** A pool admin deploys a pool with `SwapAllowlistExtension` to restrict swaps to KYC'd or permissioned users. They allowlist the router address so legitimate users can use the periphery. Any unpermissioned user can call `router.exactInputSingle({pool: pool, ...})` and swap freely — `allowedSwapper[pool][router] == true` passes the check regardless of who the actual caller is. The entire per-user allowlist is nullified for all router-mediated swaps, breaking the core access-control invariant the extension is designed to enforce and allowing unauthorized fund flows through the pool.

**DoS for legitimate users (Medium):** If the admin does not allowlist the router (only individual users), every allowlisted user who routes through the periphery is blocked with `NotAllowedToSwap`, making the router's slippage protection, multi-hop routing, and deadline enforcement inaccessible — a broken core swap flow.

## Likelihood Explanation
`MetricOmmSimpleRouter` is the primary public-facing swap interface. `SwapAllowlistExtension` is a production periphery contract explicitly designed for per-pool access control. The pool admin has no way to configure the extension to check the actual user when the router is the intermediary — the bug is structural, not a misconfiguration. Any unpermissioned user can trigger Scenario A with a single router call, requiring no special privileges or setup beyond the pool admin having made the natural configuration of allowlisting the router.

## Recommendation
The `beforeSwap` hook receives `sender` (direct pool caller) and `recipient`, neither of which is the actual end user when the router is involved. The correct fix requires the router to encode the real user identity (`msg.sender` at router entry) in `extensionData`, and the extension to decode and verify it against a registry of trusted routers. A minimal mitigation is to document that `SwapAllowlistExtension` gates the direct pool caller only, and require pool admins to never allowlist the router — but this fundamentally changes the security model the extension advertises and makes the periphery unusable for allowlisted users.

## Proof of Concept
1. Deploy a pool with `SwapAllowlistExtension` configured.
2. Pool admin calls `swapExtension.setAllowedToSwap(pool, address(router), true)` — allowlisting the router so legitimate users can use the periphery.
3. Unpermissioned `attacker` (not individually allowlisted) calls `router.exactInputSingle({pool: pool, recipient: attacker, ...})`.
4. Router calls `pool.swap(attacker, ...)` — `msg.sender` inside pool is `router`.
5. `_beforeSwap(router, attacker, ...)` is called; `SwapAllowlistExtension.beforeSwap` receives `sender = router`.
6. `allowedSwapper[pool][router] == true` → check passes; attacker receives output tokens despite never being individually allowlisted.

Foundry test: deploy pool with extension, `setAllowedToSwap(pool, router, true)`, call `router.exactInputSingle` from an address not in `allowedSwapper`, assert swap succeeds and tokens are transferred.