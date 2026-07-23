The code confirms all three cited locations exactly as described. Let me verify the complete call chain and impact before rendering a verdict.

**Confirmed code facts:**

1. `MetricOmmPool.addLiquidity` passes `msg.sender` as `sender` and the caller-supplied `owner` as separate args: [1](#0-0) 

2. `ExtensionCalling._beforeAddLiquidity` forwards both to the extension: [2](#0-1) 

3. `DepositAllowlistExtension.beforeAddLiquidity` silently discards the first parameter (`sender`) and only validates `owner`: [3](#0-2) 

4. `addLiquidity` has no `msg.sender == owner` guard (only `removeLiquidity` does): [4](#0-3) 

All code facts are verified. The exploit path is real and reachable by any unprivileged caller.

---

Audit Report

## Title
`DepositAllowlistExtension.beforeAddLiquidity()` Validates `owner` Instead of `sender`, Allowing Any Address to Bypass the Deposit Allowlist — (`metric-periphery/contracts/extensions/DepositAllowlistExtension.sol`)

## Summary
`DepositAllowlistExtension` is the pool admin's mechanism to enforce a permissioned deposit surface. Its `beforeAddLiquidity` hook receives `sender` (the actual `msg.sender` of `addLiquidity`) and `owner` (the position owner supplied by the caller), but silently discards `sender` and only validates `owner` against `allowedDepositor`. Because `addLiquidity` imposes no `msg.sender == owner` constraint, any address can call `pool.addLiquidity(allowlistedOwner, ...)` and the extension will approve the call, rendering the allowlist ineffective.

## Finding Description
`MetricOmmPool.addLiquidity` passes `msg.sender` as `sender` and the caller-supplied `owner` as separate arguments to `_beforeAddLiquidity` (line 191), which forwards both via `abi.encodeCall` to the extension (ExtensionCalling.sol lines 95–98). Inside `DepositAllowlistExtension.beforeAddLiquidity`, the first parameter is unnamed and discarded; only `owner` is checked: `allowedDepositor[msg.sender][owner]` (line 38). Since `addLiquidity` has no `msg.sender == owner` guard (that guard exists only in `removeLiquidity` at line 206), an unauthorized caller Alice can invoke `pool.addLiquidity(Bob, salt, deltas, ...)` where Bob is allowlisted. The extension evaluates `allowedDepositor[pool][Bob] == true` and does not revert. Alice's `metricOmmModifyLiquidityCallback` pays tokens into the pool, and `_positionBinShares` for Bob's position key is credited. The allowlist invariant is broken: Alice deposited into a permissioned pool without being on the allowlist.

## Impact Explanation
The `DepositAllowlistExtension` is the sole on-chain mechanism for the pool admin to enforce a permissioned deposit surface (KYC, regulatory compliance, partner-only pools). The bypass constitutes an admin-boundary break: an unprivileged path circumvents the pool admin's explicit access restriction. Unauthorized parties can alter `binTotals`, `_binStates`, and `_positionBinShares` for allowlisted owners without the admin's consent. The attacker forfeits their deposited tokens (only `owner` can call `removeLiquidity`), so there is no direct financial gain, but the compliance invariant the admin configured is fully nullified. Severity: Medium — broken access control with no direct fund loss to the protocol or LPs, but the admin-set access boundary is bypassed by any unprivileged caller.

## Likelihood Explanation
`addLiquidity` is a public, unpermissioned entry point with no factory or role check. The attacker only needs to know one allowlisted address, which is discoverable via the public `allowedDepositor` mapping or emitted `AllowedToDepositSet` events. The attacker loses their deposited tokens, limiting economic motivation, but griefing or collusion with the allowlisted `owner` (who receives the position shares) is a realistic scenario. The attack is trivially repeatable.

## Recommendation
Check `sender` (the actual caller) instead of — or in addition to — `owner`:

```solidity
function beforeAddLiquidity(address sender, address owner, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
}
```

If the intent is to restrict both who can call `addLiquidity` and who can own positions, both `sender` and `owner` should be validated.

## Proof of Concept
1. Pool is deployed with `DepositAllowlistExtension`; `allowAllDepositors[pool] = false`.
2. Pool admin calls `setAllowedToDeposit(pool, Bob, true)` — Bob is allowlisted.
3. Alice is **not** in `allowedDepositor[pool]`.
4. Alice calls `pool.addLiquidity(Bob, salt, deltas, callbackData, extensionData)`.
5. `_beforeAddLiquidity(msg.sender=Alice, owner=Bob, ...)` is forwarded to the extension.
6. Extension evaluates `allowedDepositor[pool][Bob]` → `true` → no revert.
7. Alice's callback pays tokens into the pool; `_positionBinShares[keccak256(Bob, salt, bin)]` is credited.
8. Alice has deposited into a permissioned pool without being on the allowlist. The pool admin's access boundary is bypassed.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L191-191)
```text
    _beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
```

**File:** metric-core/contracts/MetricOmmPool.sol (L206-206)
```text
    if (msg.sender != owner) revert NotPositionOwner();
```

**File:** metric-core/contracts/ExtensionCalling.sol (L95-98)
```text
    _callExtensionsInOrder(
      BEFORE_ADD_LIQUIDITY_ORDER,
      abi.encodeCall(IMetricOmmExtensions.beforeAddLiquidity, (sender, owner, salt, deltas, extensionData))
    );
```

**File:** metric-periphery/contracts/extensions/DepositAllowlistExtension.sol (L32-42)
```text
  function beforeAddLiquidity(address, address owner, uint80, LiquidityDelta calldata, bytes calldata)
    external
    view
    override
    returns (bytes4)
  {
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][owner]) {
      revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
  }
```
