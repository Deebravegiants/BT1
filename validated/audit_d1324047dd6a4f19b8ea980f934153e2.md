Audit Report

## Title
Router's Stranded Native ETH Consumed for Zero-`msg.value` WETH-Input Swap — (`metric-periphery/contracts/base/PeripheryPayments.sol`)

## Summary
`PeripheryPayments.pay()` uses `address(this).balance` — the router's entire native ETH balance — when settling a WETH-input swap, with no check that the ETH originated from the current transaction's `msg.value`. A victim who sends excess ETH via a `payable` entry point and omits `refundETH` leaves ETH stranded in the router. An attacker can then call `exactInputSingle{value: 0}(tokenIn=WETH, ...)` and have the router silently consume the victim's stranded ETH to fund the swap, receiving real output tokens at zero cost.

## Finding Description

`pay()` in `PeripheryPayments.sol` handles WETH-input swaps by reading the router's full native balance: [1](#0-0) 

When `nativeBalance >= value` (line 75), the router wraps its own ETH and transfers WETH to the pool with no `safeTransferFrom` from the payer. The `payer` argument (the attacker's address) is never consulted in this branch.

The entry point `exactInputSingle` is `payable` and stores `msg.sender` as the payer in transient storage: [2](#0-1) 

The callback then calls `pay()` with that stored payer: [3](#0-2) 

The pool's `IncorrectDelta` guard only verifies the pool received the correct token amount; it is indifferent to whether the WETH was wrapped from the attacker's ETH or from a prior user's stranded ETH: [4](#0-3) 

The `receive()` guard prevents arbitrary ETH injection but does not prevent ETH from accumulating via `msg.value` in prior payable calls: [5](#0-4) 

The test suite confirms `refundETH` is optional and not enforced by the router: [6](#0-5) 

## Impact Explanation
A prior user's stranded ETH is consumed to settle an attacker's swap. The attacker receives real pool output tokens without transferring any asset. The victim permanently loses the ETH left in the router. Loss magnitude equals `min(router.balance, attacker's amountIn)` and is bounded only by how much ETH the victim forgot to reclaim. This is a direct loss of user principal with no protocol-level mitigation, meeting Critical/High severity under Sherlock thresholds.

## Likelihood Explanation
Users routinely over-send ETH to guarantee a swap succeeds and rely on `refundETH` to recover the surplus. Omitting `refundETH` is a realistic user error, particularly when calling `exactInputSingle` directly (not via multicall). The router's ETH balance is publicly readable on-chain. An attacker can monitor it and exploit it atomically in a single transaction with zero capital at risk.

## Recommendation
In `pay()`, when `token == WETH`, only consume native ETH up to the amount that belongs to the current call context. The cleanest approach is to pass `msg.value` of the originating call as a parameter (or store it in transient storage at entry alongside the other callback context fields) and cap native ETH consumption to that value. Any shortfall must be pulled from the payer via `safeTransferFrom`. Alternatively, enforce `address(this).balance == 0` at the start of every non-multicall payable entry point, or document and enforce via a modifier that WETH-input swaps must always be paired with `refundETH` in a multicall.

## Proof of Concept
```
1. Victim calls router.exactInputSingle{value: 10_000}(tokenIn=WETH, amountIn=1_000, ...)
   → swap uses 1_000 ETH worth of WETH; 9_000 ETH remains in router.
   → Victim does NOT call refundETH.

2. Attacker calls router.exactInputSingle{value: 0}(tokenIn=WETH, amountIn=9_000, ...)
   → Pool executes swap, calls metricOmmSwapCallback on router.
   → Router calls pay(WETH, attacker, pool, 9_000).
   → nativeBalance (9_000) >= value (9_000) → branch at line 75 taken.
   → Router wraps its own 9_000 ETH and transfers WETH to pool.
   → Pool's IncorrectDelta check passes (pool received correct WETH).
   → Attacker receives pool output tokens.

Result: Attacker paid 0 ETH; victim lost 9_000 ETH.
```

A Foundry test can reproduce this by: (1) pranking a victim to call `exactInputSingle{value: 10_000}` with `amountIn=1_000` and no `refundETH`; (2) asserting `address(router).balance == 9_000`; (3) pranking an attacker to call `exactInputSingle{value: 0}` with `amountIn=9_000`; (4) asserting the attacker received output tokens and `address(router).balance == 0`.

### Citations

**File:** metric-periphery/contracts/base/PeripheryPayments.sol (L32-34)
```text
  receive() external payable {
    if (msg.sender != WETH) revert NotWETH();
  }
```

**File:** metric-periphery/contracts/base/PeripheryPayments.sol (L73-84)
```text
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
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L67-71)
```text
  function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut) {
    _checkDeadline(params.deadline);
    uint128 priceLimitX64 = MetricOmmSwapPath.normalizePriceLimit(params.zeroForOne, params.priceLimitX64);

    _setNextCallbackContext(params.pool, CALLBACK_MODE_JUST_PAY, msg.sender, params.tokenIn);
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

**File:** metric-core/contracts/MetricOmmPool.sol (L257-263)
```text
      uint256 balance0Before = balance0();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
      // casting to uint256 is safe because amount0Delta is positive and the ammount of tokens in pool is capped by uint128.max
      // forge-lint: disable-next-line(unsafe-typecast)
      if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
        revert IncorrectDelta();
      }
```

**File:** metric-periphery/test/MetricOmmSimpleRouter.native.t.sol (L106-133)
```text
  function test_multicall_ethInput_exactInputSingle_refundsUnusedEth() public {
    uint128 amountIn = 1_000;
    uint256 msgValue = 2 ether;
    uint256 swapperEthBefore = swapper.balance;

    vm.prank(swapper);
    bytes[] memory calls = new bytes[](2);
    calls[0] = abi.encodeWithSelector(
      router.exactInputSingle.selector,
      IMetricOmmSimpleRouter.ExactInputSingleParams({
        pool: address(pool),
        tokenIn: address(weth),
        tokenOut: address(token1),
        zeroForOne: true,
        amountIn: amountIn,
        amountOutMinimum: 0,
        recipient: recipient,
        deadline: _deadline(),
        priceLimitX64: 0,
        extensionData: ""
      })
    );
    calls[1] = abi.encodeWithSelector(router.refundETH.selector);
    router.multicall{value: msgValue}(calls);

    assertEq(swapper.balance, swapperEthBefore - amountIn, "unused eth refunded");
    _assertRouterEmpty();
  }
```
