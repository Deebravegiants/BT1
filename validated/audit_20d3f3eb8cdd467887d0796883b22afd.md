Based on my analysis of the codebase, I found a valid analog.

---

### Title
Unvalidated Pool Address in `MetricOmmSimpleRouter` Allows Fake Pool to Drain User-Approved Tokens — (`metric-periphery/contracts/MetricOmmSimpleRouter.sol`)

### Summary

`MetricOmmSimpleRouter` accepts caller-supplied pool addresses in all swap entry points (`exactInputSingle`, `exactInput`, `exactOutputSingle`, `exactOutput`) without verifying that those addresses are pools registered in `MetricOmmPoolFactory`. A malicious actor can supply a fake pool contract that calls back the router's `metricOmmSwapCallback` with inflated deltas, causing the router to transfer the victim's approved tokens to the attacker.

### Finding Description

Every swap entry point in `MetricOmmSimpleRouter` takes a user-supplied `pool` (or `pools[]`) address and immediately calls `swap` on it:

```solidity
// exactInputSingle — no factory check
_setNextCallbackContext(params.pool, CALLBACK_MODE_JUST_PAY, msg.sender, params.tokenIn);
(int128 amount0Delta, int128 amount1Delta) = IMetricOmmPoolActions(params.pool)
    .swap(params.recipient, params.zeroForOne, ...);
``` [1](#0-0) 

The multi-hop path validator `_validatePath` only checks array-length invariants — it is declared `pure` and has no access to the factory, so it cannot and does not verify factory registration:

```solidity
function _validatePath(...) internal pure {
    if (
      tokens.length < 2 || pools.length != tokens.length - 1 || ...
    ) { revert InvalidPath(); }
}
``` [2](#0-1) 

`exactInputSingle` and `exactOutputSingle` do not even call `_validatePath`.

The router's callback guard `_requireExpectedCallbackCaller(msg.sender)` only checks that the caller of `metricOmmSwapCallback` matches the pool address stored in transient storage by `_setNextCallbackContext`. Because the attacker's fake pool **is** the address that was stored, this guard passes unconditionally. [3](#0-2) 

Once the guard passes, `_justPayCallback` executes:

```solidity
function _justPayCallback(int256 amount0Delta, int256 amount1Delta) private {
    pay(
      _getTokenToPay(),
      _getPayer(),          // ← victim (original msg.sender)
      msg.sender,           // ← attacker's fake pool
      uint256(MetricOmmSwapResults.extractPositiveAmount(amount0Delta, amount1Delta))
    );
}
``` [4](#0-3) 

The fake pool controls `amount0Delta`/`amount1Delta`, so it can set the positive delta to any value up to the victim's full token approval, and the router will transfer that amount from the victim to the fake pool.

The factory address is passed to the router's constructor and stored in `MetricOmmSwapRouterBase`, but it is never consulted to validate pool addresses at swap time. [5](#0-4) 

### Impact Explanation

Any user who calls the router with a malicious pool address (e.g., via a compromised frontend) loses all tokens they have approved to the router, up to their full approval amount. This is a direct loss of user principal with no recovery path. The factory registry exists and `isPool` is queryable, but the router never calls it. [6](#0-5) 

### Likelihood Explanation

The Velodrome audit report explicitly identified this attack vector as the primary risk: "a greater risk for users arises from the possibility of calling the router from a frontend that can pass in any arbitrary factory… especially if a website is compromised." The same threat model applies here. A compromised or malicious frontend, a phishing site, or a malicious integrator can supply a fake pool address. No privileged access is required — any EOA can trigger this by calling `exactInputSingle` with a crafted `params.pool`.

### Recommendation

In `MetricOmmSimpleRouter`, validate every pool address against the factory registry before calling `swap` on it. The factory is already stored in `MetricOmmSwapRouterBase`; add a check such as:

```solidity
require(IMetricOmmPoolFactory(factory).isPool(pool), "UnregisteredPool()");
```

Apply this check in `exactInputSingle`, `exactOutputSingle`, and inside `_validatePath` (converting it from `pure` to `view`) for `exactInput` and `exactOutput`. Also apply it inside `_exactOutputIterateCallback` when recursively selecting the next pool from `cb.pools[tradesLeft]`. [7](#0-6) 

### Proof of Concept

1. Attacker deploys `FakePool` implementing `IMetricOmmPoolActions.swap`:
   - When `swap` is called, it immediately calls `router.metricOmmSwapCallback(1e18, 0, "")` (or any large positive delta for token0).
2. Victim approves `router` for 1000 USDC (`tokenIn = USDC`).
3. Attacker (or compromised frontend) calls:
   ```solidity
   router.exactInputSingle(ExactInputSingleParams({
       pool: address(fakePool),
       tokenIn: USDC,
       zeroForOne: true,
       amountIn: 1,
       recipient: attacker,
       priceLimitX64: 0,
       amountOutMinimum: 0,
       ...
   }));
   ```
4. Router calls `_setNextCallbackContext(fakePool, CALLBACK_MODE_JUST_PAY, victim, USDC)`.
5. Router calls `fakePool.swap(...)`.
6. `FakePool.swap` calls `router.metricOmmSwapCallback(1e18, 0, "")`.
7. `_requireExpectedCallbackCaller(fakePool)` passes — fakePool is the expected caller.
8. `_justPayCallback` calls `pay(USDC, victim, fakePool, 1e18)`.
9. Router transfers 1e18 USDC from victim to attacker's fake pool. [8](#0-7)

### Citations

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L24-24)
```text
  constructor(address weth, address factory) MetricOmmSwapRouterBase(factory) PeripheryPayments(weth) {}
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L46-62)
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

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L99-112)
```text
    for (uint256 i = 0; i <= last; i++) {
      address pool = params.pools[i];
      bool zeroForOne = MetricOmmSwapPath.resolveZeroForOneBitmap(params.zeroForOneBitMap, i);

      _setNextCallbackContext(pool, CALLBACK_MODE_JUST_PAY, i == 0 ? msg.sender : address(this), params.tokens[i]);
      (int128 amount0Delta, int128 amount1Delta) = IMetricOmmPoolActions(pool)
        .swap(
          i == last ? params.recipient : address(this),
          zeroForOne,
          amount,
          MetricOmmSwapPath.openLimit(zeroForOne),
          "",
          params.extensionDatas[i]
        );
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L192-199)
```text
  function _justPayCallback(int256 amount0Delta, int256 amount1Delta) private {
    pay(
      _getTokenToPay(),
      _getPayer(),
      msg.sender,
      uint256(MetricOmmSwapResults.extractPositiveAmount(amount0Delta, amount1Delta))
    );
  }
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L235-245)
```text
  function _validatePath(address[] calldata tokens, address[] calldata pools, bytes[] calldata extensionDatas)
    internal
    pure
  {
    if (
      tokens.length < 2 || pools.length != tokens.length - 1 || extensionDatas.length != pools.length
        || pools.length > MAX_PATH_POOLS
    ) {
      revert InvalidPath();
    }
  }
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L149-151)
```text
  function isPool(address pool) external view override returns (bool) {
    return poolToIdx[pool] != 0;
  }
```
