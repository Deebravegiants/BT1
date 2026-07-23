The code confirms the vulnerability. Let me verify the exact mechanics before rendering the final output.

The `pay()` function at [1](#0-0)  reads `address(this).balance` — the contract-wide ETH balance — with no per-caller accounting.

`exactInputSingle` is `payable` at [2](#0-1) , so ETH sent with a function call bypasses the `receive()` guard at [3](#0-2)  (which only blocks bare ETH transfers, not `msg.value` attached to function calls).

The transient payer slot correctly records the second caller as `payer` via `_setNextCallbackContext` at [4](#0-3) , but `pay()` never verifies that the ETH it wraps originated from that payer.

The test at [5](#0-4)  demonstrates that overpaying and calling `refundETH()` is the expected pattern — confirming that omitting `refundETH()` is a realistic user mistake that leaves ETH stranded.

---

Audit Report

## Title
Stale Native ETH in Router Consumed by Subsequent WETH Swapper — (`metric-periphery/contracts/base/PeripheryPayments.sol`)

## Summary
`PeripheryPayments.pay()` settles WETH swaps by reading `address(this).balance` — the router's total ETH balance — with no per-caller accounting. A user who overpays a `payable` swap entry-point and omits `refundETH()` leaves ETH stranded in the router across transaction boundaries. A subsequent caller swapping WETH with zero `msg.value` and zero WETH allowance will have their input silently funded by the victim's stranded ETH, constituting a direct cross-transaction theft of user principal.

## Finding Description
`pay()` in `PeripheryPayments.sol` (L73–84) branches on `token == WETH` and reads `uint256 nativeBalance = address(this).balance`. If `nativeBalance >= value`, it wraps that ETH and transfers WETH to the pool without touching the payer's ERC-20 allowance. This balance is contract-wide, not scoped to the current caller's `msg.value`.

ETH accumulates in the router because every swap entry-point (`exactInputSingle`, `exactInput`, `exactOutputSingle`, `exactOutput`) is `payable`. The `receive()` guard (L32–34) only rejects bare ETH transfers; it does not prevent ETH from accumulating via `msg.value` attached to function calls. A user who calls `exactInputSingle{value: X}` with `amountIn < X` and omits `refundETH()` leaves `X - amountIn` ETH stranded.

The transient-storage payer slot correctly records the second caller as `payer` via `_setNextCallbackContext` (MetricOmmSimpleRouter.sol L71), but `pay()` never checks whether the ETH it is about to wrap came from that payer. The callback path `metricOmmSwapCallback` → `_justPayCallback` → `pay(WETH, payer, pool, value)` (L192–199) reaches the vulnerable branch unconditionally for any WETH-input swap.

Exploit flow:
1. Victim calls `exactInputSingle{value: 1 ether}` with `amountIn = 0.5 ether`, omits `refundETH()`. Router retains 0.5 ETH.
2. Attacker calls `exactInputSingle` (no `msg.value`, no WETH allowance) with `tokenIn = WETH`, `amountIn = 0.5 ether`.
3. Pool triggers callback → `pay(WETH, attacker, pool, 0.5 ether)` → `nativeBalance = 0.5 ether >= value` → router wraps victim's ETH, transfers WETH to pool.
4. Attacker's WETH allowance: unchanged. Victim's 0.5 ETH: gone.

## Impact Explanation
Direct loss of user principal. The victim loses ETH they sent to the router; the attacker receives the corresponding swap output without spending any tokens or ETH. The pool's accounting is internally consistent (it receives the correct token amount), but the wrong party pays. This is a Critical/High direct theft of user funds meeting Sherlock thresholds.

## Likelihood Explanation
Medium. The precondition is that a victim leaves ETH in the router by overpaying and omitting `refundETH()`. The test suite (`test_multicall_ethInput_exactInputSingle_refundsUnusedEth`) demonstrates this is an expected and documented usage pattern, making the omission realistic. An attacker can monitor the router's ETH balance on-chain and exploit it immediately in the next block. The attack is repeatable and requires no special privileges.

## Recommendation
Track the ETH contributed by the current call rather than the contract's total balance. Pass `msg.value` (or a per-call ETH budget) into `pay()` and consume only from that amount, refunding any remainder. Alternatively, enforce that `address(this).balance == 0` at the start of every swap entry-point, requiring callers to use multicall with `refundETH()` for any ETH-input swap.

## Proof of Concept
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

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L71-71)
```text
    _setNextCallbackContext(params.pool, CALLBACK_MODE_JUST_PAY, msg.sender, params.tokenIn);
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
