The vulnerability is real and traceable through the exact code. Here is the full analysis:

---

### Title
Leftover Native ETH on Router Consumed by Subsequent User's WETH Swap — (`metric-periphery/contracts/base/PeripheryPayments.sol`)

### Summary

`PeripheryPayments.pay()` uses the router's entire `address(this).balance` to settle WETH swap inputs without any per-user accounting. ETH left on the router from a prior user's `msg.value` overpayment is silently consumed by the next user's WETH swap, causing the prior user to lose their ETH and the subsequent user to pay nothing from their own allowance.

### Finding Description

`exactInputSingle` (and all other `payable` swap entry points) accept `msg.value`. When `tokenIn == WETH`, the intended flow is: user sends ETH → `pay()` wraps it → WETH goes to pool. If the user sends more ETH than the swap consumes (e.g., for slippage tolerance), the surplus stays on the router until `refundETH()` is called.

The `receive()` guard only blocks *direct* ETH transfers from non-WETH addresses: [1](#0-0) 

It does **not** prevent ETH from accumulating via `msg.value` in payable functions. So ETH can and does persist on the router between transactions.

When the next user calls `exactInputSingle` with `tokenIn == WETH`, the callback path is:

`exactInputSingle` → `_setNextCallbackContext(pool, CALLBACK_MODE_JUST_PAY, msg.sender, tokenIn)` → pool calls back → `_justPayCallback` → `pay(token, payer, pool, value)` [2](#0-1) [3](#0-2) 

Inside `pay()`, the WETH branch reads the router's **total** native balance with no per-user attribution: [4](#0-3) 

If `address(this).balance >= value`, the function wraps the router's ETH and transfers WETH to the pool — **without pulling a single token from `payer`'s allowance**. The `payer` stored in transient storage is the current `msg.sender`, but their allowance is never touched. [5](#0-4) 

### Impact Explanation

**Direct fund loss (High):** User A sends `exactInputSingle` with `msg.value = 1 ETH` for a swap that only consumes `0.6 ETH`. The remaining `0.4 ETH` stays on the router. User A intends to call `refundETH()` but has not yet done so (or forgets). User B calls `exactInputSingle` with `tokenIn = WETH`, `amountIn = 0.4 ETH`, zero WETH allowance. The callback fires, `pay()` sees `nativeBalance = 0.4 ETH >= value = 0.4 ETH`, wraps User A's ETH, and sends WETH to the pool. User B's swap settles in full; User A's `0.4 ETH` is gone. User A can no longer reclaim it via `refundETH()` because the balance is now zero.

The pool is correctly settled (it receives the right WETH amount), so there is no pool insolvency — but there is a direct, irreversible transfer of User A's funds to benefit User B.

### Likelihood Explanation

- ETH overpayment is the standard pattern for WETH swaps (users send `amountIn + slippage buffer` and rely on `refundETH`).
- Any attacker watching the mempool or the router's ETH balance can front-run or follow-up immediately after a swap that leaves ETH behind.
- No special permissions, malicious pool setup, or non-standard tokens are required.

### Recommendation

Track the ETH deposited by the **current transaction** in transient storage (e.g., record `msg.value` at entry in `exactInputSingle`/`exactInput`/etc.) and cap the native ETH used in `pay()` to that per-call budget. Any ETH beyond the budget must be pulled from `payer` via `transferFrom`. Alternatively, require that `address(this).balance == 0` at the start of each swap entry point (enforced by a transient guard), reverting if stale ETH is present.

### Proof of Concept

```solidity
// Foundry integration test sketch
function test_staleEthConsumedBySubsequentSwapper() public {
    // User A sends exactInputSingle with 1 ETH, swap only needs 0.6 ETH
    vm.deal(userA, 1 ether);
    vm.prank(userA);
    router.exactInputSingle{value: 1 ether}(ExactInputSingleParams({
        pool: address(pool), tokenIn: address(weth), ..., amountIn: 0.6 ether, ...
    }));
    // 0.4 ETH remains on router; userA has not called refundETH

    assertEq(address(router).balance, 0.4 ether);

    // User B has zero WETH allowance, calls exactInputSingle for 0.4 ETH worth of WETH
    uint256 allowanceBefore = weth.allowance(userB, address(router));
    vm.prank(userB);
    router.exactInputSingle{value: 0}(ExactInputSingleParams({
        pool: address(pool), tokenIn: address(weth), ..., amountIn: 0.4 ether, ...
    }));

    // Assert: userB's WETH allowance was not consumed
    assertEq(weth.allowance(userB, address(router)), allowanceBefore);
    // Assert: router ETH is now zero (userA's ETH was consumed)
    assertEq(address(router).balance, 0);
    // Assert: pool received full amountIn in WETH
    assertEq(weth.balanceOf(address(pool)) - poolBalanceBefore, 0.4 ether);
}
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

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L71-71)
```text
    _setNextCallbackContext(params.pool, CALLBACK_MODE_JUST_PAY, msg.sender, params.tokenIn);
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L192-198)
```text
  function _justPayCallback(int256 amount0Delta, int256 amount1Delta) private {
    pay(
      _getTokenToPay(),
      _getPayer(),
      msg.sender,
      uint256(MetricOmmSwapResults.extractPositiveAmount(amount0Delta, amount1Delta))
    );
```
