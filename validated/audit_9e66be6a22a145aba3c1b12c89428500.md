The code is clear. Let me trace the exact path described.

The vulnerability is real and traceable end-to-end. Here is the full finding.

---

### Title
Prior User's Leftover ETH Silently Consumed by Subsequent WETH Swap — (`metric-periphery/contracts/base/PeripheryPayments.sol`)

---

### Summary

`PeripheryPayments.pay` reads `address(this).balance` — the router's **total** native ETH balance — when settling a WETH swap. Because that balance accumulates across transactions, any ETH left over from a prior user's payable call is silently consumed to subsidize the next user's WETH input, causing direct loss of the prior user's funds.

---

### Finding Description

The `pay` function contains a hybrid native/ERC-20 settlement path for WETH: [1](#0-0) 

When `0 < address(this).balance < value`, the middle branch (lines 78-81) fires:

1. Wraps **all** of `address(this).balance` into WETH and transfers it to the pool.
2. Pulls only `value - nativeBalance` WETH from `payer`.

`address(this).balance` is not scoped to the current transaction's `msg.value`. It includes ETH deposited by any prior caller who sent ETH via a `payable` entry-point (e.g. `exactInputSingle{value: ...}`) and did not yet call `refundETH`.

`exactInputSingle` is `payable` and stores no per-user ETH accounting: [2](#0-1) 

The `receive()` guard only blocks direct ETH pushes from non-WETH addresses; it does not prevent ETH from accumulating via `msg.value` in payable calls: [3](#0-2) 

---

### Impact Explanation

User A sends `0.5 ETH` with a WETH swap for `0.3 WETH` amountIn. The first branch of `pay` wraps exactly `0.3 ETH`; `0.2 ETH` remains in the router. Before user A calls `refundETH`, user B calls `exactInputSingle(tokenIn=WETH, amountIn=1 ether)` with no ETH. The middle branch fires: user A's `0.2 ETH` is wrapped and forwarded to the pool, and only `0.8 WETH` is pulled from user B. User A's `0.2 ETH` is permanently lost. The pool receives the correct `1 WETH`, so no pool insolvency occurs — the loss falls entirely on user A.

---

### Likelihood Explanation

- Any user who sends ETH with a WETH-input swap and does not atomically batch `refundETH` in the same `multicall` leaves ETH exposed.
- An attacker can passively monitor the router's ETH balance on-chain and issue a WETH swap immediately after detecting a non-zero balance, front-running the victim's `refundETH`.
- No privileged role, malicious pool, or non-standard token is required.

---

### Recommendation

Track only the ETH that arrived in the **current** transaction. Replace the `address(this).balance` read with a value derived from `msg.value` passed down through the call stack, or record the pre-call balance at entry and use only the delta. Alternatively, require that WETH swaps using native ETH consume exactly `msg.value` and revert if `msg.value` does not cover the full `amountIn`, eliminating the partial-native hybrid path entirely.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

// Foundry unit test (pseudo-code outline)
function test_priorUserEthConsumedByWethSwap() public {
    // User A: send 0.5 ETH, swap WETH amountIn = 0.3 ether
    // After swap: router holds 0.2 ETH (user A's change, refundETH not yet called)
    uint256 routerEthBefore = address(router).balance; // 0.2 ether

    // User B: swap WETH amountIn = 1 ether, sends 0 ETH
    // pay() middle branch fires: wraps 0.2 ETH (user A's), pulls 0.8 WETH from user B
    vm.prank(userB);
    router.exactInputSingle(ExactInputSingleParams({
        tokenIn: WETH, amountIn: 1 ether, ...
    }));

    // User A calls refundETH — receives nothing
    vm.prank(userA);
    router.refundETH();

    assertEq(userA.balance, initialUserABalance - 0.5 ether); // lost 0.2 ETH
    assertEq(address(router).balance, 0);
}
```

The pool receives exactly `1 WETH` in both cases, confirming no pool-level invariant is broken — the loss is borne entirely by user A whose `0.2 ETH` was silently consumed.

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
