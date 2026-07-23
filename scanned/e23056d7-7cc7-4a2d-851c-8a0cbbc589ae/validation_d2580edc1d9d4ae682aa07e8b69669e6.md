### Title
`DepositAllowlistExtension.beforeAddLiquidity()` Ignores `sender`, Allowing Unauthorized Depositors to Bypass the Allowlist — (`metric-periphery/contracts/extensions/DepositAllowlistExtension.sol`)

---

### Summary

`DepositAllowlistExtension` is designed to gate `addLiquidity` by depositor address. Its `beforeAddLiquidity` hook receives both `sender` (the actual caller of `addLiquidity`) and `owner` (the position owner), but silently discards `sender` and only validates `owner`. Any address not on the allowlist can bypass the restriction by specifying an allowlisted address as `owner`.

---

### Finding Description

`MetricOmmPool.addLiquidity` passes `msg.sender` as `sender` and the caller-supplied `owner` as separate arguments to the extension: [1](#0-0) 

`ExtensionCalling._beforeAddLiquidity` forwards both to the extension: [2](#0-1) 

Inside `DepositAllowlistExtension.beforeAddLiquidity`, the first parameter (`sender`) is unnamed and discarded. Only `owner` is checked: [3](#0-2) 

Because `sender` is never validated, any address can call `pool.addLiquidity(allowlistedOwner, salt, deltas, ...)` and the extension will approve the call as long as `owner` is on the allowlist — regardless of who `sender` is.

This is the direct analog of the KUMA finding: `KUMABondToken.approve()` checked `msg.sender` and `to` but not the token owner; here `beforeAddLiquidity` checks `owner` but not `sender` (the actual depositor).

---

### Impact Explanation

The `DepositAllowlistExtension` is the pool admin's mechanism to enforce a permissioned deposit surface (e.g., KYC, regulatory compliance, or partner-only pools). Bypassing it allows an unauthorized address to:

1. **Inject liquidity into a permissioned pool** — the unauthorized `sender` pays tokens via the `metricOmmModifyLiquidityCallback`, affecting `binTotals`, `_binStates`, and `_positionBinShares` for the allowlisted `owner`.
2. **Circumvent the admin-set access boundary** — the pool admin's explicit restriction is rendered ineffective by any caller who knows an allowlisted address.

The tokens paid by the unauthorized depositor are locked in the position owned by `owner` (only `owner` can call `removeLiquidity` per the `msg.sender != owner` guard), so the attacker forfeits their tokens. However, the allowlist invariant is broken: unauthorized parties participate in pool state changes that the admin intended to restrict. [4](#0-3) 

---

### Likelihood Explanation

- `addLiquidity` is a public, unpermissioned entry point — no factory or role check blocks the call.
- The attacker only needs to know one allowlisted address (publicly discoverable via `allowedDepositor` mapping or emitted events).
- The attacker loses their deposited tokens (they cannot withdraw), which limits economic motivation but does not prevent griefing or compliance bypass via collusion with the `owner`.

---

### Recommendation

Check `sender` (the actual caller) instead of — or in addition to — `owner`:

```solidity
// DepositAllowlistExtension.sol
function beforeAddLiquidity(address sender, address owner, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    // Check the actual depositor (sender), not just the position owner.
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
}
```

If the intent is to restrict both who can call `addLiquidity` and who can own positions, both `sender` and `owner` should be validated.

---

### Proof of Concept

1. Pool is deployed with `DepositAllowlistExtension`; `allowAllDepositors[pool] = false`.
2. Pool admin calls `setAllowedToDeposit(pool, Bob, true)` — Bob is allowlisted.
3. Alice is **not** in `allowedDepositor[pool]`.
4. Alice calls `pool.addLiquidity(Bob, salt, deltas, callbackData, extensionData)` directly.
5. `_beforeAddLiquidity(msg.sender=Alice, owner=Bob, ...)` is forwarded to the extension.
6. Extension evaluates `allowedDepositor[pool][Bob]` → `true` → no revert.
7. Alice's callback pays tokens into the pool; `_positionBinShares[keccak256(Bob, salt, bin)]` is credited.
8. Alice has deposited into a permissioned pool without being on the allowlist. The pool admin's access boundary is bypassed. [3](#0-2) [5](#0-4)

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

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L70-72)
```text
          // safe because -128 <= LOWEST_BIN <= HIGHEST_BIN <= 127 (enforced by factory)
          // forge-lint: disable-next-line(unsafe-typecast)
          bytes32 posKey = _positionBinKey(owner, salt, int8(binIdx));
```
