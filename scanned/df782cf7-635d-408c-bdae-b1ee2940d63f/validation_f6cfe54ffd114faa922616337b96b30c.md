### Title
Excess or misrouted `msg.value` strands ETH in `MetricOmmSimpleRouter` / `MetricOmmPoolLiquidityAdder`, enabling theft via `refundETH()` or free swaps via `pay()` — (`metric-periphery/contracts/base/PeripheryPayments.sol`)

---

### Summary

Every swap and liquidity entry point in `MetricOmmSimpleRouter` and `MetricOmmPoolLiquidityAdder` is `payable`, but none of them validate that `msg.value == 0` when `tokenIn` is not WETH, or that `msg.value == amountIn` when it is WETH. Excess ETH accumulates silently in the router. A subsequent caller can then either (a) steal it directly via `refundETH()`, which unconditionally forwards the entire contract ETH balance to `msg.sender`, or (b) receive a free swap because `pay()` prefers the contract's native balance over pulling from the actual payer.

---

### Finding Description

**Root cause — no `msg.value` guard on payable entry points**

`exactInputSingle`, `exactInput`, `exactOutputSingle`, `exactOutput`, `addLiquidityExactShares`, and `addLiquidityWeighted` are all declared `payable`: [1](#0-0) [2](#0-1) [3](#0-2) 

None of them check `msg.value == 0` when `tokenIn != WETH`, or `msg.value == amountIn` when `tokenIn == WETH`.

**Root cause — `pay()` silently consumes the contract's native balance**

When the callback fires and `token == WETH`, `pay()` first checks the contract's own ETH balance: [4](#0-3) 

- If `nativeBalance >= value` (line 75–77): the contract wraps its own ETH and sends it to the pool — the declared `payer` contributes **nothing**.
- If `0 < nativeBalance < value` (line 78–81): the contract partially subsidises the swap from its own ETH, then pulls only the remainder from the payer.

**Root cause — `refundETH()` sends to `msg.sender`, not the original depositor** [5](#0-4) 

Any caller — not the user who accidentally left ETH — can invoke `refundETH()` and receive the full balance.

**`receive()` does not protect against ETH sent via function calls** [6](#0-5) 

`receive()` rejects plain ETH transfers from non-WETH addresses, but ETH attached to a `payable` function call bypasses `receive()` entirely and is accepted unconditionally.

---

### Impact Explanation

**Attack vector A — direct ETH theft via `refundETH()`**

1. Alice calls `exactInputSingle{value: 2 ether}(tokenIn=WETH, amountIn=1 ether, ...)`.
2. `pay()` wraps exactly 1 ETH; 1 ETH remains in the router.
3. Bob (or a front-running bot) calls `refundETH()` and receives Alice's 1 ETH.

Alice loses 1 ETH with no recourse.

**Attack vector B — free swap using a prior victim's ETH**

1. Alice's excess 1 ETH is stranded in the router (same setup as above).
2. Bob calls `exactInputSingle{value: 0}(tokenIn=WETH, amountIn=1 ether, ...)` without sending any ETH or pre-approving WETH.
3. Inside `_justPayCallback` → `pay()`, `nativeBalance (1 ETH) >= value (1 ETH)`, so the router wraps Alice's ETH and forwards it to the pool on Bob's behalf.
4. Bob receives the full swap output for free; Alice's ETH is permanently consumed.

**Attack vector C — non-WETH token with accidental ETH**

A user calls any swap or liquidity function with `tokenIn != WETH` but attaches ETH. `pay()` takes the `else` branch and calls `safeTransferFrom` on the ERC-20, ignoring `msg.value` entirely. The ETH is stranded and claimable by anyone. [7](#0-6) 

---

### Likelihood Explanation

- Any user who sends ETH alongside a WETH swap with `msg.value > amountIn`, or who mistakenly attaches ETH to a non-WETH swap, triggers the vulnerability.
- Front-running bots routinely monitor mempool for stranded-ETH patterns; `refundETH()` is a zero-cost, permissionless call.
- Attack vector B requires no front-running: the attacker simply submits a WETH swap with `msg.value = 0` after the victim's transaction is confirmed.

Likelihood: **Medium** (requires a user error, but the error is easy to make and the exploit is trivial).

---

### Recommendation

1. **Add `msg.value` guards to every payable entry point.** When `tokenIn != WETH`, require `msg.value == 0`. When `tokenIn == WETH`, require `msg.value == 0 || msg.value == amountIn` (or enforce exact equality):

```solidity
function exactInputSingle(ExactInputSingleParams calldata params)
    external payable returns (uint256 amountOut)
{
    if (params.tokenIn != WETH) {
        require(msg.value == 0, "ETH sent for non-WETH token");
    } else {
        require(msg.value == 0 || msg.value == params.amountIn, "msg.value != amountIn");
    }
    // ...
}
```

2. **Alternatively, auto-refund excess ETH** at the end of each entry point (after the swap/liquidity call) rather than relying on a separate `refundETH()` call.

3. **Restrict `refundETH()` to `msg.sender` only within a multicall context**, or document clearly that any stranded ETH is claimable by anyone, so integrators understand the risk.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

// Assume router is deployed, WETH/token1 pool exists, Alice has approved nothing.

function testFreeSwap(address router, address pool, address weth, address token1) external {
    // Step 1: Alice swaps 1 ETH → token1 but accidentally sends 2 ETH
    IMetricOmmSimpleRouter(router).exactInputSingle{value: 2 ether}(
        IMetricOmmSimpleRouter.ExactInputSingleParams({
            pool: pool,
            tokenIn: weth,
            recipient: alice,
            amountIn: 1 ether,
            amountOutMinimum: 0,
            zeroForOne: true,
            priceLimitX64: 0,
            deadline: block.timestamp,
            extensionData: ""
        })
    );
    // Router now holds 1 ETH (Alice's excess).

    // Step 2: Bob calls exactInputSingle with msg.value=0, no WETH approval needed.
    // pay() sees nativeBalance(1 ETH) >= value(1 ETH) → uses Alice's ETH for Bob's swap.
    IMetricOmmSimpleRouter(router).exactInputSingle{value: 0}(
        IMetricOmmSimpleRouter.ExactInputSingleParams({
            pool: pool,
            tokenIn: weth,
            recipient: bob,
            amountIn: 1 ether,
            amountOutMinimum: 0,
            zeroForOne: true,
            priceLimitX64: 0,
            deadline: block.timestamp,
            extensionData: ""
        })
    );
    // Bob receives token1 output; Alice's 1 ETH is gone.
}
``` [8](#0-7) [9](#0-8)

### Citations

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L67-67)
```text
  function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut) {
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L130-130)
```text
  function exactOutputSingle(ExactOutputSingleParams calldata params) external payable returns (uint256 amountIn) {
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
