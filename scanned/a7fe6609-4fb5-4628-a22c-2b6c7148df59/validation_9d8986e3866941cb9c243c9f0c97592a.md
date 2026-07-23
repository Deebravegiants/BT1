### Title
`SwapAllowlistExtension.beforeSwap()` only checks `sender`, not `recipient` — allowlisted swapper can route output tokens to any non-allowlisted address - (File: metric-periphery/contracts/extensions/SwapAllowlistExtension.sol)

### Summary

`SwapAllowlistExtension` is the production extension that gates pool swaps by address. Its `beforeSwap` hook receives both `sender` (the swap initiator) and `recipient` (the address that receives output tokens), but silently ignores `recipient`. An allowlisted swapper can call `swap()` with any arbitrary `recipient`, and the allowlist check passes while real ERC-20 output tokens are transferred to the non-allowlisted address.

### Finding Description

`MetricOmmPool.swap()` accepts a caller-controlled `recipient` parameter and passes it to `_beforeSwap()` alongside `msg.sender`: [1](#0-0) 

The pool then unconditionally transfers output tokens to `recipient` after the extension check: [2](#0-1) 

`SwapAllowlistExtension.beforeSwap()` receives `recipient` as its second parameter but leaves it unnamed and never reads it. Only `sender` is verified: [3](#0-2) 

The `IMetricOmmExtensions` interface confirms `recipient` is available to the hook: [4](#0-3) 

Contrast this with `DepositAllowlistExtension.beforeAddLiquidity()`, which correctly ignores `sender` and checks `owner` (the address that actually holds the position): [5](#0-4) 

The asymmetry is the bug: the deposit extension checks the address that holds the economic position; the swap extension does not check the address that receives the economic output.

### Impact Explanation

Any pool that deploys `SwapAllowlistExtension` for KYC/compliance gating has its access control bypassed for the output leg. An allowlisted swapper calls `pool.swap(nonAllowlistedRecipient, ...)` — the `beforeSwap` check passes (only `sender` is verified), and the pool transfers real ERC-20 output tokens to `nonAllowlistedRecipient`. The non-allowlisted address receives actual token balances without ever being approved. This is a direct loss of the access-control invariant the extension is designed to enforce, and it moves real token balances to addresses the pool admin explicitly did not authorize.

The `MetricOmmSimpleRouter` amplifies the issue: the router is `msg.sender` of `swap()`, so if the router is allowlisted as a swapper, any end-user can call `router.exactInputSingle(...)` with any `recipient` and the allowlist check passes unconditionally: [6](#0-5) 

### Likelihood Explanation

Any pool that configures `SwapAllowlistExtension` is affected. The trigger requires only a single allowlisted address (including the router if it is allowlisted) to call `swap()` with a non-allowlisted `recipient`. No privileged cooperation is needed beyond holding an existing allowlist entry. The `recipient` parameter is fully caller-controlled with no on-chain validation.

### Recommendation

Add a `recipient` check inside `beforeSwap`, mirroring how `beforeAddLiquidity` checks `owner`:

```solidity
function beforeSwap(address sender, address recipient, bool, int128, uint128, uint256, uint128, uint128, bytes calldata)
    external
    view
    override
    returns (bytes4)
{
    if (!allowAllSwappers[msg.sender] && !allowedSwapper[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToSwap();
    }
    if (!allowAllSwappers[msg.sender] && !allowedSwapper[msg.sender][recipient]) {
        revert IMetricOmmPoolActions.NotAllowedToSwap();
    }
    return IMetricOmmExtensions.beforeSwap.selector;
}
```

Alternatively, document explicitly that `recipient` is intentionally unchecked and that pool admins must not rely on `SwapAllowlistExtension` to restrict who can receive output tokens.

### Proof of Concept

1. Pool is deployed with `SwapAllowlistExtension` attached.
2. Pool admin calls `setAllowedToSwap(pool, alice, true)` — Alice is allowlisted; Bob is not.
3. Alice calls `pool.swap(bob, zeroForOne, amountSpecified, priceLimitX64, callbackData, extensionData)`.
4. `_beforeSwap(alice, bob, ...)` is called → `SwapAllowlistExtension.beforeSwap(alice, bob, ...)`.
5. The check `allowedSwapper[pool][alice]` is `true` → no revert.
6. Pool executes the swap and calls `transferToken1(bob, outputAmount)`.
7. Bob (non-allowlisted) receives real ERC-20 output tokens.

The `recipient` check that would have caught this — `allowedSwapper[pool][bob]` — is never evaluated. [3](#0-2) [7](#0-6)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L217-240)
```text
  function swap(
    address recipient,
    bool zeroForOne,
    int128 amountSpecified,
    uint128 priceLimitX64,
    bytes calldata callbackData,
    bytes calldata extensionData
  ) external whenNotPaused nonReentrant(PoolActions.SWAP) returns (int128, int128) {
    require(amountSpecified != 0, InvalidAmount());

    uint256 packedSlot0Initial = Slot0Library.loadPackedSlot0();
    (uint128 bidPriceX64, uint128 askPriceX64) = _getBidAndAskPriceX64();

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

**File:** metric-core/contracts/MetricOmmPool.sol (L250-278)
```text
    if (zeroForOne) {
      if (amount1Delta < 0) {
        // casting to uint256 is safe because amount1Delta is negative and the ammount of tokens in pool is capped by uint128.max
        // forge-lint: disable-next-line(unsafe-typecast)
        transferToken1(recipient, uint256(-amount1Delta));
      }

      uint256 balance0Before = balance0();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
      // casting to uint256 is safe because amount0Delta is positive and the ammount of tokens in pool is capped by uint128.max
      // forge-lint: disable-next-line(unsafe-typecast)
      if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
        revert IncorrectDelta();
      }
    } else {
      if (amount0Delta < 0) {
        // casting to uint256 is safe because amount0Delta is negative and the ammount of tokens in pool is capped by uint128.max
        // forge-lint: disable-next-line(unsafe-typecast)
        transferToken0(recipient, uint256(-amount0Delta));
      }

      uint256 balance1Before = balance1();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
      // casting to uint256 is safe because amount1Delta is positive and the ammount of tokens in pool is capped by uint128.max
      // forge-lint: disable-next-line(unsafe-typecast)
      if (amount1Delta > 0 && balance1Before + uint256(amount1Delta) > balance1()) {
        revert IncorrectDelta();
      }
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
