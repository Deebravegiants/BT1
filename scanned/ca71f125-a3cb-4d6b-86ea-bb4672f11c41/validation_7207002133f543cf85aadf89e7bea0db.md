### Title
`DepositAllowlistExtension` Checks `owner` Instead of `sender`, Allowing Any Unprivileged Caller to Bypass the Deposit Allowlist — (`metric-periphery/contracts/extensions/DepositAllowlistExtension.sol`)

---

### Summary

`DepositAllowlistExtension.beforeAddLiquidity` silently discards the `sender` argument (the actual depositor) and gates only on `owner` (the LP-position recipient). Because `owner` is a free caller-supplied parameter in `MetricOmmPool.addLiquidity`, any non-whitelisted address can bypass the allowlist by nominating any whitelisted address as `owner`.

---

### Finding Description

`MetricOmmPool.addLiquidity` accepts a caller-supplied `owner` and forwards both `msg.sender` (the real depositor) and `owner` to the extension hook:

```solidity
// MetricOmmPool.sol
function addLiquidity(
    address owner,          // ← caller-supplied, not validated against msg.sender
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
) external nonReentrant(PoolActions.ADD_LIQUIDITY) ... {
    ...
    _beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
```

`ExtensionCalling._beforeAddLiquidity` encodes both arguments and calls the extension:

```solidity
// ExtensionCalling.sol
abi.encodeCall(IMetricOmmExtensions.beforeAddLiquidity, (sender, owner, salt, deltas, extensionData))
```

`DepositAllowlistExtension.beforeAddLiquidity` then **discards `sender`** (unnamed first parameter) and checks only `owner`:

```solidity
// DepositAllowlistExtension.sol
function beforeAddLiquidity(address, address owner, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][owner]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
}
```

The sibling `SwapAllowlistExtension.beforeSwap` correctly checks `sender`:

```solidity
// SwapAllowlistExtension.sol
function beforeSwap(address sender, address, bool, int128, uint128, uint256, uint128, uint128, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllSwappers[msg.sender] && !allowedSwapper[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToSwap();
    }
```

The asymmetry is the root cause. The deposit allowlist checks the wrong identity.

The existing unit test `test_revertsWhenDepositorNotAllowed` passes `address(0)` as `sender` and `depositor` as `owner`, confirming the live check is on `owner`, not `sender`:

```solidity
// DepositAllowlistSubExtension.t.sol
extension.beforeAddLiquidity(address(0), depositor, 0, emptyDelta, "");
```

---

### Impact Explanation

The `DepositAllowlistExtension` is completely ineffective as an access-control gate. Any non-whitelisted address can:

1. Observe any whitelisted address `alice` (e.g., from past `AllowedToDepositSet` events).
2. Call `pool.addLiquidity(owner = alice, ...)` directly.
3. The extension check passes (`allowedDepositor[pool][alice] == true`).
4. The pool mints LP shares into Alice's position key.
5. The pool issues a callback to the actual caller (Bob) to pay the tokens.
6. Bob pays; the deposit succeeds.

Bob has deposited into the pool without being on the allowlist. The LP position is credited to Alice, but Bob controls the token flow and can manipulate pool bin state (token balances, `curPosInBin`, `curBinIdx`) without authorization. The pool admin's intent to restrict who can interact with pool liquidity is fully defeated — an admin-boundary break via an unprivileged path.

---

### Likelihood Explanation

Exploitation requires no special privileges. Any address can call `addLiquidity` directly on the pool with a known whitelisted `owner`. Whitelisted addresses are discoverable on-chain from `AllowedToDepositSet` events. The bypass is trivial and unconditional.

---

### Recommendation

Check `sender` (the actual depositor) instead of `owner` (the LP-position recipient), mirroring the correct pattern in `SwapAllowlistExtension`:

```solidity
// DepositAllowlistExtension.sol — fixed
function beforeAddLiquidity(address sender, address, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    return IMetricOmmExtensions.beforeAddLiquidity.selector;
}
```

If the intended design is to gate on the LP-position owner (e.g., to restrict who may hold positions), the parameter name and NatSpec must be updated to reflect that intent, and the `addLiquidity` caller must be separately validated.

---

### Proof of Concept

```
Setup:
  pool admin deploys pool with DepositAllowlistExtension
  pool admin calls: extension.setAllowedToDeposit(pool, alice, true)
  bob is NOT on the allowlist

Attack:
  bob calls pool.addLiquidity(
      owner        = alice,   // whitelisted address — passes the check
      salt         = 0,
      deltas       = <any valid delta>,
      callbackData = <bob's payment data>,
      extensionData = ""
  )

Extension check:
  allowedDepositor[pool][alice] == true  →  no revert

Result:
  LP shares minted to alice's position key
  pool calls metricOmmModifyLiquidityCallback on bob
  bob pays tokens
  bob has successfully deposited into an allowlisted pool without being on the allowlist
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** metric-periphery/test/extensions/DepositAllowlistSubExtension.t.sol (L27-41)
```text
  function test_revertsWhenDepositorNotAllowed() public {
    vm.prank(address(pool));
    vm.expectRevert(IMetricOmmPoolActions.NotAllowedToDeposit.selector);
    LiquidityDelta memory emptyDelta = LiquidityDelta({binIdxs: new int256[](0), shares: new uint256[](0)});
    extension.beforeAddLiquidity(address(0), depositor, 0, emptyDelta, "");
  }

  function test_passesWhenDepositorAllowed() public {
    vm.prank(admin);
    extension.setAllowedToDeposit(address(pool), depositor, true);

    vm.prank(address(pool));
    LiquidityDelta memory emptyDelta = LiquidityDelta({binIdxs: new int256[](0), shares: new uint256[](0)});
    extension.beforeAddLiquidity(address(0), depositor, 0, emptyDelta, "");
  }
```
