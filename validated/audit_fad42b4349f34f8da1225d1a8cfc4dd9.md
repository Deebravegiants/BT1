### Title
`DepositAllowlistExtension.beforeAddLiquidity` Checks `owner` Instead of `sender`, Allowing Un-Allowlisted Depositors to Bypass the Deposit Allowlist — (File: `metric-periphery/contracts/extensions/DepositAllowlistExtension.sol`)

---

### Summary

`DepositAllowlistExtension` is documented as gating `addLiquidity` by **depositor address**. However, its `beforeAddLiquidity` hook silently drops the `sender` parameter (the actual caller who provides tokens) and instead checks `owner` (the LP-share recipient). Because `addLiquidity` explicitly supports an operator pattern where `msg.sender ≠ owner`, any un-allowlisted address can bypass the deposit gate by supplying an allowlisted address as `owner`.

---

### Finding Description

`MetricOmmPool.addLiquidity` passes two distinct addresses to every extension hook:

```solidity
// MetricOmmPool.sol line 191
_beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
```

- `msg.sender` — the operator/depositor who triggers the call and pays tokens via the modify-liquidity callback.
- `owner` — the address that receives the LP-share position.

The interface makes this split explicit:

```solidity
// IMetricOmmExtensions.sol lines 14-20
function beforeAddLiquidity(
    address sender,   // ← actual depositor / token payer
    address owner,    // ← LP-share recipient
    ...
```

`DepositAllowlistExtension.beforeAddLiquidity` discards `sender` entirely (unnamed first parameter) and only checks `owner`:

```solidity
// DepositAllowlistExtension.sol lines 32-42
function beforeAddLiquidity(address, address owner, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][owner]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
}
```

`msg.sender` inside the extension is the **pool** (enforced by `onlyPool` in `BaseMetricExtension`), so the effective check is:

```
allowedDepositor[pool][owner]
```

The actual depositor (`sender`) is never validated.

Compare with `SwapAllowlistExtension.beforeSwap`, which correctly checks `sender` (the swapper) and ignores the unnamed `recipient`:

```solidity
// SwapAllowlistExtension.sol lines 31-41
function beforeSwap(address sender, address, ...)
{
    if (!allowAllSwappers[msg.sender] && !allowedSwapper[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToSwap();
    }
    ...
}
```

The asymmetry is clear: the swap extension correctly gates the caller; the deposit extension gates the wrong address.

---

### Impact Explanation

**Severity: Medium**

An un-allowlisted address can bypass the deposit allowlist entirely:

1. Attacker identifies any allowlisted `owner` address (e.g., from on-chain `AllowedToDepositSet` events).
2. Attacker calls `pool.addLiquidity(allowedOwner, salt, deltas, callbackData, extensionData)`.
3. `beforeAddLiquidity` receives `sender = attacker` (ignored) and `owner = allowedOwner` (allowlisted → passes).
4. Attacker's callback pays the tokens; LP shares are credited to `allowedOwner`.

The pool admin's intent to restrict which addresses can inject liquidity into a permissioned pool is completely defeated. Un-allowlisted parties can alter pool composition, affect LP returns, and participate in pools explicitly configured to exclude them. The `NotAllowedToDeposit` guard is rendered meaningless for any caller who knows an allowlisted owner address.

---

### Likelihood Explanation

**Likelihood: High**

- `addLiquidity` explicitly documents and supports `msg.sender ≠ owner` (operator pattern); no extra setup is needed.
- Allowlisted owner addresses are discoverable from `AllowedToDepositSet` events emitted by `setAllowedToDeposit`.
- The bypass requires zero privileges and a single transaction.

---

### Recommendation

Replace the unnamed first parameter with `sender` and check it instead of `owner`, mirroring the correct pattern in `SwapAllowlistExtension`:

```solidity
function beforeAddLiquidity(address sender, address, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
}
```

If the intended design is to gate by `owner` (position recipient), the extension NatDoc must be corrected and the `setAllowedToDeposit` / `isAllowedToDeposit` API renamed to reflect that semantics. Either way, the current implementation contradicts the extension's own documentation.

---

### Proof of Concept

```
Setup:
  - Pool deployed with DepositAllowlistExtension
  - allowedDepositor[pool][alice] = true   (alice is allowlisted)
  - bob is NOT in the allowlist

Attack:
  1. bob calls pool.addLiquidity(
         owner        = alice,   // allowlisted → check passes
         salt         = 0,
         deltas       = <valid bins/shares>,
         callbackData = <bob's callback pays tokens>,
         extensionData = ""
     )
  2. DepositAllowlistExtension.beforeAddLiquidity receives:
         sender (arg1) = bob   → IGNORED (unnamed)
         owner  (arg2) = alice → allowedDepositor[pool][alice] == true → PASSES
  3. LiquidityLib.addLiquidity credits shares to alice's position key.
  4. bob's callback transfers tokens to the pool.

Result: bob (un-allowlisted) successfully deposited into a restricted pool.
        The DepositAllowlistExtension provided zero protection against bob.
```

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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

**File:** metric-core/contracts/interfaces/extensions/IMetricOmmExtensions.sol (L14-20)
```text
  function beforeAddLiquidity(
    address sender,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata extensionData
  ) external returns (bytes4);
```

**File:** metric-periphery/contracts/extensions/SwapAllowlistExtension.sol (L31-41)
```text
  function beforeSwap(address sender, address, bool, int128, uint128, uint256, uint128, uint128, bytes calldata)
    external
    view
    override
    returns (bytes4)
  {
    if (!allowAllSwappers[msg.sender] && !allowedSwapper[msg.sender][sender]) {
      revert IMetricOmmPoolActions.NotAllowedToSwap();
    }
    return IMetricOmmExtensions.beforeSwap.selector;
  }
```
