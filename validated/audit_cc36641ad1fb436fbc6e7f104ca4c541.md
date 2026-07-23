Audit Report

## Title
Unattributed native ETH balance in `pay()` allows theft of stranded ETH from prior users — (`metric-periphery/contracts/base/PeripheryPayments.sol`)

## Summary
`PeripheryPayments.pay()` uses `address(this).balance` to settle WETH-input swaps without any per-user attribution. When a prior user strands ETH in the router by omitting a `refundETH` call, a subsequent attacker can have their entire WETH swap settled using that stranded ETH — paying nothing themselves — while the prior user permanently loses their funds.

## Finding Description
In `PeripheryPayments.sol` lines 73–84, when `token == WETH`, `pay()` reads the router's full native balance and uses it to settle the swap if `nativeBalance >= value`:

```solidity
uint256 nativeBalance = address(this).balance;
if (nativeBalance >= value) {
    IWETH9(WETH).deposit{value: value}();
    IERC20(WETH).safeTransfer(recipient, value);
    // no safeTransferFrom on payer — payer identity is ignored
}
``` [1](#0-0) 

The `payer` stored in transient storage via `_setNextCallbackContext` is completely bypassed in this branch. The router has no mechanism to track which user's `msg.value` contributed to the current native balance.

All public swap entry points — `exactInputSingle`, `exactInput`, `exactOutputSingle`, `exactOutput` — are `payable`, as is `multicall`, so ETH accumulates in the router whenever a user sends excess `msg.value`. [2](#0-1) [3](#0-2) 

The `receive()` guard only blocks direct ETH pushes from non-WETH addresses; it does not prevent ETH from accumulating via `msg.value` on payable functions. [4](#0-3) 

The intended pattern — confirmed by the test suite — is to include `refundETH` as a second call in the same `multicall` to recover excess ETH. If a user omits this step, the excess ETH is permanently stranded and claimable by any subsequent WETH-input swap caller. [5](#0-4) 

## Impact Explanation
This is a direct loss of user principal. A victim who sends `msg.value = X + Y` with `amountIn = X` (WETH) and omits `refundETH` strands `Y` ETH in the router. An attacker who calls `exactInputSingle{value: 0}` with `tokenIn = WETH` and `amountIn ≤ Y` receives the full swap output without paying any ETH or WETH. The pool's `IncorrectDelta` check passes because the pool receives the correct WETH amount (wrapped from the victim's stranded ETH). The victim's `Y` ETH is permanently lost. This meets the Sherlock threshold for a direct loss of user principal.

## Likelihood Explanation
The documented and tested usage pattern is `multicall{value: amountIn}(exactInputSingle(...), refundETH())`. Users who send a round-number ETH value slightly above the exact swap cost, or who construct the multicall without a `refundETH` step, will strand ETH. An attacker can monitor the router's ETH balance on-chain and submit a zero-cost WETH-input swap immediately after. No special privileges, approvals, or setup are required — any unprivileged caller can exploit this.

## Recommendation
**Short term:** Track the `msg.value` contributed by the current top-level call in a transient slot (e.g., in `multicall` or each payable swap function). In `pay()`, cap native ETH consumption to that tracked budget and pull the remainder from the payer via `safeTransferFrom`.

**Long term:** Automatically refund any unused `msg.value` at the end of each top-level payable call (end of `multicall` or each individual swap function), eliminating the possibility of stranded ETH between transactions.

## Proof of Concept
```
1. Victim calls:
   router.multicall{value: 2 ETH}([
     exactInputSingle(tokenIn=WETH, amountIn=1 ETH, ...)
     // no refundETH call
   ])
   → pay() sees nativeBalance=2 ETH >= 1 ETH
   → wraps 1 ETH, sends WETH to pool. 1 ETH stranded in router.

2. Attacker calls (in a later tx):
   router.exactInputSingle{value: 0}(
     tokenIn=WETH, amountIn=1 ETH, recipient=attacker, ...
   )
   → _justPayCallback fires, calls pay(WETH, attacker, pool, 1 ETH)
   → pay() sees nativeBalance=1 ETH >= 1 ETH
   → wraps victim's 1 ETH, safeTransfers WETH to pool
   → no safeTransferFrom on attacker (branch never reached)
   → pool's IncorrectDelta check passes (pool received correct WETH)
   → attacker receives swap output for free

Net: victim loses 1 ETH; attacker receives token output worth ~1 ETH.
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
