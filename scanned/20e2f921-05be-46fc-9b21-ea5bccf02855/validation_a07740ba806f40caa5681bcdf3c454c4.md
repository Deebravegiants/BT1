### Title
`DepositAllowlistExtension` Checks `owner` Instead of `sender`, Allowing Any Unprivileged Caller to Bypass the Deposit Allowlist — (`metric-periphery/contracts/extensions/DepositAllowlistExtension.sol`)

---

### Summary

`DepositAllowlistExtension.beforeAddLiquidity` is documented as gating `addLiquidity` **by depositor address**, but its implementation checks the `owner` argument (the position recipient) rather than the `sender` argument (the actual depositor/payer). Because `MetricOmmPool.addLiquidity` accepts an arbitrary `owner` address from any caller, any unprivileged address can bypass the allowlist by supplying an allowlisted address as `owner` while acting as the real depositor.

---

### Finding Description

`MetricOmmPool.addLiquidity` is a permissionless external function. It passes both `msg.sender` (as `sender`) and the caller-supplied `owner` to `_beforeAddLiquidity`, which forwards them to every registered extension: [1](#0-0) 

`ExtensionCalling._beforeAddLiquidity` encodes both arguments and calls each extension: [2](#0-1) 

`DepositAllowlistExtension.beforeAddLiquidity` receives `sender` as its first (unnamed, discarded) argument and `owner` as its second. The guard only inspects `owner`: [3](#0-2) 

The NatSpec on the contract states it "Gates `addLiquidity` by depositor address, per pool," but the depositor is `sender` — the address that will pay tokens through the modify-liquidity callback — not `owner`. The `owner` is merely the address that receives the LP position.

Because `owner` is a free parameter supplied by the caller, any address can call `pool.addLiquidity(allowlisted_address, salt, deltas, callbackData, "")` directly. The extension evaluates `allowedDepositor[pool][allowlisted_address]` → `true` and returns the success selector. The unauthorized caller then settles the token payment through its own `metricOmmModifyLiquidityCallback` implementation, and the LP shares are credited to `allowlisted_address`.

---

### Impact Explanation

- The `DepositAllowlistExtension` access control is fully defeated: any address can deposit into a pool that the admin intended to restrict, simply by nominating an allowlisted address as `owner`.
- The pool admin's boundary is broken by an unprivileged path — a direct call to `pool.addLiquidity` with a crafted `owner` argument, requiring no special role or privilege.
- The unauthorized depositor can manipulate per-bin balances (`binState.token0BalanceScaled`, `binState.token1BalanceScaled`) and `binTotals` in ways the pool admin did not authorize, affecting the composition of liquidity available to swappers.
- The allowlisted `owner` receives an LP position they did not request and cannot prevent, constituting griefing of their position accounting.

---

### Likelihood Explanation

- Likelihood is **high**: the bypass requires only a direct call to `pool.addLiquidity` with `owner` set to any address already in the allowlist. No privileged access, no special token, no complex setup is needed.
- The pool address and allowlisted addresses are public on-chain. Any observer can identify them and execute the bypass immediately.
- The `MetricOmmPool` contract is permissionless; there is no factory-level guard preventing direct calls.

---

### Recommendation

Change `DepositAllowlistExtension.beforeAddLiquidity` to check `sender` (the actual depositor/payer) rather than `owner` (the position recipient):

```solidity
// Before (checks owner — wrong)
function beforeAddLiquidity(address, address owner, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][owner]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
}

// After (checks sender — correct)
function beforeAddLiquidity(address sender, address, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
}
```

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

// Setup: pool has DepositAllowlistExtension configured.
// Admin has allowlisted `alice` but NOT `attacker`.

contract AttackerCallback is IMetricOmmModifyLiquidityCallback {
    IERC20 token0;
    IERC20 token1;

    constructor(address _token0, address _token1) {
        token0 = IERC20(_token0);
        token1 = IERC20(_token1);
    }

    function metricOmmModifyLiquidityCallback(
        uint256 amount0Delta,
        uint256 amount1Delta,
        bytes calldata
    ) external override {
        // Attacker pays tokens from their own balance
        if (amount0Delta > 0) token0.transfer(msg.sender, amount0Delta);
        if (amount1Delta > 0) token1.transfer(msg.sender, amount1Delta);
    }

    function exploit(address pool, address alice, uint80 salt, LiquidityDelta calldata deltas) external {
        // sender = address(this) [NOT allowlisted]
        // owner  = alice          [IS allowlisted]
        // Extension checks owner (alice) → passes.
        // Attacker pays; alice receives LP shares without consent.
        IMetricOmmPoolActions(pool).addLiquidity(alice, salt, deltas, "", "");
    }
}
```

**Trace:**
1. `AttackerCallback.exploit` calls `pool.addLiquidity(alice, salt, deltas, "", "")`.
2. Pool calls `_beforeAddLiquidity(address(attackerCallback), alice, ...)`.
3. Extension receives `sender = attackerCallback` (discarded), `owner = alice`.
4. Check: `allowedDepositor[pool][alice]` → `true` → no revert.
5. `LiquidityLib.addLiquidity` credits shares to `alice`, calls `metricOmmModifyLiquidityCallback` on `attackerCallback`.
6. Attacker pays tokens; `alice`'s position is modified without her consent; the allowlist is bypassed. [3](#0-2) [4](#0-3) [2](#0-1)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L182-196)
```text
  function addLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
  ) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (uint256 amount0Added, uint256 amount1Added) {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    _beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Added, amount1Added) = LiquidityLib.addLiquidity(
      _liquidityContext(), owner, salt, deltas, callbackData, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterAddLiquidity(msg.sender, owner, salt, deltas, amount0Added, amount1Added, extensionData);
  }
```

**File:** metric-core/contracts/ExtensionCalling.sol (L88-99)
```text
  function _beforeAddLiquidity(
    address sender,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata extensionData
  ) internal {
    _callExtensionsInOrder(
      BEFORE_ADD_LIQUIDITY_ORDER,
      abi.encodeCall(IMetricOmmExtensions.beforeAddLiquidity, (sender, owner, salt, deltas, extensionData))
    );
  }
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
