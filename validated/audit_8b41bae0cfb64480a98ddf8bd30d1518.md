### Title
Unguarded `msg.value` on Non-WETH Swap and Liquidity Functions Allows Accidental ETH to Be Stolen via `refundETH()` — (File: `metric-periphery/contracts/base/PeripheryPayments.sol`, `metric-periphery/contracts/MetricOmmSimpleRouter.sol`, `metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol`)

---

### Summary

All four swap entry-points in `MetricOmmSimpleRouter` and all four liquidity entry-points in `MetricOmmPoolLiquidityAdder` are declared `payable`, yet none of them validate `msg.value == 0` when the token being paid is a plain ERC-20 (not WETH). Any ETH accidentally sent with such a call is silently accepted, left in the router, and immediately claimable by any third party through the permissionless `refundETH()` helper, which forwards `address(this).balance` to `msg.sender`.

---

### Finding Description

`MetricOmmSimpleRouter` exposes four `payable` swap functions:

- `exactInputSingle` [1](#0-0) 
- `exactInput` [2](#0-1) 
- `exactOutputSingle` [3](#0-2) 
- `exactOutput` [4](#0-3) 

`MetricOmmPoolLiquidityAdder` exposes four `payable` liquidity functions:

- `addLiquidityExactShares` (two overloads) [5](#0-4) 
- `addLiquidityWeighted` (two overloads) [6](#0-5) 

The interface documentation itself states the router's scope is **"ERC-20 routes only. No native ETH, WETH wrap/unwrap…"**, confirming native ETH is not an intended input for these paths. [7](#0-6) 

The internal `pay()` function in `PeripheryPayments` branches on the token address:

```solidity
function pay(address token, address payer, address recipient, uint256 value) internal {
    if (payer == address(this)) {
        IERC20(token).safeTransfer(recipient, value);
    } else if (token == WETH) {
        uint256 nativeBalance = address(this).balance;
        if (nativeBalance >= value) { ... }   // uses ETH
        ...
    } else {
        IERC20(token).safeTransferFrom(payer, recipient, value);  // ignores ETH
    }
}
``` [8](#0-7) 

When `token != WETH`, the `else` branch executes a plain `safeTransferFrom` and **never touches `address(this).balance`**. Any ETH sent with the call is silently retained in the contract.

`refundETH()` is permissionless and sends the entire contract balance to whoever calls it:

```solidity
function refundETH() external payable override {
    uint256 balance = address(this).balance;
    if (balance > 0) {
        _transferETH(msg.sender, balance);
    }
}
``` [9](#0-8) 

There is no access control, no recipient parameter, and no link back to the original depositor.

A secondary impact exists: if ETH is already sitting in the router when a **different** user performs a WETH swap, `pay()` will consume that ETH first (lines 74–77) to satisfy the second user's WETH obligation, effectively transferring the first user's ETH to the pool on behalf of the second user. [10](#0-9) 

---

### Impact Explanation

A user who accidentally sends ETH alongside a non-WETH swap or liquidity call permanently loses that ETH. The ETH is either:

1. **Stolen** — any MEV bot or observer calls `refundETH()` in the same or a subsequent block and receives the full balance.
2. **Misappropriated** — a subsequent WETH swap by any user causes `pay()` to wrap and forward the stuck ETH to the pool, paying that user's obligation with the victim's funds.

In both cases the victim has no on-chain recourse. This is a direct loss of user principal.

---

### Likelihood Explanation

- All swap and liquidity functions are `payable`, so wallets, aggregators, and multicall bundles can forward ETH without any EVM-level rejection.
- Users frequently confuse native ETH with WETH, especially when building multicall bundles that mix `unwrapWETH9` / `refundETH` with swap calls.
- MEV bots routinely monitor for unprotected `refundETH`-style helpers; the window between the victim's transaction and a theft call can be a single block.
- No special privilege or setup is required to trigger or exploit the issue.

---

### Recommendation

Add a `msg.value == 0` guard at the top of every swap and liquidity entry-point that does not intentionally accept native ETH:

```solidity
// In exactInputSingle, exactInput, exactOutputSingle, exactOutput,
// addLiquidityExactShares, addLiquidityWeighted:
require(msg.value == 0, "Router: unexpected ETH");
```

Alternatively, introduce a non-`payable` variant for pure ERC-20 paths and reserve `payable` only for functions that explicitly wrap ETH (e.g., a future `exactInputSingleWithETH`).

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

// Assume:
//   router  = MetricOmmSimpleRouter (deployed)
//   pool    = a valid MetricOmm pool for USDC/DAI (neither is WETH)
//   victim  = an EOA that mistakenly sends 1 ETH with a USDC→DAI swap
//   attacker = any EOA

// Step 1 – victim calls exactInputSingle with 1 ETH attached
router.exactInputSingle{value: 1 ether}(
    IMetricOmmSimpleRouter.ExactInputSingleParams({
        pool:            address(pool),
        tokenIn:         USDC,          // not WETH
        tokenOut:        DAI,
        zeroForOne:      true,
        amountIn:        1_000e6,
        amountOutMinimum: 990e18,
        recipient:       victim,
        deadline:        block.timestamp + 60,
        priceLimitX64:   0,
        extensionData:   ""
    })
);
// Swap succeeds. 1 ETH is now silently held by the router.
// pay() called safeTransferFrom(USDC, victim, pool, 1000e6) — ETH untouched.

// Step 2 – attacker (or MEV bot) calls refundETH in the same or next block
router.refundETH();   // attacker receives 1 ETH; victim has no recourse
```

### Citations

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

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L88-116)
```text
  function addLiquidityWeighted(
    address pool,
    address owner,
    uint80 salt,
    LiquidityDelta calldata weightDeltas,
    uint256 maxAmountToken0,
    uint256 maxAmountToken1,
    int8 minimalCurBin,
    uint104 minimalPosition,
    int8 maximalCurBin,
    uint104 maximalPosition,
    bytes calldata extensionData
  ) external payable override returns (uint256 amount0Added, uint256 amount1Added) {
    _validateOwner(owner);
    _validateDeltas(weightDeltas);
    _validatePositiveWeights(weightDeltas);
    _validateBinAndBinPosition(pool, minimalCurBin, minimalPosition, maximalCurBin, maximalPosition);

    try IMetricOmmPoolActions(pool)
      .addLiquidity(owner, salt, weightDeltas, abi.encode(KIND_PROBE), extensionData) returns (
      uint256, uint256
    ) {
      revert WeightedProbeInconclusive();
    } catch (bytes memory reason) {
      (uint256 need0, uint256 need1) = _decodeLiquidityProbeOrBubble(reason);
      LiquidityDelta memory scaled = _scaleWeightsToShares(weightDeltas, maxAmountToken0, maxAmountToken1, need0, need1);
      return _addLiquidity(pool, owner, salt, scaled, msg.sender, maxAmountToken0, maxAmountToken1, extensionData);
    }
  }
```

**File:** metric-periphery/contracts/interfaces/IMetricOmmSimpleRouter.sol (L11-11)
```text
/// @dev Scope: ERC-20 routes only. No native ETH, WETH wrap/unwrap, on-chain quotes, sweep, or refund helpers.
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
