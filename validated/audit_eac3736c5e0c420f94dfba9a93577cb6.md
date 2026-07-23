Audit Report

## Title
`DepositAllowlistExtension.beforeAddLiquidity()` Silently Discards `sender`, Allowing Any Address to Bypass the Deposit Allowlist — (`metric-periphery/contracts/extensions/DepositAllowlistExtension.sol`)

## Summary
`DepositAllowlistExtension.beforeAddLiquidity` receives `sender` (the actual `addLiquidity` caller) as its first argument but leaves it unnamed and never validates it. Only `owner` (the position recipient, caller-supplied) is checked against the allowlist. Any address can therefore deposit into a permissioned pool by specifying an allowlisted address as `owner`, fully bypassing the pool admin's access boundary.

## Finding Description
`MetricOmmPool.addLiquidity` passes `msg.sender` as `sender` and the caller-supplied `owner` as separate arguments: [1](#0-0) 

`ExtensionCalling._beforeAddLiquidity` faithfully forwards both to the extension via `abi.encodeCall`: [2](#0-1) 

Inside `DepositAllowlistExtension.beforeAddLiquidity`, the first parameter (`sender`) is unnamed and silently discarded. The guard only checks `owner`: [3](#0-2) 

`msg.sender` inside the extension is the pool address (the caller of the extension), so `allowedDepositor[pool][owner]` is evaluated — never `allowedDepositor[pool][sender]`. Any unpermissioned address Alice can call `pool.addLiquidity(Bob, salt, deltas, ...)` where Bob is allowlisted; the extension evaluates `allowedDepositor[pool][Bob] == true` and does not revert. Alice's callback pays tokens into the pool, and `_positionBinShares` is credited to Bob's key.

The `removeLiquidity` guard (`msg.sender != owner`) means only Bob can withdraw, so Alice forfeits her tokens — but the allowlist invariant is broken: an unauthorized address has altered pool state (`binTotals`, `_binStates`, `_positionBinShares`) that the admin intended to restrict. [4](#0-3) 

## Impact Explanation
The `DepositAllowlistExtension` is the pool admin's sole mechanism to enforce a permissioned deposit surface (KYC, regulatory compliance, partner-only pools). Bypassing it allows an unauthorized address to inject liquidity into a permissioned pool, mutating `binTotals`, `_binStates`, and `_positionBinShares` for an allowlisted owner without the admin's consent. This constitutes an admin-boundary break: the pool admin's explicit access restriction is rendered ineffective by any unprivileged caller who knows one allowlisted address.

## Likelihood Explanation
`addLiquidity` is a public, unpermissioned entry point with no factory or role check blocking the call. Allowlisted addresses are discoverable via the public `allowedDepositor` mapping or emitted `AllowedToDepositSet` events. The attacker forfeits deposited tokens (no withdrawal path), which limits economic motivation but does not prevent griefing or compliance bypass via collusion with the allowlisted `owner`. [5](#0-4) 

## Recommendation
Validate `sender` (the actual caller) instead of — or in addition to — `owner`:

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

If the intent is to restrict both who calls `addLiquidity` and who can own positions, both `sender` and `owner` should be validated.

## Proof of Concept
1. Deploy pool with `DepositAllowlistExtension`; `allowAllDepositors[pool] = false`.
2. Pool admin calls `setAllowedToDeposit(pool, Bob, true)` — Bob is allowlisted.
3. Alice (not allowlisted) calls `pool.addLiquidity(Bob, salt, deltas, callbackData, extensionData)`.
4. Pool calls `_beforeAddLiquidity(Alice, Bob, ...)` → extension receives `(Alice, Bob, ...)`.
5. Extension evaluates `allowedDepositor[pool][Bob]` → `true` → no revert.
6. Alice's callback pays tokens; `_positionBinShares[keccak256(Bob, salt, bin)]` is credited.
7. Alice has deposited into a permissioned pool without being on the allowlist. The admin's access boundary is bypassed. [3](#0-2)

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

**File:** metric-periphery/contracts/extensions/DepositAllowlistExtension.sol (L13-14)
```text
  mapping(address pool => mapping(address depositor => bool)) public allowedDepositor;
  mapping(address pool => bool) public allowAllDepositors;
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
