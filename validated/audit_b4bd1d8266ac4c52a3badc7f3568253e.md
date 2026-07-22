### Title
Mistakenly Sent ETH Is Silently Ignored and Griefable When Swapping or Adding Liquidity With Non-WETH ERC20 Tokens - (`metric-periphery/contracts/base/PeripheryPayments.sol`)

---

### Summary

`PeripheryPayments.pay()` branches on `token == WETH` to consume native ETH from the contract's balance. When `token` is any other ERC20, the native balance is never touched. Because every external entry point on `MetricOmmSimpleRouter` and `MetricOmmPoolLiquidityAdder` is `payable`, a caller who mistakenly attaches `msg.value` while swapping or adding liquidity with a non-WETH ERC20 pair leaves that ETH stranded in the router. Any third party can then drain it by calling the public `refundETH()`.

---

### Finding Description

`PeripheryPayments.pay()` handles three cases:

```solidity
// metric-periphery/contracts/base/PeripheryPayments.sol  lines 69-88
function pay(address token, address payer, address recipient, uint256 value) internal {
    if (payer == address(this)) {
        IERC20(token).safeTransfer(recipient, value);
    } else if (token == WETH) {               // ← only branch that consumes ETH
        uint256 nativeBalance = address(this).balance;
        if (nativeBalance >= value) { ... }
        else if (nativeBalance > 0) { ... }
        else { IERC20(WETH).safeTransferFrom(payer, recipient, value); }
    } else {                                  // ← non-WETH ERC20: ETH silently ignored
        IERC20(token).safeTransferFrom(payer, recipient, value);
    }
}
```

Native ETH is consumed **only** when `token == WETH`. For every other ERC20 the function falls through to `safeTransferFrom` and `address(this).balance` is never touched.

All external entry points that ultimately call `pay()` are declared `payable`:

- `MetricOmmSimpleRouter`: `exactInputSingle`, `exactInput`, `exactOutputSingle`, `exactOutput`, `multicall`
- `MetricOmmPoolLiquidityAdder`: `addLiquidityExactShares` (both overloads), `addLiquidityWeighted` (both overloads), `multicall`

A user who calls, e.g., `exactInputSingle{value: 1 ether}(...)` with `tokenIn = USDC` completes the swap (USDC is pulled via `safeTransferFrom`) while 1 ETH remains in the router. The `refundETH()` helper is `external` and sends the full ETH balance to `msg.sender`:

```solidity
// metric-periphery/contracts/base/PeripheryPayments.sol  lines 58-63
function refundETH() external payable override {
    uint256 balance = address(this).balance;
    if (balance > 0) {
        _transferETH(msg.sender, balance);   // ← sends to caller, not original depositor
    }
}
```

Any address that calls `refundETH()` before the victim does receives the stranded ETH.

---

### Impact Explanation

A user who attaches ETH to a non-WETH ERC20 swap or liquidity call loses that ETH to the first caller of `refundETH()`. The loss is proportional to `msg.value` and is immediate; no privileged role is required to trigger it. This constitutes a direct loss of user principal.

---

### Likelihood Explanation

The external functions are `payable` by design (to support native-ETH-as-WETH flows). A user or integrating contract that sends ETH alongside a non-WETH ERC20 call — through a frontend bug, a scripting mistake, or a misunderstanding of the WETH wrapping pattern — silently loses funds. The `refundETH()` griefing path requires no special access and can be executed by any MEV bot monitoring the mempool.

---

### Recommendation

In the non-WETH ERC20 branch of `pay()`, revert if the contract holds a non-zero native balance that was not expected:

```solidity
} else {
    if (address(this).balance > 0) revert UnexpectedETH();   // add this guard
    IERC20(token).safeTransferFrom(payer, recipient, value);
}
```

Alternatively, add a `msg.value == 0` guard at the top of each external entry point that does not explicitly support native ETH input (i.e., those whose `tokenIn`/pool tokens are not WETH).

---

### Proof of Concept

1. Pool is `token0 = USDC`, `token1 = DAI` (neither is WETH).
2. Victim calls:
   ```solidity
   router.exactInputSingle{value: 1 ether}(ExactInputSingleParams({
       tokenIn: address(USDC), tokenOut: address(DAI), ...
   }));
   ```
3. Inside the swap callback, `_justPayCallback` calls `pay(USDC, victim, pool, amount)`.
4. `USDC != WETH` → `safeTransferFrom(victim, pool, amount)` executes; 1 ETH stays in `address(router).balance`.
5. Attacker calls `router.refundETH()` → receives 1 ETH.
6. Victim's USDC was spent correctly; their 1 ETH is gone.

The same path applies to `addLiquidityExactShares{value: X}(...)` when both pool tokens are non-WETH ERC20. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** metric-periphery/contracts/base/PeripheryPayments.sol (L58-63)
```text
  function refundETH() external payable override {
    uint256 balance = address(this).balance;
    if (balance > 0) {
      _transferETH(msg.sender, balance);
    }
  }
```

**File:** metric-periphery/contracts/base/PeripheryPayments.sol (L69-88)
```text
  function pay(address token, address payer, address recipient, uint256 value) internal {
    // If the payer is contract it means we are in the middle of a path. In the middle of a path we operate on ERC20 only.
    if (payer == address(this)) {
      IERC20(token).safeTransfer(recipient, value);
    } else if (token == WETH) {
      uint256 nativeBalance = address(this).balance;
      if (nativeBalance >= value) {
        IWETH9(WETH).deposit{value: value}();
        IERC20(WETH).safeTransfer(recipient, value);
      } else if (nativeBalance > 0) {
        IWETH9(WETH).deposit{value: nativeBalance}();
        IERC20(WETH).safeTransfer(recipient, nativeBalance);
        IERC20(WETH).safeTransferFrom(payer, recipient, value - nativeBalance);
      } else {
        IERC20(WETH).safeTransferFrom(payer, recipient, value);
      }
    } else {
      IERC20(token).safeTransferFrom(payer, recipient, value);
    }
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

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L56-68)
```text
  function addLiquidityExactShares(
    address pool,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    uint256 maxAmountToken0,
    uint256 maxAmountToken1,
    bytes calldata extensionData
  ) external payable override returns (uint256 amount0Added, uint256 amount1Added) {
    _validateOwner(owner);
    _validateDeltas(deltas);
    return _addLiquidity(pool, owner, salt, deltas, msg.sender, maxAmountToken0, maxAmountToken1, extensionData);
  }
```
