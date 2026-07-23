### Title
`_validatePath` Omits Pool-Token Connectivity Check, Allowing Multihop Swaps to Deliver Wrong Output Token — (`metric-periphery/contracts/MetricOmmSimpleRouter.sol`)

---

### Summary

`MetricOmmSimpleRouter._validatePath` only checks array-length consistency. It never verifies that consecutive pools in a multihop path are actually connected (i.e., that the output token of `pools[i]` matches the input token of `pools[i+1]`). A utility function `MetricOmmSwapPath.poolsAreConnected` exists for exactly this purpose but is never called by the router. As a result, a caller can supply a path where `tokens[last]` does not match the actual output token of `pools[last]`, causing the recipient to receive a different (potentially worthless) token while the `amountOutMinimum` guard passes silently.

---

### Finding Description

`_validatePath` in `MetricOmmSimpleRouter` enforces only structural constraints:

```solidity
// metric-periphery/contracts/MetricOmmSimpleRouter.sol:235-245
function _validatePath(address[] calldata tokens, address[] calldata pools, bytes[] calldata extensionDatas)
    internal pure
{
    if (
        tokens.length < 2 || pools.length != tokens.length - 1 || extensionDatas.length != pools.length
            || pools.length > MAX_PATH_POOLS
    ) {
        revert InvalidPath();
    }
}
``` [1](#0-0) 

It does not call `MetricOmmSwapPath.poolsAreConnected`, which performs the missing check:

```solidity
// metric-periphery/contracts/libraries/MetricOmmSwapPath.sol:43-53
function poolsAreConnected(address[] calldata pools, uint256 zeroForOneBitMap) internal view returns (bool) {
    uint256 last = pools.length - 1;
    for (uint256 i = 0; i < last; i++) {
        bool zeroForOne = resolveZeroForOneBitmap(zeroForOneBitMap, i);
        bool nextZeroForOne = resolveZeroForOneBitmap(zeroForOneBitMap, i + 1);
        if (hopOutputToken(pools[i], zeroForOne) != hopInputToken(pools[i + 1], nextZeroForOne)) {
            return false;
        }
    }
    return true;
}
``` [2](#0-1) 

`poolsAreConnected` is only used in `MetricOmmSwapQuoter.sol` (off-chain simulation), never in the live router.

In `exactInput`, for each hop `i`, the router stores `params.tokens[i]` as the payment token and `address(this)` as the payer for intermediate hops:

```solidity
// metric-periphery/contracts/MetricOmmSimpleRouter.sol:103
_setNextCallbackContext(pool, CALLBACK_MODE_JUST_PAY, i == 0 ? msg.sender : address(this), params.tokens[i]);
``` [3](#0-2) 

The pool's balance check enforces that the correct token is paid (so wrong-token payment reverts). However, the **output** token of `pools[i]` is never verified against `tokens[i+1]`. The final output amount check only validates quantity:

```solidity
// metric-periphery/contracts/MetricOmmSimpleRouter.sol:121-122
amountOut = MetricOmmSwapInputs.int128ToUint128(amount);
if (amountOut < params.amountOutMinimum) revert InsufficientOutput(amountOut, params.amountOutMinimum);
``` [4](#0-3) 

The interface explicitly acknowledges this gap: *"Path token connectivity and single-hop tokenIn / tokenOut against pool immutables remain the caller's obligation off-chain."* [5](#0-4) 

---

### Impact Explanation

A caller (or a buggy/malicious integrator constructing paths on behalf of users) can supply a path where `pools[last]` outputs a token different from `tokens[last]`. The recipient receives the wrong token; the `amountOutMinimum` guard passes if the raw amount is sufficient. If the actual output token is worth less than the expected `tokens[last]`, the user suffers a direct loss of principal with no on-chain revert.

Concrete example:
- `tokens = [WETH, USDC, DAI]`, `pools = [Pool_WETH_USDC, Pool_USDC_WETH]`, `zeroForOneBitMap = 0b11`
- Hop 0: WETH → USDC via `Pool_WETH_USDC` (correct). Router holds USDC.
- Hop 1: Router pays USDC to `Pool_USDC_WETH` (pool balance check passes). Pool sends WETH to recipient.
- Recipient receives WETH, not DAI. `amountOutMinimum` passes if WETH amount ≥ minimum.
- User paid WETH and received WETH back minus fees — a total loss of spread and notional fees with no DAI delivered.

---

### Likelihood Explanation

Any caller of `exactInput` or `exactOutput` with a multihop path can trigger this. No special privilege is required. Realistic triggers include: aggregator routing bugs, front-end manipulation, or deliberate path construction. The protocol's own `poolsAreConnected` utility confirms the developers anticipated this check but omitted it from the live execution path.

---

### Recommendation

Call `MetricOmmSwapPath.poolsAreConnected` inside `_validatePath` (or inline the check) and revert with `InvalidPath` if it returns `false`:

```solidity
function _validatePath(address[] calldata tokens, address[] calldata pools, bytes[] calldata extensionDatas)
    internal view  // view, not pure — poolsAreConnected reads pool immutables
{
    if (
        tokens.length < 2 || pools.length != tokens.length - 1 || extensionDatas.length != pools.length
            || pools.length > MAX_PATH_POOLS
    ) {
        revert InvalidPath();
    }
    // NEW: verify consecutive pools are connected
    if (!MetricOmmSwapPath.poolsAreConnected(pools, /* zeroForOneBitMap must be threaded in */)) {
        revert InvalidPath();
    }
}
```

`zeroForOneBitMap` must be threaded into `_validatePath` since `poolsAreConnected` requires it to resolve direction per hop. Additionally, verify that `tokens[0]` matches `hopInputToken(pools[0], zeroForOne_0)` and `tokens[last]` matches `hopOutputToken(pools[last], zeroForOne_last)`.

---

### Proof of Concept

```solidity
// Attacker constructs a two-hop exactInput path where pools[1] is disconnected.
// Pool A: WETH/USDC  (token0=WETH, token1=USDC)
// Pool C: USDC/WETH  (token0=USDC, token1=WETH)  ← not USDC/DAI

address[] memory tokens = new address[](3);
tokens[0] = address(weth);
tokens[1] = address(usdc);
tokens[2] = address(dai);   // ← claimed output, never enforced

address[] memory pools = new address[](2);
pools[0] = address(poolA);  // WETH/USDC — correct
pools[1] = address(poolC);  // USDC/WETH — WRONG, should be USDC/DAI

bytes[] memory extensionDatas = new bytes[](2);

// zeroForOneBitMap = 0b11: both hops are zeroForOne
// Hop 0: WETH→USDC (correct), Hop 1: USDC→WETH (wrong direction/pool)
uint256 amountOut = router.exactInput(
    IMetricOmmSimpleRouter.ExactInputParams({
        tokens: tokens,
        pools: pools,
        extensionDatas: extensionDatas,
        zeroForOneBitMap: 3,
        amountIn: 1_000,
        amountOutMinimum: 0,   // ← no token-type protection
        recipient: recipient,
        deadline: block.timestamp + 1
    })
);
// recipient receives WETH, not DAI; _validatePath did not revert
``` [6](#0-5) [2](#0-1)

### Citations

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L92-125)
```text
  function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut) {
    _checkDeadline(params.deadline);
    _validatePath(params.tokens, params.pools, params.extensionDatas);

    uint256 last = params.pools.length - 1;
    int128 amount = MetricOmmSwapInputs.asAmountSpecifiedIn(params.amountIn);

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

      int128 amountInActual = MetricOmmSwapResults.extractAmountIn(zeroForOne, amount0Delta, amount1Delta);
      if (amountInActual < amount) revert InvalidInputAmountAtHop(uint8(i), amountInActual, amount);

      amount = MetricOmmSwapResults.extractAmountOut(zeroForOne, amount0Delta, amount1Delta);
    }

    if (amount <= 0) revert InvalidSwapDeltas();
    amountOut = MetricOmmSwapInputs.int128ToUint128(amount);
    if (amountOut < params.amountOutMinimum) revert InsufficientOutput(amountOut, params.amountOutMinimum);

    _clearExpectedCallbackPool();
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

**File:** metric-periphery/contracts/libraries/MetricOmmSwapPath.sol (L43-53)
```text
  function poolsAreConnected(address[] calldata pools, uint256 zeroForOneBitMap) internal view returns (bool) {
    uint256 last = pools.length - 1;
    for (uint256 i = 0; i < last; i++) {
      bool zeroForOne = resolveZeroForOneBitmap(zeroForOneBitMap, i);
      bool nextZeroForOne = resolveZeroForOneBitmap(zeroForOneBitMap, i + 1);
      if (hopOutputToken(pools[i], zeroForOne) != hopInputToken(pools[i + 1], nextZeroForOne)) {
        return false;
      }
    }
    return true;
  }
```

**File:** metric-periphery/contracts/interfaces/IMetricOmmSimpleRouter.sol (L12-13)
```text
///      Only pools registered on the configured factory may be used. Path token connectivity and single-hop
///      tokenIn / tokenOut against pool immutables remain the caller's obligation off-chain.
```
