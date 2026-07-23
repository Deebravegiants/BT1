Audit Report

## Title
`DepositAllowlistExtension.beforeAddLiquidity` Checks `owner` Instead of `sender`, Allowing Un-Allowlisted Depositors to Bypass the Deposit Allowlist — (File: `metric-periphery/contracts/extensions/DepositAllowlistExtension.sol`)

## Summary
`DepositAllowlistExtension` is documented as gating `addLiquidity` by depositor address, but its `beforeAddLiquidity` hook silently discards the `sender` parameter (the actual caller who pays tokens) and checks only `owner` (the LP-share recipient). Because `MetricOmmPool.addLiquidity` explicitly supports an operator pattern where `msg.sender ≠ owner`, any un-allowlisted address can bypass the deposit gate by supplying an allowlisted address as `owner`.

## Finding Description

`MetricOmmPool.addLiquidity` passes `msg.sender` as `sender` and the caller-supplied `owner` as two distinct addresses to every extension hook: [1](#0-0) 

`ExtensionCalling._beforeAddLiquidity` faithfully forwards both addresses: [2](#0-1) 

The interface makes the split explicit — `sender` is the actual depositor/token payer, `owner` is the LP-share recipient: [3](#0-2) 

`DepositAllowlistExtension.beforeAddLiquidity` discards `sender` (unnamed first parameter) and checks only `owner`: [4](#0-3) 

Inside the extension, `msg.sender` is the calling pool (enforced by the `onlyPool` modifier inherited from `BaseMetricExtension`): [5](#0-4) 

So the effective check is `allowedDepositor[pool][owner]` — the actual depositor (`sender`) is never validated. By contrast, `SwapAllowlistExtension.beforeSwap` correctly checks `sender` (the swapper) and ignores the unnamed `recipient`: [6](#0-5) 

**Exploit path:**
1. Attacker identifies any allowlisted `owner` address from on-chain `AllowedToDepositSet` events.
2. Attacker calls `pool.addLiquidity(allowedOwner, salt, deltas, callbackData, extensionData)`.
3. `beforeAddLiquidity` receives `sender = attacker` (ignored) and `owner = allowedOwner` (allowlisted → passes).
4. Attacker's callback pays the tokens; LP shares are credited to `allowedOwner`.
5. The `NotAllowedToDeposit` guard is never triggered despite the attacker being un-allowlisted.

No existing guard prevents this: `removeLiquidity` does enforce `msg.sender == owner`, but `addLiquidity` has no such check, explicitly permitting the operator pattern. [7](#0-6) 

## Impact Explanation
The pool admin's intent to restrict which addresses can inject liquidity into a permissioned pool is completely defeated. Un-allowlisted parties can alter pool composition, affect LP returns, and participate in pools explicitly configured to exclude them. The `NotAllowedToDeposit` guard is rendered meaningless for any caller who knows an allowlisted owner address. This constitutes broken core pool functionality (deposit allowlist) causing unauthorized pool participation — a Medium severity impact under Sherlock thresholds.

## Likelihood Explanation
The bypass requires zero privileges and a single transaction. The operator pattern (`msg.sender ≠ owner`) is explicitly supported and documented in `addLiquidity`. Allowlisted owner addresses are discoverable from `AllowedToDepositSet` events emitted by `setAllowedToDeposit`. No special setup or collusion is required.

## Recommendation
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

## Proof of Concept
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

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L191-191)
```text
    _beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
```

**File:** metric-core/contracts/MetricOmmPool.sol (L199-206)
```text
  function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    nonReentrant(PoolActions.REMOVE_LIQUIDITY)
    returns (uint256 amount0Removed, uint256 amount1Removed)
  {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    if (msg.sender != owner) revert NotPositionOwner();
```

**File:** metric-core/contracts/ExtensionCalling.sol (L88-98)
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

**File:** metric-periphery/contracts/extensions/base/BaseMetricExtension.sol (L19-24)
```text
  modifier onlyPool() {
    if (!IMetricOmmPoolFactory(FACTORY).isPool(msg.sender)) {
      revert OnlyPool(msg.sender, FACTORY);
    }
    _;
  }
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
