### Title
`DepositAllowlistExtension` Checks `owner` Instead of `sender`, Allowing Unprivileged Allowlist Bypass — (File: `metric-periphery/contracts/extensions/DepositAllowlistExtension.sol`)

---

### Summary

`DepositAllowlistExtension.beforeAddLiquidity` silently drops the `sender` argument and gates on `owner` (the position beneficiary) instead. Any address that is not on the allowlist can bypass the restriction by calling `pool.addLiquidity(allowlisted_address, salt, …)` directly, paying the tokens themselves while crediting shares to the allowlisted address. The allowlist — the only admin-set access-control boundary on liquidity ingress — is therefore completely ineffective against an unprivileged caller.

---

### Finding Description

`MetricOmmPool.addLiquidity` deliberately separates the payer (`msg.sender`, who implements the callback) from the position owner (`owner`, whose share balance is credited): [1](#0-0) 

Before minting, the pool calls `_beforeAddLiquidity(msg.sender, owner, …)`, which forwards both `sender` and `owner` to every registered extension: [2](#0-1) 

`DepositAllowlistExtension.beforeAddLiquidity` receives `sender` as its first argument but **discards it** (the parameter is unnamed). It then checks `owner` against the allowlist: [3](#0-2) 

The mapping and the public setter are both named `allowedDepositor`, making the intent unambiguous — the allowlist is meant to gate the **depositor** (the caller), not the position owner: [4](#0-3) 

Because the check is on `owner` rather than `sender`, any caller can pass the gate by supplying an allowlisted address as `owner`. The `MetricOmmPoolLiquidityAdder` even documents and tests this operator pattern explicitly: [5](#0-4) 

---

### Impact Explanation

1. **Allowlist bypass (admin-boundary break):** The pool admin's intent to restrict which addresses may add liquidity is completely defeated. Any unprivileged address can call `pool.addLiquidity(allowlisted_victim, salt, …)` directly, pay the tokens through the callback, and have shares credited to the victim's position — all while the allowlist check silently passes.

2. **Griefing / forced position mutation:** Because `removeLiquidity` enforces `MinimalLiquidity` on partial exits, an attacker can add a dust amount of shares to a victim's existing position, making the victim unable to remove a specific share count without either exiting fully or keeping at least `minimalMintableLiquidity` shares: [6](#0-5) 

3. **Allowlist semantics are inverted:** Addresses on the allowlist have their positions open to arbitrary third-party deposits; addresses not on the allowlist cannot add liquidity even to their own positions. This is the opposite of the intended behavior.

---

### Likelihood Explanation

Exploitation requires only that an attacker deploy a minimal contract implementing `IMetricOmmModifyLiquidityCallback` and call `pool.addLiquidity` directly with any allowlisted address as `owner`. No privileged access, no special tokens, and no complex setup are needed. The `MetricOmmPoolLiquidityAdder` itself demonstrates the operator pattern is a supported and tested flow.

---

### Recommendation

Change the allowlist check to validate `sender` (the actual caller) rather than `owner` (the position beneficiary):

```solidity
// Before (buggy):
function beforeAddLiquidity(address, address owner, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][owner]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    ...
}

// After (fixed):
function beforeAddLiquidity(address sender, address, uint80, LiquidityDelta calldata, bytes calldata)
    external view override returns (bytes4)
{
    if (!allowAllDepositors[msg.sender] && !allowedDepositor[msg.sender][sender]) {
        revert IMetricOmmPoolActions.NotAllowedToDeposit();
    }
    ...
}
```

---

### Proof of Concept

```
Setup:
  - Pool deployed with DepositAllowlistExtension as beforeAddLiquidity hook.
  - Admin calls setAllowedToDeposit(pool, alice, true).
  - Bob (attacker) is NOT on the allowlist.

Attack:
  1. Bob deploys AttackerContract implementing IMetricOmmModifyLiquidityCallback.
  2. AttackerContract calls pool.addLiquidity(alice, salt, deltas, callbackData, "").
  3. Pool calls _beforeAddLiquidity(address(AttackerContract), alice, …).
  4. DepositAllowlistExtension checks allowedDepositor[pool][alice] → true → passes.
  5. Pool mints shares to alice's position.
  6. Pool calls AttackerContract.metricOmmModifyLiquidityCallback(…).
  7. AttackerContract pays the required tokens from Bob's balance.

Result:
  - Bob (not on allowlist) successfully added liquidity, bypassing the allowlist.
  - Alice's position is modified without her consent.
  - If alice had 5000 shares and Bob added 1 share, alice can no longer
    remove exactly 5000 shares (leaving 1 < minimalMintableLiquidity),
    forcing a full exit or acceptance of the unwanted position.
```

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

**File:** metric-periphery/contracts/extensions/DepositAllowlistExtension.sol (L13-19)
```text
  mapping(address pool => mapping(address depositor => bool)) public allowedDepositor;
  mapping(address pool => bool) public allowAllDepositors;

  constructor(address factory_) BaseMetricExtension(factory_) {}

  function setAllowedToDeposit(address pool_, address depositor, bool allowed) external onlyPoolAdmin(pool_) {
    allowedDepositor[pool_][depositor] = allowed;
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

**File:** metric-periphery/test/MetricOmmPoolLiquidityAdder.t.sol (L211-220)
```text
  function test_exactShares_canAddOnBehalfOfAnotherOwner() public {
    LiquidityDelta memory d = _deltaAbovePrice(4, 10_000);
    address bob = makeAddr("bob");

    vm.prank(alice);
    helper.addLiquidityExactShares(address(pool), bob, 1, d, type(uint256).max, type(uint256).max, "");

    uint256 bobShares = stateView.positionBinShares(address(pool), bob, 1, int8(4));
    assertGt(bobShares, 0);
  }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L196-202)
```text
          if (userShares < sharesToRemove) {
            revert IMetricOmmPoolActions.InsufficientLiquidity(sharesToRemove, userShares);
          }
          uint256 newUserShares = userShares - sharesToRemove;
          if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }
```
