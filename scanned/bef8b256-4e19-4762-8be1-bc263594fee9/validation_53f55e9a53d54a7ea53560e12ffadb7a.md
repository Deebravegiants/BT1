The code is fully readable. Let me trace the exact execution path and assess the claim.

**The `pay` function** (`PeripheryPayments.sol` lines 73–84):

```solidity
} else if (token == WETH) {
    uint256 nativeBalance = address(this).balance;   // ALL ETH in contract
    if (nativeBalance >= value) {
        IWETH9(WETH).deposit{value: value}();
        IERC20(WETH).safeTransfer(recipient, value);
    } else if (nativeBalance > 0) {
        IWETH9(WETH).deposit{value: nativeBalance}();
        IERC20(WETH).safeTransfer(recipient, nativeBalance);
        IERC20(WETH).safeTransferFrom(payer, recipient, value - nativeBalance); // payer pays only remainder
    } else {
        IERC20(WETH).safeTransferFrom(payer, recipient, value);
    }
}
```

**Can ETH accumulate between transactions?**

The `receive()` guard blocks direct ETH pushes from non-WETH addresses: [1](#0-0) 

However, all swap entry points are `payable` — `exactInputSingle`, `exactOutputSingle`, `exactInput`, `exactOutput`, and `multicall` all accept ETH. When a user sends more ETH than the swap consumes (e.g., `exactOutputSingle{value: 1000}` where actual input is 600), the `pay` function uses exactly `value` ETH and the remaining 400 ETH stays in the router: [2](#0-1) 

The test suite confirms this pattern explicitly — the recommended usage is `multicall{value}([exactInputSingle, refundETH])`, and the test `test_multicall_ethInput_exactInputSingle_refundsUnusedEth` shows that without `refundETH`, excess ETH is stranded: [3](#0-2) 

**The attack path is real:**

1. User A calls `exactOutputSingle{value: 1000}` (actual input = 600), omitting `refundETH()`. 400 ETH remains in the router.
2. User B calls `exactInputSingle` with `tokenIn = WETH`, `amountIn = 800`, sending no ETH.
3. Pool calls back → `_justPayCallback` → `pay(WETH, userB, pool, 800)`.
4. `nativeBalance = 400 > 0`, so the router wraps 400 ETH → transfers to pool, then pulls only 400 WETH from User B via `safeTransferFrom`.
5. Pool receives full 800 WETH. User B pays 400 WETH instead of 800. User A's 400 ETH is consumed silently. [4](#0-3) [5](#0-4) 

**No guard prevents this.** The `pay` function reads `address(this).balance` — the total contract ETH — with no accounting for which transaction deposited it. There is no transient-storage tracking of `msg.value` per call, no cap on how much native ETH can be consumed per swap, and no check that the native balance was contributed by the current payer.

---

### Title
Residual ETH in Router Silently Subsidizes Subsequent WETH Swaps, Stealing Prior User's ETH — (`metric-periphery/contracts/base/PeripheryPayments.sol`)

### Summary
`PeripheryPayments.pay` uses `address(this).balance` (the entire contract ETH balance) when settling WETH swap inputs. ETH left in the router from a prior user's payable call is consumed to partially fund a subsequent user's WETH payment, causing the prior user to lose their stranded ETH with no recourse.

### Finding Description
The `pay` function's WETH branch reads `nativeBalance = address(this).balance` without any per-transaction accounting. When `0 < nativeBalance < value`, it wraps and forwards all available native ETH to the pool, then pulls only `value - nativeBalance` from the actual payer. Because all swap entry points are `payable` and users routinely send excess ETH for exact-output swaps (expecting to reclaim it via `refundETH()`), any ETH not reclaimed in the same multicall persists in the router across transaction boundaries. A subsequent WETH swap by any user will silently consume that residual ETH, reducing the payer's ERC-20 WETH debit by exactly the residual amount. [6](#0-5) 

### Impact Explanation
Direct loss of user principal. User A's stranded ETH is transferred to the pool as WETH on behalf of User B, with no event, no revert, and no recovery path. User A cannot distinguish this from a normal refund failure. The pool's balances are unaffected (it receives the correct `value`), so pool solvency is intact, but per-user settlement conservation is broken: User B's net WETH debit is `value - residual` instead of `value`.

### Likelihood Explanation
Moderate. The exact-output payable pattern (`exactOutputSingle{value: X}` where X > actual input) is the standard native-ETH usage pattern documented in the test suite and NatDoc. Users who omit `refundETH()` — whether by mistake, by using a frontend that doesn't batch it, or by a failed multicall that reverts after the swap — leave ETH stranded. Any subsequent WETH swap by any address drains it. An attacker can monitor the router's ETH balance on-chain and front-run the next WETH swap to capture the subsidy.

### Recommendation
Track the ETH contributed by the current transaction in transient storage at each payable entry point (storing `msg.value`), and cap native ETH consumption in `pay` to that per-call budget rather than `address(this).balance`. Alternatively, pass the caller-contributed ETH amount explicitly through the call stack so `pay` can distinguish owned ETH from residual ETH.

### Proof of Concept
```solidity
// 1. User A: exact-output WETH swap, sends excess ETH, omits refundETH
router.exactOutputSingle{value: 1000}(ExactOutputSingleParams({
    tokenIn: WETH, amountOut: someOutput, amountInMaximum: 1000, ...
}));
// actual input consumed = 600; router.balance = 400 (User A's ETH, stranded)

// 2. User B: exact-input WETH swap, sends no ETH
router.exactInputSingle(ExactInputSingleParams({
    tokenIn: WETH, amountIn: 800, ...
}));
// pay(WETH, userB, pool, 800) is called in callback
// nativeBalance = 400 → wraps 400 ETH → safeTransfer(pool, 400)
// safeTransferFrom(userB, pool, 400)  ← userB pays only 400, not 800
// pool receives 800 WETH ✓, userB saves 400 WETH, userA loses 400 ETH
assert(weth.balanceOf(userB_before) - weth.balanceOf(userB_after) == 400); // not 800
assert(address(router).balance == 0); // User A's ETH is gone
```

### Citations

**File:** metric-periphery/contracts/base/PeripheryPayments.sol (L32-34)
```text
  receive() external payable {
    if (msg.sender != WETH) revert NotWETH();
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
