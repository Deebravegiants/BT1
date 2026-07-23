Audit Report

## Title
Unattributed native ETH balance in `pay()` allows theft of stranded ETH from prior users — (`metric-periphery/contracts/base/PeripheryPayments.sol`)

## Summary

`PeripheryPayments.pay()` resolves WETH payments by checking `address(this).balance` with no per-user accounting. When a prior user's `msg.value` overpayment leaves ETH stranded in the router, any subsequent WETH-input swap caller can have their entire payment settled from that stranded ETH — paying nothing themselves — while the prior user permanently loses their funds.

## Finding Description

In `pay()`, when `token == WETH` and `payer != address(this)`, the function reads the router's total native balance:

```solidity
uint256 nativeBalance = address(this).balance;
if (nativeBalance >= value) {
    IWETH9(WETH).deposit{value: value}();
    IERC20(WETH).safeTransfer(recipient, value);   // payer never pulled
} else if (nativeBalance > 0) { ... }
``` [1](#0-0) 

When `nativeBalance >= value`, `safeTransferFrom` is never called on `payer`. The payer identity stored in transient storage is completely ignored for the actual token settlement.

ETH accumulates between transactions because:

1. All four swap entry points are `payable` — `exactInputSingle`, `exactInput`, `exactOutputSingle`, `exactOutput` — so users routinely send `msg.value` to fund WETH-input swaps. [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

2. `refundETH()` is a separate, optional call — it is never invoked automatically at the end of `multicall` or any swap function. [6](#0-5) 

3. The `receive()` guard only blocks direct ETH pushes from non-WETH addresses; it does not prevent ETH from accumulating via `msg.value` on payable functions. [7](#0-6) 

4. `multicall` has no automatic refund or `msg.value` budget tracking. [8](#0-7) 

The pool's `IncorrectDelta` check passes because the pool receives the correct WETH amount regardless of its origin — it cannot distinguish victim ETH from attacker ETH.

## Impact Explanation

Direct loss of user principal. A victim who sends `msg.value = X + Y` with `amountIn = X` (WETH) and omits `refundETH` strands `Y` ETH in the router. An attacker calling any WETH-input swap with `amountIn ≤ Y` and `msg.value = 0` receives full swap output without paying any ETH or WETH. The victim's `Y` ETH is permanently unrecoverable (unless the attacker is front-run by another attacker). This is a direct loss of user principal above Sherlock thresholds, exploitable by any unprivileged caller with no special setup.

## Likelihood Explanation

The documented and tested usage pattern is `multicall{value: amountIn}([exactInputSingle(...), refundETH()])`. Users who omit the `refundETH` step, send a round-number ETH value slightly above the exact swap cost, or construct a single-call (non-multicall) payable swap will strand ETH. An attacker can monitor the router's ETH balance on-chain or watch the mempool and immediately follow up with a zero-cost WETH swap. No approvals, privileges, or prior setup are required. The attack is repeatable across any number of victims.

## Recommendation

**Short term:** Track the `msg.value` budget per top-level call in a transient storage slot (set at entry to `multicall` or each payable swap function). In `pay()`, consume native ETH only up to the tracked budget for the current transaction; pull the remainder from `payer` via `safeTransferFrom`.

**Long term:** Automatically refund any unused `msg.value` at the end of each top-level payable call (`multicall` and each individual swap function), eliminating the possibility of ETH stranding between transactions.

## Proof of Concept

```
1. Victim calls:
   router.multicall{value: 2 ETH}([
     exactInputSingle(tokenIn=WETH, amountIn=1 ETH, ...)
     // no refundETH call
   ])
   → pay() sees address(this).balance = 2 ETH >= 1 ETH
   → wraps 1 ETH, safeTransfers WETH to pool
   → 1 ETH remains stranded in router

2. Attacker calls (next tx):
   router.exactInputSingle{value: 0}(
     tokenIn=WETH, amountIn=1 ETH, recipient=attacker, ...
   )
   → pay() sees address(this).balance = 1 ETH >= 1 ETH
   → wraps victim's 1 ETH, safeTransfers WETH to pool
   → safeTransferFrom(attacker, ...) never called
   → pool's IncorrectDelta check passes (correct WETH received)
   → attacker receives swap output worth ~1 ETH for free

Net: victim loses 1 ETH permanently; attacker receives token output worth ~1 ETH.
```

Foundry test scaffold: deploy router with WETH, fund victim with 2 ETH, call `exactInputSingle{value: 2 ether}(amountIn=1 ETH)` without `refundETH`, assert `address(router).balance == 1 ether`, then call `exactInputSingle{value: 0}(amountIn=1 ETH)` from attacker address, assert attacker received swap output and `address(router).balance == 0`. The existing test at `metric-periphery/test/MetricOmmSimpleRouter.native.t.sol` lines 106–133 confirms the refund-dependent pattern and can be adapted by removing the `refundETH` call to reproduce the stranding condition.

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

**File:** metric-periphery/contracts/base/PeripheryPayments.sol (L74-84)
```text
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

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L39-44)
```text
  function multicall(bytes[] calldata data) public payable override returns (bytes[] memory results) {
    results = new bytes[](data.length);
    for (uint256 i = 0; i < data.length; i++) {
      results[i] = Address.functionDelegateCall(address(this), data[i]);
    }
  }
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L67-67)
```text
  function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut) {
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L92-92)
```text
  function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut) {
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L130-130)
```text
  function exactOutputSingle(ExactOutputSingleParams calldata params) external payable returns (uint256 amountIn) {
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L154-154)
```text
  function exactOutput(ExactOutputParams calldata params) external payable returns (uint256 amountIn) {
```
